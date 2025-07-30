import asyncio
import colorlog
import httpx
import os
import logging
import argparse
from typing import List, Dict, Union
from pathlib import Path
from datetime import datetime, timezone

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID

from lumeo.api import LumeoApiClient
from lumeo.api.lumeo_types import JsonObject

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

console = Console()

class BulkDownloader:
    def __init__(self, api_client: LumeoApiClient, output_path_template: str, 
                 download_media: bool = True, download_metadata: bool = False, 
                 max_concurrent_downloads: int = 5):
        self.api_client = api_client
        self.output_path_template = output_path_template
        self.download_media = download_media
        self.download_metadata = download_metadata
        self.max_concurrent_downloads = max_concurrent_downloads
        self.progress = Progress()

    async def download_files(self, files: List[JsonObject]):
        sem = asyncio.Semaphore(self.max_concurrent_downloads)
        async with httpx.AsyncClient() as client:
            with self.progress:
                tasks = [self.download_file(client, sem, file) for file in files]
                self.overall_task_id = self.progress.add_task(f"Downloading {len(files)} files", total=len(files))
                await asyncio.gather(*tasks)

    async def download_file(self, client: httpx.AsyncClient, sem: asyncio.Semaphore, file: JsonObject):
        async with sem:
            output_path = self.get_output_path(file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            file_detail = await self.api_client.get_file_with_id(file['id'])
            if self.download_media:
                await self.download_content(client, file_detail['data_url'], output_path, file['name'])
            
            if self.download_metadata:
                metadata_path = f"{output_path}.metadata.json"
                await self.download_content(client, file_detail['metadata_url'], metadata_path, f"{file['name']} (metadata)")
                
            self.progress.update(self.overall_task_id, advance=1)

    async def download_content(self, client: httpx.AsyncClient, url: str, path: str, description: str):
        task_id = self.progress.add_task(f"Downloading {description}", total=None)
        try:
            async with client.stream('GET', url) as response:
                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    self.progress.update(task_id, total=total_size)
                    # Create the directory if it doesn't exist
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, 'wb') as f:
                        downloaded = 0
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            self.progress.update(task_id, completed=downloaded)
                    
                    #logging.info(f"Downloaded: {path}")
                else:
                    logging.error(f"Failed to download {url}. Status: {response.status_code}")
        finally:
            self.progress.remove_task(task_id)

    def get_output_path(self, file: JsonObject) -> str:
        template_vars = {
            'application_id': file['application_id'],
            'deployment_id': file.get('deployment_id', ''),
            'gateway_id': file.get('gateway_id', ''),
            'pipeline_id': file.get('pipeline_id', ''),
            'camera_id': file.get('camera_id', ''),
            'stream_id': file.get('stream_id', '')
        }
        output_path = self.output_path_template.format(**template_vars)
        return os.path.join(output_path, file['name'])

async def bulk_download(api_client: LumeoApiClient, output_path_template: str,
                        list: bool = True, download: bool = False, 
                        download_media: bool = True, download_metadata: bool = False, 
                        max_concurrent_downloads: int = 5, **kwargs):
    downloader = BulkDownloader(api_client, output_path_template, 
                                download_media, download_metadata, max_concurrent_downloads)
    
    files = await api_client.get_files(**kwargs)
    
    if list:
        total_size = sum(file.get('size', 0) for file in files)
        print(f"Filters: {kwargs}")
        print(f"Total files: {len(files)}")
        print(f"Total size: {total_size / (1024 * 1024):.2f} MB")

        table = Table(title="File List")
        table.add_column("File Name", style="cyan")
        table.add_column("Size (MB)", justify="right", style="green")
        table.add_column("Deployment ID", style="magenta")
        table.add_column("Gateway ID", style="yellow")
        table.add_column("Camera ID", style="blue")
        table.add_column("Stream ID", style="red")
        table.add_column("Created At", style="purple")

        for file in files:
            table.add_row(
                file['name'],
                f"{file.get('size', 0) / (1024 * 1024):.2f}",
                file.get('deployment_id', ''),
                file.get('gateway_id', ''),
                file.get('camera_id', ''),
                file.get('stream_id', ''),
                file.get('created_at', '')
            )

        console.print(table)
    
    if download:
        await downloader.download_files(files)
    else:
        print(f"Skipping download of {len(files)} files. Add --download parameter to download files.")

def parse_args():
    parser = argparse.ArgumentParser(description="Bulk download files from Lumeo API", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--app_id", required=True, help="Lumeo application ID")
    parser.add_argument("--token", required=True, help="Lumeo API token")
    parser.add_argument("--list", action="store_true", default=True, help="List files")
    parser.add_argument("--download", action="store_true", default=False, help="Download files")
    parser.add_argument("--download_media", action="store_true", default=True, help="Download media files")
    parser.add_argument("--download_metadata", action="store_true", default=True, help="Download metadata files")
    
    parser.add_argument("--output_path_template", default="{application_id}/{deployment_id}", help="Output folder path template. Available variables: application_id, deployment_id, gateway_id, pipeline_id, camera_id, stream_id")
    parser.add_argument("--max_concurrent_downloads", type=int, default=5, help="Maximum number of concurrent downloads")

    parser.add_argument("--file_ids", nargs="*", help="Comma separated list of file IDs to filter files")
    parser.add_argument("--pipeline_ids", nargs="*", help="Comma separated list of pipeline IDs to filter files")
    parser.add_argument("--deployment_ids", nargs="*", help="Comma separated list of deployment IDs to filter files")
    parser.add_argument("--camera_ids", nargs="*", help="Comma separated list of camera IDs to filter files")
    parser.add_argument("--stream_ids", nargs="*", help="Comma separated list of stream IDs to filter files")
    parser.add_argument("--gateway_ids", nargs="*", help="Comma separated list of gateway IDs to filter files")
    parser.add_argument("--created_since", help="Start date for file filtering (UTC format: YYYY-MM-DDTHH:MM:SSZ)")
    parser.add_argument("--created_until", help="End date for file filtering (UTC format: YYYY-MM-DDTHH:MM:SSZ)")
    return parser.parse_args()

async def main():
    args = parse_args()
    api_client = LumeoApiClient(args.app_id, args.token)
    
    kwargs = {}
    if args.file_ids:
        kwargs['file_ids'] = args.file_ids
    if args.pipeline_ids:
        kwargs['pipeline_ids'] = args.pipeline_ids
    if args.deployment_ids:
        kwargs['deployment_ids'] = args.deployment_ids
    if args.camera_ids:
        kwargs['camera_ids'] = args.camera_ids
    if args.stream_ids:
        kwargs['stream_ids'] = args.stream_ids
    if args.gateway_ids:
        kwargs['gateway_ids'] = args.gateway_ids
    if args.created_since:
        kwargs['created_since'] = args.created_since
    if args.created_until:
        kwargs['created_until'] = args.created_until
        
    # Ensure at least one filter is provided
    if not any([args.file_ids, args.pipeline_ids, args.deployment_ids, args.camera_ids, 
                args.stream_ids, args.gateway_ids, args.created_since, args.created_until]):
        logging.error("At least one filter (file_ids, pipeline_ids, deployment_ids, camera_ids, "
                      "stream_ids, gateway_ids, created_since, or created_until) is required.")
        return

    await bulk_download(
        api_client,
        output_path_template=args.output_path_template,
        list=args.list,
        download=args.download,
        download_media=args.download_media,
        download_metadata=args.download_metadata,
        max_concurrent_downloads=args.max_concurrent_downloads,
        **kwargs
    )

def run_main():
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

if __name__ == "__main__":
    run_main()
