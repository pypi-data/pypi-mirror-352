#!python3

"""
Lumeo Bulk Deployer

Lumeo Bulk Deployer uploads & queues media file deployments, or creates live stream deployments on a specific gateway. 
Learn more at https://docs.lumeo.com/docs/bulk-deployer

Arguments:
    Authentication Args:
        --app_id APP_ID       Application (aka Workspace) ID
        --token TOKEN         Access (aka API) Token.

    Source Files (one of pattern, file_list, csv_file, s3_bucket or tag is required):
        --pattern PATTERN     Glob pattern for files to upload
        --file_list FILE_LIST
                                Comma separated list of file URIs to queue
        --csv_file CSV_FILE   CSV file containing file_uri and corresponding camera_external_id or camera_id
        --s3_bucket S3_BUCKET
                                S3 bucket name to use as source for files
        --s3_access_key_id S3_ACCESS_KEY_ID
                                S3 Access key ID
        --s3_secret_access_key S3_SECRET_ACCESS_KEY
                                S3 secret access key
        --s3_region S3_REGION
                                S3 region if using AWS S3 bucket. Either s3_region or s3_endpoint_url must be specified.
        --s3_endpoint_url S3_ENDPOINT_URL
                                S3 endpoint URL. Either s3_region or s3_endpoint_url must be specified.
        --s3_prefix S3_PREFIX
                                S3 path prefix to filter files. Optional.
        --tag TAG             Tag to apply to uploaded files. Can be tag uuid, tag name or tag path (e.g. "tag1/tag2/tag3").If specified without pattern/file_list/csv_file/s3_bucket, will process
                                existing files with that tag.

    Associate Files with Virtual Camera (gets pipeline & deployment config from camera):
        --camera_id CAMERA_ID
                                Camera ID of an existing camera, to associate with the uploaded files
        --camera_external_id CAMERA_EXTERNAL_ID
                                Use your own unique camera id to find or create a virtual camera, and associate with the uploaded files

    Source Live Streams (gateway_id + one of stream_id, stream_urls, or stream_tag is required):
        --gateway_id GATEWAY_ID
                                Gateway ID to create (not queue) deployment for processing live streams.
        --stream_id STREAM_ID
                                Stream ID of an existing stream to create a deployment for processing live streams.
        --stream_urls STREAM_URLS
                                Comma separated list of RTSP or HLS stream URLs to create streams for processing.
        --stream_tag STREAM_TAG
                                Creates one deployment for each stream with the specified tag or applies tag to created streams when used with stream_urls. Can be tag uuid, tag name or tag path (e.g.
                                "tag1/tag2/tag3").

    Deployment Args (needed for Live Stream Deployments or when camera not specified for File deployments):
        --pipeline_id PIPELINE_ID
                                Pipeline ID to queue deployment for processing. Required if camera_id / camera_external_id not specified.
        --deployment_config DEPLOYMENT_CONFIG
                                String containing a Deployment config JSON object. Video source in the config will be overridden by source files specified in this script. Ignored if camera_id or
                                camera_external_id specified. Optional.

    General Args:
        --deployment_prefix DEPLOYMENT_PREFIX
                                Prefix to use for deployment name. Optional.
        --delete_processed DELETE_PROCESSED
                                Delete successfully processed files from the local folder after uploading
        --log_level LOG_LEVEL
                                Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        --batch_size BATCH_SIZE
                                Number of concurrent uploads to process at a time. Default 5.
        --queue_size          Print the current queue size
        --split_local_file_size SPLIT_LOCAL_FILE_SIZE
                                Split local files into chunks of this size before uploading. Default 250MB.
"""

import argparse
import asyncio
import boto3
import colorlog
import csv
import glob
import json
import logging
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

from lumeo.api import LumeoApiClient
from botocore.client import Config
from .deployer import LumeoDeployer

handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s %(levelname)-8s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red,bg_white',
        'CRITICAL': 'red,bg_white',
    },
))

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class BulkDeployer:
    def __init__(self, args=None, api_client=None):
        self._api_client = api_client
        self._queuing_lock = asyncio.Lock()
        self._start_time = time.time()
        if not args:
            self._parser = self._create_args_parser()
            self._args = self._parser.parse_args()
        else:
            self._args = args

    async def run(self):
        tasks = []
        chunk_files_to_delete = []

        if not self._validate_args(self._args):
            self._parser.print_usage()
            return

        if not self._api_client:
            self._api_client = LumeoApiClient(self._args.app_id, self._args.token)
            
        if self._args.clear_queue:
            await self._clear_queue(self._api_client)
            return

        if self._args.queue_size and not (self._args.pattern or self._args.file_list or self._args.csv_file or self._args.s3_bucket or self._args.tag):
            await self._print_queue_size(self._api_client)
            return

        if self._args.tag:
            # Create a tag if another file source is provided and the tag is not found.
            create_tag = (self._args.csv_file or self._args.file_list or self._args.pattern or self._args.s3_bucket)
            self._args.tag = await self._get_tag_id(self._args.tag, create_tag)
            
        if self._args.stream_tag:
            # Create a tag if another live stream source is provided and the tag is not found.
            create_tag = (self._args.stream_urls)
            self._args.stream_tag = await self._get_tag_id(self._args.stream_tag, create_tag)
            
        tasks, chunk_files_to_delete = await self._get_tasks()

        results = await self._process_tasks(tasks)

        self._log_results(results)

        # Delete all chunk files after processing
        for chunk_file in chunk_files_to_delete:
            try:
                os.remove(chunk_file)
            except Exception as e:
                logger.warning(f"Failed to delete chunk file {chunk_file} at cleanup: {e}")

        # Get the deployment queue for this app
        await self._print_queue_size(self._api_client)
        return

    def _create_args_parser(self):
        parser = argparse.ArgumentParser(description="""Lumeo Bulk Deployer uploads & queues media file deployments, \
                                                        or creates live stream deployments on a specific gateway. \
                                                        Learn more at https://docs.lumeo.com/docs/bulk-deployer """)

        required_group = parser.add_argument_group('Authentication Args')
        required_group.add_argument('--app_id', required=True, help='Application (aka Workspace) ID')
        required_group.add_argument('--token', required=True, help='Access (aka API) Token.')

        file_source_group = parser.add_argument_group('Source Files (one of pattern, file_list, csv_file, s3_bucket or tag is required)')
        file_source_group.add_argument('--pattern', help='Glob pattern for files to upload')
        file_source_group.add_argument('--file_list', help='Comma separated list of file URIs to queue')
        file_source_group.add_argument('--csv_file', help='CSV file containing file_uri and corresponding camera_external_id or camera_id')
        file_source_group.add_argument('--s3_bucket', help='S3 bucket name to use as source for files')
        file_source_group.add_argument('--s3_access_key_id', help='S3 Access key ID')
        file_source_group.add_argument('--s3_secret_access_key', help='S3 secret access key')
        file_source_group.add_argument('--s3_region', help='S3 region if using AWS S3 bucket. Either s3_region or s3_endpoint_url must be specified.')
        file_source_group.add_argument('--s3_endpoint_url', help='S3 endpoint URL. Either s3_region or s3_endpoint_url must be specified.')
        file_source_group.add_argument('--s3_prefix', help='S3 path prefix to filter files. Optional.')
        file_source_group.add_argument('--tag', help='Tag to apply to uploaded files. Can be tag uuid, tag name or tag path (e.g. "tag1/tag2/tag3").'
                                          'If specified without pattern/file_list/csv_file/s3_bucket, will process existing files with that tag.')

        camera_group = parser.add_argument_group('Associate Files with Virtual Camera (gets pipeline & deployment config from camera)')
        camera_group.add_argument('--camera_id', help='Camera ID of an existing camera, to associate with the uploaded files')
        camera_group.add_argument('--camera_external_id', help='Use your own unique camera id to find or create a virtual camera, and associate with the uploaded files')

        live_stream_group = parser.add_argument_group('Source Live Streams (gateway_id + one of stream_id, stream_urls, or stream_tag is required)')
        live_stream_group.add_argument('--gateway_id', help='Gateway ID to create (not queue) deployment for processing live streams.')
        live_stream_group.add_argument('--stream_id', help='Stream ID of an existing stream to create a deployment for processing live streams.')
        live_stream_group.add_argument('--stream_urls', help='Comma separated list of RTSP or HLS stream URLs to create streams for processing.')
        live_stream_group.add_argument('--stream_tag', help='Creates one deployment for each stream with the specified tag or applies tag to created streams '
                                                            'when used with stream_urls. '
                                                            'Can be tag uuid, tag name or tag path (e.g. "tag1/tag2/tag3").')

        pipeline_group = parser.add_argument_group('Deployment Args (needed for Live Stream Deployments or when camera not specified for File deployments)')
        pipeline_group.add_argument('--pipeline_id', help='Pipeline ID to queue deployment for processing. Required if camera_id / camera_external_id not specified.')
        pipeline_group.add_argument('--deployment_config', help='String containing a Deployment config JSON object. Video source in the config will be overridden by source files specified in this script. Ignored if camera_id or camera_external_id specified. Optional.')

        other_group = parser.add_argument_group('General Args')
        other_group.add_argument('--deployment_prefix', help='Prefix to use for deployment name. Optional.')
        other_group.add_argument('--delete_processed', help='Delete successfully processed files from the local folder after uploading')
        other_group.add_argument('--log_level', default='INFO', help='Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
        other_group.add_argument('--batch_size', type=int, default=5, help='Number of concurrent uploads to process at a time. Default 5.')
        other_group.add_argument('--queue_size', action='store_true', help='Print the current queue size')
        other_group.add_argument('--clear_queue', action='store_true', help='Clear the deployment queue')
        other_group.add_argument('--split_local_file_size', type=int, default=250*1024*1024, help='Split local files into chunks of this size before uploading. Default 250MB.')

        return parser

    def _validate_args(self, args):
        if len(vars(args)) <= 1:
            return False

        logger.setLevel(args.log_level.upper())

        if not args.queue_size and not args.clear_queue:
            if not args.gateway_id: 
                if not any([args.pattern, args.file_list, args.csv_file, args.s3_bucket, args.tag]):
                    logging.error("Please provide either a tag for already uploaded files, glob pattern, a file list, a csv file, or an S3 bucket.")
                    return False
                elif not (args.csv_file or any([args.camera_id, args.camera_external_id, args.pipeline_id])):
                    logging.error("Please provide either a camera_id or camera_external_id or pipeline_id if source isnt a csv file.")
                    return False
                elif args.s3_bucket and not all([args.access_key_id, args.secret_access_key]):
                    logging.error("Please provide AWS credentials when using an S3 bucket")
                    return False
                elif args.s3_bucket and not any([args.region, args.endpoint_url]):
                    print("Please provide AWS S3 region OR endpoint URL when using an S3 bucket")
                    return False
            else:
                if not any([args.stream_id, args.stream_urls, args.stream_tag]):
                    logging.error("Gateway ID provided. Please also provide either a stream_id, stream_urls, or stream_tag.")
                    return False
                elif not args.pipeline_id:
                    logging.error("Gateway ID provided. Please also provide a pipeline_id to create deployments for live streams.")
                    return False

        if args.deployment_config:
            try:
                args.deployment_config = json.loads(args.deployment_config)
            except json.JSONDecodeError:
                logging.error("Invalid deployment config JSON provided")
                return False
        else:
            args.deployment_config = {}

        return True
    
    async def _get_tasks(self):
        if not self._args.gateway_id:
            if self._args.csv_file:
                return await self._process_csv_file(self._args, self._api_client, self._queuing_lock)
            elif self._args.file_list:
                return await self._process_file_list(self._args, self._api_client, self._queuing_lock)
            elif self._args.pattern:
                return await self._process_glob_pattern(self._args, self._api_client, self._queuing_lock)
            elif self._args.s3_bucket:
                return await self._process_s3_bucket(self._args, self._api_client, self._queuing_lock)
            elif self._args.tag:
                return await self._process_existing_files_with_tag(self._args, self._api_client, self._queuing_lock)
        else:
            if self._args.stream_id:
                return await self._process_existing_live_stream(self._args, self._api_client, self._queuing_lock)
            elif self._args.stream_urls:
                return await self._process_live_stream_list(self._args, self._api_client, self._queuing_lock)
            elif self._args.stream_tag:
                return await self._process_existing_live_streams_with_tag(self._args, self._api_client, self._queuing_lock)
        return [], []        
    
    def _is_local_mp4_and_large(self, file_path, chunk_size):
        if not file_path.lower().endswith('.mp4'):
            return False
        try:
            size = os.path.getsize(file_path)
            return size > chunk_size
        except Exception:
            return False

    def _split_mp4_file(self, file_path, chunk_size):
        """
        Splits the mp4 file into chunks of approximately chunk_size bytes using ffmpeg.
        Returns a list of chunk file paths. If splitting fails, returns [].
        """
        try:
            logging.info(f"[{file_path}] Splitting into chunks of {chunk_size/1024/1024} MB.")
            # Get duration of the video
            cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', file_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                
                # Calculate target chunk duration
                duration = float(result.stdout.strip())
                size = os.path.getsize(file_path)                
                chunk_count = int(size // chunk_size) + (1 if size % chunk_size else 0)
                if chunk_count <= 1:
                    return [file_path]
                chunk_duration = duration / chunk_count
                
                # Prepare output pattern
                temp_dir = tempfile.mkdtemp(prefix="lumeo_chunks_")
                base = os.path.splitext(os.path.basename(file_path))[0]
                out_pattern = os.path.join(temp_dir, f"{base}_chunk_%03d.mp4")
                
                # ffmpeg split
                ffmpeg_cmd = [
                    'ffmpeg', '-i', file_path, '-c', 'copy', '-map', '0',
                    '-f', 'segment', '-segment_time', str(chunk_duration), '-reset_timestamps', '1', out_pattern
                ]
                result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if result.returncode == 0:
                    # List chunk files
                    chunk_files = sorted([str(p) for p in Path(temp_dir).glob(f"{base}_chunk_*.mp4")])
                    if chunk_files:
                        return chunk_files
                    else:
                        logger.error(f"[{file_path}] No chunk files produced by ffmpeg. Ensure ffmpeg is installed and in the PATH or specify a different split_local_file_size. Will skip file.")
                else:
                    logger.error(f"[{file_path}] File splitting using ffmpeg failed: {result.stderr}. Ensure ffmpeg is installed and in the PATH or specify a different split_local_file_size. Will skip file.")
            else:
                logger.error(f"[{file_path}] ffprobe failed: {result.stderr}. Ensure ffmpeg is installed and in the PATH or specify a different split_local_file_size. Will skip file.")
        
        except Exception as e:
            logger.error(f"[{file_path}] Exception during mp4 splitting: {e}. Ensure ffmpeg is installed and in the PATH or specify a different split_local_file_size. Will skip file.")
        
        return []

    def _create_upload_tasks_for_file(self, file_uri, args, api_client, queuing_lock, camera_external_id, camera_id, pipeline_id, deployment_config):
        chunk_size = args.split_local_file_size
        tasks = []
        chunk_files = [file_uri]
        chunk_files_to_delete = []
        if self._is_local_mp4_and_large(file_uri, chunk_size):
            chunk_files = self._split_mp4_file(file_uri, chunk_size)
            # Only mark for deletion if they are not the original file
            chunk_files_to_delete = [f for f in chunk_files if f != file_uri]
        for chunk_file in chunk_files:
            tasks.append(LumeoDeployer(api_client, queuing_lock, file_uri=chunk_file, tag_id=args.tag,
                                       camera_external_id=camera_external_id, camera_id=camera_id,
                                       pipeline_id=pipeline_id, deployment_config=deployment_config,
                                       deployment_prefix=args.deployment_prefix, 
                                       delete_processed_files=args.delete_processed).process())
        return tasks, chunk_files_to_delete

    async def _process_csv_file(self, args, api_client, queuing_lock):
        tasks = []
        all_chunks_to_delete = []
        with open(args.csv_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header
            for row in reader:
                file_uri = None
                camera_external_id = args.camera_external_id
                camera_id = args.camera_id
                pipeline_id = args.pipeline_id
                deployment_config = args.deployment_config
                file_uri = row[0].strip() if len(row[0].strip()) > 0 else None
                if file_uri and not file_uri.startswith('#'):
                    if len(row) > 1:
                        camera_external_id = row[1].strip() if len(row[1].strip()) > 0 else camera_external_id
                    if len(row) > 2:
                        camera_id = row[2].strip() if len(row[2].strip()) > 0 else camera_id
                    if len(row) > 3:
                        pipeline_id = row[3].strip() if len(row[3].strip()) > 0 else pipeline_id
                    if len(row) > 4:
                        deployment_config_str = row[4].strip() if len(row[4].strip()) > 0 else "{}"
                        try:
                            deployment_config_dict = json.loads(deployment_config_str)
                        except json.JSONDecodeError:
                            logging.error(f"Invalid deployment config JSON provided in row {reader.line_num} : {row}. Skipping.")
                            continue
                        deployment_config = deployment_config_dict

                    if not any([camera_external_id, camera_id, pipeline_id]):
                        logging.error(f"No camera_id, camera_external_id or pipeline_id provided in row {reader.line_num} : {row}. Skipping.")
                        continue

                    t, c = self._create_upload_tasks_for_file(
                        file_uri, args, api_client, queuing_lock, camera_external_id, camera_id, pipeline_id, deployment_config
                    )
                    tasks.extend(t)
                    all_chunks_to_delete.extend(c)
                else:
                    logging.error(f"Invalid file URI provided in CSV file row {reader.line_num}: {row}. Skipping.")
        return tasks, all_chunks_to_delete

    async def _process_file_list(self, args, api_client, queuing_lock):
        tasks = []
        all_chunks_to_delete = []
        for file_uri in args.file_list.split(','):
            t, c = self._create_upload_tasks_for_file(
                file_uri, args, api_client, queuing_lock, args.camera_external_id, args.camera_id, args.pipeline_id, args.deployment_config
            )
            tasks.extend(t)
            all_chunks_to_delete.extend(c)
        return tasks, all_chunks_to_delete

    async def _process_glob_pattern(self, args, api_client, queuing_lock):
        tasks = []
        all_chunks_to_delete = []
        for file_path in glob.glob(args.pattern):
            t, c = self._create_upload_tasks_for_file(
                file_path, args, api_client, queuing_lock, args.camera_external_id, args.camera_id, args.pipeline_id, args.deployment_config
            )
            tasks.extend(t)
            all_chunks_to_delete.extend(c)
        return tasks, all_chunks_to_delete

    async def _process_s3_bucket(self, args, api_client, queuing_lock):
        s3_file_list = await self._get_s3_file_list(args.bucket, args.access_key_id, args.secret_access_key, args.region, args.endpoint_url, args.prefix)
        tasks = []
        for signed_url in s3_file_list:
            tasks.append(LumeoDeployer(api_client, queuing_lock, file_uri=signed_url, tag_id=args.tag,
                                        camera_external_id=args.camera_external_id, camera_id=args.camera_id,
                                        pipeline_id=args.pipeline_id, deployment_config=args.deployment_config,
                                        deployment_prefix=args.deployment_prefix).process())
        return tasks

    async def _process_existing_files_with_tag(self, args, api_client, queuing_lock):
        tasks = []

        # Get all file streams with the specified tag ID
        logging.info(f"Getting existing file streams with tag {args.tag}")
        file_streams = await api_client.get_streams(args.tag, stream_type="file")
        for stream in file_streams:
            # Create a task for processing this file
            tasks.append(LumeoDeployer(api_client, queuing_lock, stream_id=stream['id'], 
                                        pipeline_id=args.pipeline_id,deployment_config=args.deployment_config,
                                        deployment_prefix=args.deployment_prefix).process())

        return tasks
        
    async def _process_existing_live_streams_with_tag(self, args, api_client, queuing_lock):
        tasks = []
        logging.info(f"Getting existing live streams with tag {args.stream_tag}")
        live_streams = await api_client.get_streams(args.stream_tag, stream_type="rtsp")
        for stream in live_streams:
            # Create a task for processing this file
            tasks.append(LumeoDeployer(api_client, queuing_lock, stream_id=stream['id'],
                                        gateway_id=args.gateway_id, pipeline_id=args.pipeline_id,
                                        deployment_config=args.deployment_config,
                                        deployment_prefix=args.deployment_prefix).process())
        return tasks
    
    async def _process_existing_live_stream(self, args, api_client, queuing_lock):
        tasks = []  
        tasks.append(LumeoDeployer(api_client, queuing_lock, stream_id=args.stream_id,
                                        gateway_id=args.gateway_id, pipeline_id=args.pipeline_id,
                                        deployment_config=args.deployment_config,
                                        deployment_prefix=args.deployment_prefix).process())
        return tasks
    
    async def _process_live_stream_list(self, args, api_client, queuing_lock):
        tasks = []  
        for stream_url in args.stream_urls.split(','):
            tasks.append(LumeoDeployer(api_client, queuing_lock, stream_uri=stream_url, tag_id=args.stream_tag,
                                        gateway_id=args.gateway_id, pipeline_id=args.pipeline_id,
                                        deployment_config=args.deployment_config,
                                        deployment_prefix=args.deployment_prefix).process())
        return tasks    
    
    async def _get_tag_id(self, tag_path, create=False):
        tag_id = None
        # tag is to be applied. get or create tag path.
        try:
            uuid.UUID(tag_path)
            tag_id = tag_path
        except ValueError:
            tag_id = await self._api_client.get_tag_id_by_path(tag_path)
            if not tag_id and create:
                logging.info(f"Tag path '{tag_path}' not found. Creating...")
                tag_id = await self._api_client.create_tag_path(tag_path)
            if not tag_id:
                logging.error(f"Tag path '{tag_path}' not found.")
        return tag_id

    async def _get_s3_file_list(self, bucket_name, access_key_id, secret_access_key, region, endpoint_url=None, prefix=None):
        file_list = []
        s3_config = {
            'aws_access_key_id': access_key_id,
            'aws_secret_access_key': secret_access_key,
            'config': Config(signature_version='s3v4')
        }

        if endpoint_url:
            s3_config['endpoint_url'] = endpoint_url
        else:
            s3_config['region_name'] = region

        s3 = boto3.client('s3', **s3_config)

        paginator = s3.get_paginator('list_objects_v2')
        pagination_params = {'Bucket': bucket_name}
        if prefix:
            pagination_params['Prefix'] = prefix

        for page in paginator.paginate(**pagination_params):
            for obj in page.get('Contents', []):
                signed_url = s3.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name,
                                                                'Key': obj['Key']},
                                                        ExpiresIn=604800)  # 1 week in seconds
                file_list.append(signed_url)

        return file_list

    async def _process_tasks(self, tasks):
        results = []
        sem = asyncio.Semaphore(self._args.batch_size)
        async def process_with_limit(task):
            async with sem:
                return await task

        tasks = [process_with_limit(task) for task in tasks]
        for completed in asyncio.as_completed(tasks):
            result = await completed
            results.append(result)
        return results

    def _log_results(self, results):
        end_time = time.time()
        successful_tasks = sum(1 for status, _ in results if status)
        failed_tasks = sum(1 for status, _ in results if not status)
        print(f"Finished queueing. Results : Total {len(results)}, Successful {successful_tasks}, Failed {failed_tasks}.")    
        print(f"Total processing time: {round(end_time - self._start_time, 2)} seconds")


    async def _print_queue_size(self, api_client: LumeoApiClient):
        # Get the deployment queue for this app
        deployment_queue_id = await api_client.get_deployment_queue_id()
        queue_entries = await api_client.get_queue_entries(deployment_queue_id)
        print(f"Current Queue size: {len(queue_entries)}")

    async def _clear_queue(self, api_client: LumeoApiClient):
        # Get current queue size first
        deployment_queue_id = await api_client.get_deployment_queue_id()
        queue_entries = await api_client.get_queue_entries(deployment_queue_id)
        queue_size = len(queue_entries)

        if queue_size == 0:
            print("Queue is already empty")
            return

        # Confirm with user before proceeding
        confirmation = input(f"Are you sure you want to clear {queue_size} entries from the queue? (y/N): ")
        if confirmation.lower() != 'y':
            print("Queue clear cancelled")
            return
        
        for entry in queue_entries:
            await api_client.delete_queue_entry(deployment_queue_id, entry['id'])

        print(f"Queue cleared. Total entries deleted: {len(queue_entries)}")

def run_main():
    asyncio.run(BulkDeployer().run())
        
# if __name__ == "__main__":
#     main()
