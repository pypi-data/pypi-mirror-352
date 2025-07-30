import requests
import time
from datetime import datetime
import json
import sys
import argparse
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.console import Console

class StreamCleaner:
    def __init__(self, api_token, app_id, created_ts_until, created_ts_since=None, gateway_ids=None):
        self.api_token = api_token
        self.app_id = app_id
        self.base_url = "https://api.lumeo.com/v1"
        self.headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_token}"
        }
        self.created_ts_until = created_ts_until
        self.created_ts_since = created_ts_since
        self.gateway_ids = gateway_ids.split(',') if gateway_ids else None
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.skipped_streams = []
        self.console = Console()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_streams(self):
        """Fetch streams using offset pagination"""
        self.console.print("Fetching next batch of streams...")
        url = f"{self.base_url}/apps/{self.app_id}/streams"
        params = {
            "pagination": "offset",
            "page": 1,
            "limit": 50,
            "sources[]": "uri_stream",
            "stream_types[]": "file"
        }
        if self.created_ts_until:
            params["created_ts_until"] = self.created_ts_until
        if self.created_ts_since:
            params["created_ts_since"] = self.created_ts_since
        if self.gateway_ids:
            # Add each gateway ID as a separate gateway_ids[] parameter
            for gateway_id in self.gateway_ids:
                params.setdefault("gateway_ids[]", []).append(gateway_id)

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def delete_stream(self, stream_id, stream_name):
        """Delete a single stream with retries only for rate limiting"""
        url = f"{self.base_url}/apps/{self.app_id}/streams/{stream_id}"
        
        while True:
            try:
                response = self.session.delete(url)
                
                if 200 <= response.status_code < 300:  # Any 2xx status code is success
                    self.console.print(f"Deleted stream {stream_name} ({stream_id})")
                    return True
                
                if response.status_code == 429:  # Rate limited
                    retry_after = response.headers.get('retry-after')
                    if not retry_after:
                        try:
                            body = response.json()
                            message = body.get('message', '')
                            import re
                            match = re.search(r'(\d+)\s*(?:second|minute|hour)', message, re.IGNORECASE)
                            if match:
                                retry_after = int(match.group(1))
                                if 'minute' in message.lower():
                                    retry_after *= 60
                                elif 'hour' in message.lower():
                                    retry_after *= 3600
                            else:
                                retry_after = 60
                        except:
                            retry_after = 60
                    
                    self.console.print(f"Rate limited while deleting {stream_name}. Waiting {retry_after} seconds...")
                    time.sleep(int(retry_after))
                    continue
                
                # For any other error status code, log and skip
                error_msg = f"Error {response.status_code}"
                try:
                    error_msg += f": {response.json().get('message', '')}"
                except:
                    error_msg += f": {response.text}"
                
                self.console.print(f"Skipping stream {stream_name} due to {error_msg}")
                self.skipped_streams.append((stream_id, stream_name, error_msg))
                return False
                
            except requests.exceptions.RequestException as e:
                self.console.print(f"Skipping stream {stream_name} due to error: {str(e)}")
                self.skipped_streams.append((stream_id, stream_name, str(e)))
                return False

    def cleanup_streams(self):
        """Main cleanup function that handles pagination and rate limiting"""
        total_deleted = 0
        
        try:
            self.console.print("Fetching initial stream count...")
            response_data = self.get_streams()
            total_streams = response_data.get('total_elements', 0)
            
            if total_streams == 0:
                self.console.print("No streams found to delete.")
                return
            
            self.console.print(f"Found {total_streams} streams to delete")
            
            with Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                delete_task = progress.add_task(f"[cyan]Deleting {total_streams} streams...", total=total_streams)
                
                while True:
                    response_data = self.get_streams()
                    streams = response_data.get('data', [])
                    
                    if not streams:
                        break
                    
                    for stream in streams:
                        stream_id = stream['id']
                        stream_name = stream['name']
                        
                        if self.delete_stream(stream_id, stream_name):
                            total_deleted += 1
                            progress.update(delete_task, advance=1)
                        
                        time.sleep(0.5)  # Small delay between deletions
                    
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Error occurred: {str(e)}")
            
        self.console.print(f"\n[green]Cleanup completed.")
        self.console.print(f"Total streams deleted: {total_deleted}")
        
        if self.skipped_streams:
            self.console.print(f"\n[yellow]Skipped {len(self.skipped_streams)} streams:")
            for stream_id, stream_name, error in self.skipped_streams:
                self.console.print(f"- {stream_name} ({stream_id}): {error}")

def run_main():
    parser = argparse.ArgumentParser(description='Bulk delete streams & related deployments from a Lumeo app. Use with caution!')
    parser.add_argument('--token', required=True, help='API token')
    parser.add_argument('--app-id', required=True, help='Application ID')
    parser.add_argument('--created-ts-until', help='Delete streams created before this timestamp (ISO format)')
    parser.add_argument('--created-ts-since', help='Delete streams created after this timestamp (ISO format)')
    parser.add_argument('--gateway-ids', help='Comma-separated list of gateway IDs to filter streams')
    
    args = parser.parse_args()
    
    with StreamCleaner(args.token, args.app_id, args.created_ts_until, 
                      args.created_ts_since, args.gateway_ids) as cleaner:
        cleaner.cleanup_streams()
