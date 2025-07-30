import logging
from typing import Dict, Optional, Tuple, Union, cast, List

import aiofiles
import backoff
import httpx
from aiocache import cached
from backoff import _typing as backoff_typing
from httpx import HTTPError, HTTPStatusError, Timeout

from .lumeo_types import JsonObject

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("aiocache").setLevel(logging.WARNING)

def backoff_handler(details: backoff_typing.Details) -> None:
    logging.warning(
        f"Backing off {details['wait']:0.1f} seconds after {details['tries']} tries"
        f" calling function {details['target'].__name__} with args {details['args']} and kwargs {details['kwargs']}"
    )

def backoff_no_giveup(exc: Exception) -> bool:
    return False

class LumeoApiClient:
    client: httpx.AsyncClient = httpx.AsyncClient(timeout=Timeout(60.0))

    def __init__(self, application_id: str, token: str, api_base_url: str = 'https://api.lumeo.com') -> None:
        self.headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}
        self.base_url: str = api_base_url
        self.application_id = application_id
        self.client.base_url = self.base_url        
        self.client.headers = self.headers
        logging.info(f"Initialized Lumeo API client with base url: {self.base_url}, app_id: {application_id}, token: xxxx{token[-4:]}")

    def log_debug(self, message: str) -> None:
        logging.debug(f"{message}")
        
    def log_info(self, message: str) -> None:
        logging.info(f"{message}")

    def log_warning(self, message: str) -> None:
        logging.warning(f"{message}")

    def log_error(self, message: str) -> None:
        logging.error(f"{message}")
        
    async def close(self) -> None:
        await self.client.aclose()
        
    @backoff.on_exception(backoff.expo, HTTPError, max_time=60, on_backoff=backoff_handler, giveup=backoff_no_giveup, logger=None)        
    async def request(self, request_desc: str, method: str, url: str, timeout: Optional[Union[float, httpx.Timeout]] = None, **kwargs) -> Union[httpx.Response, None]:
        try:
            self.log_debug(f"API request: {request_desc} : {url}")
            response = await self.client.request(method, url, headers=self.headers, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except HTTPError as err:            
            # Log error    
            #print(f"{err} : {err.response.text}")
            message = f"{err.response.status_code} : {err.response.text}" if isinstance(err, HTTPStatusError) else err #error.response.text
            self.log_warning(f"API request failed. Will retry. {request_desc}: {message}")
            
            # If the error is a 400, 401, 403, 404, 409, dont raise exception, return None
            if isinstance(err, HTTPStatusError) and err.response.status_code in {400, 401, 403, 404, 409}:
                return None                    
            
            # Re-raise the exception to be caught by backoff
            raise
        except Exception as e:
            # This will catch the HTTPError re-raised by backoff after max_time is reached
            self.log_error(f"API Error {request_desc}: {message}")
            return None
        
    async def create_event(
        self, event_type: str, severity: str, payload: str, 
        deployment_id: Union[str, None], camera_id: Union[str, None], stream_id: Union[str, None]
    ) -> None:
        event_json = {
            "category": "ftp-gateway",
            "event_type": event_type,
            "severity": severity,
            "payload": payload,
            "context": None,
            "related_entities": {
                "deployment_id": None,
                "camera_id": None,
                "stream_id": None,
                "gateway_id": None,
                "file_id": None,
                "node_id": None,
            },
        }

        if deployment_id:
            event_json["object"] = "deployment"
            event_json["object_id"] = deployment_id
            event_json["related_entities"]["deployment_id"] = deployment_id

        if camera_id:
            event_json["object"] = "camera"
            event_json["object_id"] = camera_id
            event_json["related_entities"]["camera_id"] = camera_id
            
        if stream_id:
            event_json["object"] = "stream"
            event_json["object_id"] = stream_id
            event_json["related_entities"]["stream_id"] = stream_id

        await self.request(f"Creating event {event_type}", "POST", f"/v1/apps/{self.application_id}/events", json=event_json)

        return

    async def get_camera_with_external_id(self, external_id: str) -> Union[JsonObject, None]:
        response = await self.request(
            f"Getting camera with external id {external_id}",
            "GET",
            f"/v1/apps/{self.application_id}/cameras",
            params={"pagination": "cursor", "limit": 1, "external_ids[]": external_id},
        )
        response_json = response.json()
        if "data" in response_json and len(response_json["data"]) > 0:
            return response_json["data"][0]
        else:
            return None
        
    async def get_camera_with_id(self, camera_id: str) -> Union[JsonObject, None]:
        response = await self.request(
            f"Getting camera with id {camera_id}",
            "GET",
            f"/v1/apps/{self.application_id}/cameras/{camera_id}"
        )        
        if response:            
            return response.json()
        else:
            return None        

    async def get_gateways(self) -> JsonObject:
        all_gateways = []
        page = 1
        while True:
            response = await self.request(
                f"Getting gateways (page {page})",
                "GET",
                f"/v1/apps/{self.application_id}/gateways",
                params={"pagination": "offset", "limit": 50, "page": page}
            )
            
            response_json = response.json()            
            gateways = response_json.get('data', [])
            all_gateways.extend(gateways)
            
            if len(gateways) < 50:  # Less than the limit, so it's the last page
                break
            else:            
                page += 1        
        return all_gateways        


    async def get_gateway(self, gateway_id: str) -> Union[JsonObject, None]:
        response = await self.request(
            f"Getting gateway with id {gateway_id}",
            "GET",
            f"/v1/apps/{self.application_id}/gateways/{gateway_id}"
        )
        if response:
            return response.json()
        else:
            return None

    async def create_virtual_camera(self, external_id: str, name: str) -> JsonObject:
        response = await self.request(
            f"Creating virtual camera with external id {external_id}",
            "POST",
            f"/v1/apps/{self.application_id}/cameras",
            json={
                "external_id": external_id,
                "name": name,
                "model": "Virtual",
                "status": "unknown",
                "uri": None,
                "conn_type": "virtual",
            },
        )
        response_json = response.json()
        return response_json

    async def set_camera_reference_deployments(self, camera_id: str, deployment_id: str) -> None:
        await self.request(
            f"Setting camera reference deployment for camera {camera_id}",
            "POST",
            f"/v1/apps/{self.application_id}/cameras/{camera_id}/reference_deployments",
            json=[deployment_id],
        )

    @cached(ttl=3600)
    async def get_deployment_queue_id(self) -> str:
        response = await self.request(f"Getting deployment queue", "GET", f"/v1/apps/{self.application_id}/deployment_queues")
        response_json = response.json()
        return response_json and response_json[0]["id"]

    async def create_file(self, file_name: str, file_size: int, camera_id: Union[str,None]) -> JsonObject:
        response = await self.request(
            f"Creating file with file name {file_name}",
            "POST",
            f"/v1/apps/{self.application_id}/files",
            json={
                "name": file_name,
                "size": file_size,
                "gateway_id": None,
                "pipeline_id": None,
                "node_id": None,
                "deployment_id": None,
                "camera_id": camera_id,
                "stream_id": None,
                "metadata": None,
                "description": None,
            },
        )
        response_json = response.json()
        return response_json

    async def upload_file(self, data_url: str, metadata_url: str, file_path: str, timeout: Optional[Union[float, httpx.Timeout]] = 3600) -> None:
        self.log_debug(f"API Uploading file {file_path} ...")
        try:
            async with aiofiles.open(file_path, "rb") as f:
                file_content = await f.read()
                response = await self.client.put(data_url, data=file_content, timeout=timeout)
                response.raise_for_status()

            await self.client.put(metadata_url, data="null", timeout=timeout)
            return True
        except HTTPStatusError as error:
            self.log_error(f"HTTP error while uploading file {file_path}: {error.response.text}")
        except httpx.WriteTimeout as error:
            self.log_error(f"Write timeout while uploading file {file_path}: {error.__class__.__name__}")
        except httpx.ReadTimeout as error:
            self.log_error(f"Read timeout while uploading file {file_path}: {error.__class__.__name__}")
        except httpx.ConnectTimeout as error:
            self.log_error(f"Connection timeout while uploading file {file_path}: {error.__class__.__name__}")
        except Exception as error:
            self.log_error(f"Unexpected error while uploading file {file_path}: {error.__class__.__name__} - {str(error)}")

        return False

    async def set_file_status(self, file_id: str, status: str) -> None:
        await self.request(
            f"Setting file status for file {file_id}",
            "PUT",
            f"/v1/apps/{self.application_id}/files/{file_id}/cloud_status",
            data=status,
        )
        
    async def add_tag_to_file(self, file_id: str, tag_id: str) -> None:
        await self.request(
            f"Adding tag {tag_id} to file {file_id}",
            "POST",
            f"/v1/apps/{self.application_id}/files/{file_id}/tags",
            json=[tag_id],
        )
        
    async def get_files(self, file_ids: Union[List[str], None]=None, pipeline_ids: Union[List[str], None]=None, 
                        deployment_ids: Union[List[str], None]=None, camera_ids: Union[List[str], None]=None, 
                        stream_ids: Union[List[str], None]=None, gateway_ids: Union[List[str], None]=None, 
                        created_since: Union[str, None]=None, created_until: Union[str, None]=None) -> JsonObject:
        all_files = []
        page = 1
        while True:
            params = ["pagination=offset", f"limit=50", f"page={page}", "include_snapshots=false", "with_thumbnail=false"]
            
            if file_ids:
                params.extend([f"file_ids[]={file_id}" for file_id in file_ids])
            if pipeline_ids:
                params.extend([f"pipeline_ids[]={pipeline_id}" for pipeline_id in pipeline_ids])
            if deployment_ids:
                params.extend([f"deployment_ids[]={deployment_id}" for deployment_id in deployment_ids])
            if camera_ids:
                params.extend([f"camera_ids[]={camera_id}" for camera_id in camera_ids])
            if stream_ids:
                params.extend([f"stream_ids[]={stream_id}" for stream_id in stream_ids])
            if gateway_ids:
                params.extend([f"gateway_ids[]={gateway_id}" for gateway_id in gateway_ids])
            if created_since:
                params.append(f"created_ts_since={created_since}")
            if created_until:
                params.append(f"created_ts_until={created_until}")

            query_string = "&".join(params)
            response = await self.request(
                f"Getting files (page {page})",
                "GET",
                f"/v1/apps/{self.application_id}/files?{query_string}"
            )
            if response:
                response_json = response.json()
                all_files.extend(response_json.get('data', []))
                
                if len(response_json.get('data', [])) < 50:
                    break
            else:
                break
            
            page += 1

        return all_files

    async def get_file_with_id(self, file_id: str) -> Union[JsonObject, None]:
        response = await self.request(
            f"Getting file with id {file_id}",
            "GET",
            f"/v1/apps/{self.application_id}/files/{file_id}"
        )
        return response.json()

    async def create_lumeo_file_stream(self, file: JsonObject, camera_id: Union[str,None]) -> JsonObject:
        return await self.create_file_stream(file['name'], f"lumeo://{file['id']}", camera_id)
    
    async def create_file_stream(self, name: str, url: str, camera_id: Union[str,None], gateway_id: Union[str,None]=None, disable_tls_verification: bool=False) -> JsonObject:        
        response = await self.request(
            f"Creating file stream for file {name}",
            "POST",
            f"/v1/apps/{self.application_id}/streams",
            json={
                "name": name[:200],
                "uri": url,
                "source": "uri_stream",
                "stream_type": "file",
                "camera_id": camera_id,
                "gateway_id": gateway_id,
                "status": "unknown",
                "insecure_disable_tls_verification": disable_tls_verification
            },
        )
        response_json = response.json()
        return response_json
    
    async def create_live_stream(self, name: str, url: str, gateway_id: Union[str,None]=None) -> JsonObject:        
        response = await self.request(
            f"Creating live stream for file {name}",
            "POST",
            f"/v1/apps/{self.application_id}/streams",
            json={
                "name": name[:200],
                "uri": url,
                "source": "uri_stream",
                "stream_type": "rtsp",
                "camera_id": None,
                "gateway_id": gateway_id,
                "status": "unknown",
            },
        )
        response_json = response.json()
        return response_json
    
    async def get_streams(self, tag_id: str, stream_type: str="file") -> JsonObject:
        all_streams = []
        page = 1
        while True:
            response = await self.request(
                f"Getting file streams for tag {tag_id} (page {page})",
                "GET",
                f"/v1/apps/{self.application_id}/streams",
                params={"pagination": "offset", "limit": 50, "page": page, "stream_types[]": stream_type, "tagged_with[]": tag_id,
                        "include_tagged_with_descendants": False, "only_untagged": False}
            )
            
            response_json = response.json()            
            streams = response_json.get('data', [])
            all_streams.extend(streams)
            
            if len(streams) < 50:  # Less than the limit, so it's the last page
                break
            else:            
                page += 1        
        return all_streams
        
    @cached(ttl=3600)
    async def get_stream_with_id(self, stream_id: str) -> Union[JsonObject, None]:
        response = await self.request(
            f"Getting stream with id {stream_id}",
            "GET",
            f"/v1/apps/{self.application_id}/streams/{stream_id}"
        )        
        if response:            
            return response.json()
        else:
            return None     
        
    async def add_tag_to_stream(self, stream_id: str, tag_id: str) -> None:
        await self.request(
            f"Adding tag {tag_id} to stream {stream_id}",
            "POST",
            f"/v1/apps/{self.application_id}/streams/{stream_id}/tags",
            json=[tag_id],
        )  
    
    async def get_tag_id_by_path(self, tag_path: str) -> JsonObject:
        tag_names = tag_path.split("/")
        current_tag_id = None
        for tag_name in tag_names:
            params = {"pagination": "offset", "page": 1, "limit": 1, "tag_names[]": tag_name}
            if current_tag_id:
                params['parents[]'] = current_tag_id
                
            response = await self.request(
                f"Getting tag {tag_name}", "GET", f"/v1/apps/{self.application_id}/tags", params=params
            )
            if response:
                tags_list = response.json()
                if tags_list['data']:
                    current_tag_id = tags_list['data'][0]['id']
                else:
                    return None
            else:
                return None
        self.log_debug(f"Tag leaf {tag_path} found with id {current_tag_id}")                
        return current_tag_id
    
    async def create_tag_path(self, tag_path: str) -> JsonObject:
        tag_names = tag_path.split("/")
        current_tag_id = None
        for tag_name in tag_names:
            # Check if the tag already exists
            existing_tag = await self.get_tag_id_by_path("/".join(tag_names[:tag_names.index(tag_name)+1]))
            if existing_tag:
                current_tag_id = existing_tag
            else:
                # Create the tag if it doesn't exist
                response = await self.request(
                    f"Creating tag {tag_name}", "POST", f"/v1/apps/{self.application_id}/tags",
                    json={
                        "name": tag_name,
                        "parent": current_tag_id,
                    },
                )
                if response:
                    response_json = response.json()
                    current_tag_id = response_json["id"]
                else:
                    return None
        return current_tag_id
    
    @cached(ttl=3600)
    async def get_pipeline(self, pipeline_id: str) -> Union[JsonObject, None]:
        response = await self.request(
            f"Getting pipeline {pipeline_id}", "GET", f"/v1/apps/{self.application_id}/pipelines/{pipeline_id}"
        )
        response_json = response.json()
        return response_json

    async def get_deployment(self, deployment_id: str) -> Union[JsonObject, None]:
        response = await self.request(
            f"Getting deployment {deployment_id}", "GET", f"/v1/apps/{self.application_id}/deployments/{deployment_id}"
        )
        response_json = response.json()
        return response_json
    
    async def get_deployments(self, gateway_id: str, state: str="running") -> JsonObject:
        all_deployments = []
        page = 1
        while True:
            response = await self.request(
                f"Getting deployments for gateway {gateway_id} (page {page})",
                "GET",
                f"/v1/apps/{self.application_id}/deployments",
                params={"pagination": "offset", "limit": 50, "page": page, "gateway_ids[]": gateway_id, "states[]": state}
            )
            
            response_json = response.json()            
            deployments = response_json.get('data', [])
            all_deployments.extend(deployments)
            
            if len(deployments) < 50:  # Less than the limit, so it's the last page
                break
            else:            
                page += 1        
        return all_deployments
    
    async def set_deployment_state(self, deployment_id: str, state: str) -> None:
        await self.request(
            f"Setting deployment {deployment_id} state to {state}",
            "POST",
            f"/v1/apps/{self.application_id}/deployments/{deployment_id}/{state}"
        )
        
    async def delete_deployment(self, deployment_id: str) -> None:
        await self.request(
            f"Deleting deployment {deployment_id}",
            "DELETE",
            f"/v1/apps/{self.application_id}/deployments/{deployment_id}"
        )

    async def queue_deployment(
        self, queue_id: str, pipeline_id: str, deployment_configuration: JsonObject, deployment_name: Union[str, None]
    ) -> JsonObject:
        response = await self.request(
            f"Queueing deployment for pipeline {pipeline_id} with name '{deployment_name}', configuration {deployment_configuration}",
            "POST",
            f"/v1/apps/{self.application_id}/deployment_queues/{queue_id}/entries",
            json={
                "pipeline_id": pipeline_id,
                "deployment_name": deployment_name,
                "deployment_configuration": deployment_configuration,
            },
        )
        response_json = response.json()
        return response_json
    
    async def create_deployment(
        self, pipeline_id: str, gateway_id: str, deployment_configuration: JsonObject, deployment_name: Union[str, None]
    ) -> JsonObject:
        response = await self.request(
            f"Creating deployment for pipeline {pipeline_id} with name '{deployment_name}', configuration {deployment_configuration}",
            "POST",
            f"/v1/apps/{self.application_id}/deployments",
            json={
                "pipeline_id": pipeline_id,
                "gateway_id": gateway_id,
                "name": deployment_name,
                "state": "running",
                "configuration": deployment_configuration,
            },
        )
        response_json = response.json()
        return response_json

    async def get_queue_entries(self, queue_id: str) -> JsonObject:
        all_entries = []
        page = 1
        while True:
            response = await self.request(
                f"Getting queue info for queue {queue_id} (page {page})", 
                "GET", 
                f"/v1/apps/{self.application_id}/deployment_queues/{queue_id}/entries",
                params={"pagination": "offset", "page": page, "limit": 100},            
            )
            response_json = response.json()
            entries = response_json.get('data', [])
            all_entries.extend(entries)
            
            if len(entries) < 100:  # Less than the limit, so it's the last page
                break
            else:            
                page += 1        
        return all_entries

    async def delete_queue_entry(self, queue_id: str, entry_id: str) -> None:
        await self.request(
            f"Deleting queue entry {entry_id} from queue {queue_id}",
            "DELETE",
            f"/v1/apps/{self.application_id}/deployment_queues/{queue_id}/entries/{entry_id}"
        )
