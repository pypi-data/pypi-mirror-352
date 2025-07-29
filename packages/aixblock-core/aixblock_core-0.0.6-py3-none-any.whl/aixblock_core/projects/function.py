import json
import time
import requests
from django.conf import settings
from urllib.parse import urlparse
from aixblock_core.core.utils.nginx_server import NginxReverseProxy

def convert_url(url, https=False):
    try: 
        parsed_url = urlparse(url)
        ip_address = parsed_url.hostname
        port = parsed_url.port
        nginx_proxy_manager = NginxReverseProxy(f'{settings.REVERSE_ADDRESS}', f'{ip_address}_{port}')
        if https:
            res_url = nginx_proxy_manager.configure_reverse_proxy(f'{ip_address}:{port}', f'https://{ip_address}:{port}')
        else:
            res_url = nginx_proxy_manager.configure_reverse_proxy(f'{ip_address}:{port}', f'http://{ip_address}:{port}')

    except Exception as e:
        print(e)
        res_url = f'{ip_address}:{port}'
        # payload = json.dumps({
        #     "url": url,
        #     "token": settings.TOKEN_URL_CONVERT
        # })
        # headers = {
        #     'Content-Type': 'application/json'
        # }

        # response = requests.request("POST", settings.URL_CONVERT, headers=headers, data=payload, timeout=10)

        # if response.status_code == 200:
        #     response_json = response.json()
        #     res_url = response_json.get("url").replace('https://', '').replace('http://', '')

    return res_url

def check_url_status(url, retries=3, wait_time=10):
    for attempt in range(retries):
        try:
            if "http" in url:
                response = requests.get(url)
            else:
                response = requests.get('https://'+url)
            if response.status_code == 200:
                return response.status_code
            elif response.status_code == 502:
                print(f"Attempt {attempt + 1}: Received 502 Bad Gateway. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return response.status_code
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    return "Failed to connect after multiple attempts."

def check_dashboard_url_until_available(dashboard_url, retries=10, delay=5):
    for _ in range(retries):
        try:
            # Make an HTTP request to check the dashboard URL
            response = requests.get(dashboard_url)
            
            # If the response status is not 502, return only the dashboard URL
            if response.status_code != 502:
                return True

        except requests.exceptions.RequestException:
            # Ignore errors and continue retrying
            pass

        # Wait for a few seconds before trying again
        time.sleep(delay)
    
    # If the dashboard is still down after retries, return nothing (or you can customize the response)
    return False