import requests
import argparse
from datetime import datetime
import asyncio
from lumeo.api import LumeoApiClient

state = {
    "lumeo_app_id": "",
    "lumeo_app_token": "",
    "wave_server": "",
    "wave_username": "",
    "wave_password": "",
    "start_time": None,
    "duration": None,
    "session": requests.Session(),
    "cameras": [],
    "created_tags": {}
}

async def get_token():
    response = state['session'].post(f"https://{state['wave_server']}/rest/v2/login/sessions", 
                                     json={
                                         'username': state['wave_username'],
                                         'password': state['wave_password'],
                                         'setCookie': False
                                     })
    if response.ok:
        state['wave_token'] = response.json()['token']
        state['session'].headers.update({'Authorization': f"Bearer {state['wave_token']}"})
        print(f"Got token: {state['wave_token']}")
        return True
    else:
        print(f"Failed to get token. Error: {response.text}")
        return False

async def select_or_verify_gateway():
    if state['gateway_id']:
        gateway = await state['lumeo_api_client'].get_gateway(state['gateway_id'])
        if gateway:
            print(f"Linking to gateway {gateway['name']} with ID {gateway['id']}")
            return gateway['id']
        else:
            print(f"No gateway found with ID {state['gateway_id']}")
            return None
    else:
        gateways = await state['lumeo_api_client'].get_gateways()        
        available_gateways = [gateway['id'] for gateway in gateways]
        if gateways:
            print("Available gateways in this workspace:")
            for idx, gateway in enumerate(gateways):
                print(f"{idx}. {gateway['id']}: {gateway['name']} ({gateway['status']})")
            while True:
                gateway_id = input("Enter the number or ID of the gateway to link imported cameras to: ")
                if gateway_id in available_gateways:
                    state['gateway_id'] = gateway_id
                    return state['gateway_id']
                elif gateway_id.isdigit() and int(gateway_id) in range(len(gateways)):
                    state['gateway_id'] = gateways[int(gateway_id)]['id']
                    return state['gateway_id']
                else:
                    print(f"Invalid gateway ID. Pick from the list above.")
        else:
            print("No gateways found in this workspace.")
            return None

async def fetch_cameras():
    """
    This script fetches a list of Avigilon cameras from the specified server, presents the list to the user,
    asks for the cameras to be imported, and then uses the Lumeo API to create streams with a specific stream URL.
    """
    
    # Get token
    if not await get_token():
        return
    
    # Query Avigilon API for list of cameras
    wave_cameras_url = (
        f"https://{state['wave_server']}/rest/v2/devices?deviceType=Camera"
        f"&_with=id,name,model,mac,vendor,url,parameters.customGroupId"
    )
    response = state['session'].get(wave_cameras_url)
    
    if response.ok:
        cameras = response.json()
        cameras.sort(key=lambda x: (x.get('parameters', {}).get('customGroupId', ''), x.get('name', '')))
        state['cameras'] = cameras
        
        # Present the list of cameras to the user
        print("Available cameras:")
        print("{:<10} {:<40} {:<60} {:<20} {:<20} {:<20}".format('Index', 'Name', 'Group', 'Manufacturer', 'Model', 'IP'))
        for index, camera in enumerate(cameras):
            print("{:<10} {:<40} {:<60} {:<20} {:<20} {:<20}".format(index, 
                                                                     camera.get('name',''), 
                                                                     camera.get('parameters', {}).get('customGroupId', '').replace('\n', ' > '), 
                                                                     camera.get('vendor',''), 
                                                                     camera.get('model',''), 
                                                                     camera.get('url', '').split('/')[2].split(':')[0]))
    else:
        print(f"Failed to fetch cameras from Wave. Error: {response.text}")

async def import_cameras():
    # Ask for the cameras to be imported
    camera_indices_to_import = input("Enter the indices or names of the cameras to import, separated by commas (Ctrl-c to exit) : ").split(',')

    # Use the Lumeo API to create streams with a specific stream URL
    for camera_index_or_name in camera_indices_to_import:
        camera = None
        if camera_index_or_name.isdigit():
            camera_index = int(camera_index_or_name)
            if 0 <= camera_index < len(state['cameras']):
                camera = state['cameras'][camera_index]
        else:
            camera = next((c for c in state['cameras'] if c['name'] == camera_index_or_name), None)

        if camera:
            await import_camera(camera)
        else:
            print(f"No camera found with index or name {camera_index_or_name}")    


async def import_camera(camera):
    """
    This function uses the Lumeo API to create a stream with a specific stream URL.
    """
    wave_camera_id = camera['id'].replace('{', '').replace('}', '')
    if state['start_time'] and state['duration']:
        stream_url = (
            f"https://{state['wave_username']}:{state['wave_password']}@{state['wave_server']}/hls/{wave_camera_id}.ts?pos={state['start_time']}&duration={state['duration']}&hi=true"
        )
        stream_name = f"{camera['name']} ({state['start_time']} - {state['duration']}s)"
        new_stream = await state['lumeo_api_client'].create_file_stream(stream_name, stream_url, camera_id=None, gateway_id=state['gateway_id'], disable_tls_verification=True)
    else:
        stream_url = (
            f"rtsp://{state['wave_username']}:{state['wave_password']}@{state['wave_server']}/{wave_camera_id}?codec=H264"
        )        
        new_stream = await state['lumeo_api_client'].create_live_stream(camera['name'], stream_url, gateway_id=state['gateway_id'])

    wave_tag_path = camera.get('parameters', {}).get('customGroupId', '').replace('/','_').replace('\n', '/')
    lumeo_tag_path = f"Hanwha Wave Import/{datetime.now().strftime('%Y-%m-%d')}"
    lumeo_tag_path = f"{lumeo_tag_path}/{wave_tag_path}" if wave_tag_path else lumeo_tag_path
    if lumeo_tag_path and lumeo_tag_path not in state['created_tags']:
        tag_id = await state['lumeo_api_client'].create_tag_path(lumeo_tag_path)
        state['created_tags'][lumeo_tag_path] = tag_id

    if lumeo_tag_path and lumeo_tag_path in state['created_tags']:
        await state['lumeo_api_client'].add_tag_to_stream(new_stream['id'], state['created_tags'][lumeo_tag_path])

    if new_stream:
        print(f"Successfully imported camera {camera['name']}")
    else:
        print(f"Failed to import camera {camera['name']}")
    

async def main():    
    parser = argparse.ArgumentParser(description='Fetch Hanwha Wave cameras and import them to Lumeo.')
    parser.add_argument("-l", "--lumeo_app_id", required=True, help='Your Lumeo workspace/application ID.')
    parser.add_argument("-t", "--lumeo_app_token", required=True, help='Your Lumeo workspace/application token.')
    parser.add_argument("-s", "--wave_server", required=True, help='The server IP/FQDN of your Wave system. Format: IP:PORT or FQDN:PORT.')
    parser.add_argument("-u", "--wave_username", required=True, help='Your Wave username.')
    parser.add_argument("-p", "--wave_password", required=True, help='Your Wave password.')
    parser.add_argument("-g", "--gateway_id", help='The ID of a gateway in your Lumeo workspace to connect the cameras to. Will prompt if not specified.')
    parser.add_argument("-q", "--quality", default='low', help='Options: high/low. Determines quality of video stream. Default is low.')    
    parser.add_argument("-i", "--start_time", help='The start time of the stream in ISO format. ex. 2024-05-02T14:30:00. If specified, will create a stream with this start time. Else creates a live stream.')
    parser.add_argument("-d", "--duration", help='The duration of the stream in seconds. ex. 3600. Required if --start_time is specified.')
    args = parser.parse_args()

    state['lumeo_app_id'] = args.lumeo_app_id
    state['lumeo_app_token'] = args.lumeo_app_token
    state['wave_server'] = args.wave_server.removeprefix('http://').removeprefix('https://').rstrip('/')
    state['wave_username'] = args.wave_username
    state['wave_password'] = args.wave_password    
    state['quality'] = args.quality
    state['gateway_id'] = args.gateway_id
    state['session'].verify = False
    state['start_time'] = args.start_time
    state['duration'] = args.duration
    
    if args.start_time:
        try:
            # Try parsing with various formats
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    parsed_time = datetime.strptime(args.start_time, fmt)
                    state['start_time'] = parsed_time.isoformat()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Unable to parse the provided start time.")
            
            if not state['duration']:
                raise ValueError("--duration is required if --start_time is specified.")
            
            state['duration'] = int(state['duration'])  # Ensure duration is an integer
        except ValueError as e:
            print(f"Error: {str(e)}")
            return
    
    state['lumeo_api_client'] = LumeoApiClient(state['lumeo_app_id'], state['lumeo_app_token'])

    state['gateway_id'] = await select_or_verify_gateway()
    if not state['gateway_id']:
        return

    await fetch_cameras()
    
    while True:
        await import_cameras()        
        if input("Do you want to import more cameras? (y/n): ").lower() != 'y':
            break
        
def run_main():
    asyncio.run(main())
        
if __name__ == "__main__":
    run_main()
