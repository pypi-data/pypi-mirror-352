import requests

def checkDockerKubernetesStatus(ip_address, port):
    url = f"http://{ip_address}:{port}/_ping" 
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except requests.exceptions.ConnectionError:
        pass
    return False


