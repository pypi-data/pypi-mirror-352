import requests
import os
import json
import docker

# NOTIFILE_URL = 'http://103.160.78.156:7003/api/push/email'

IN_DOCKER = bool(os.environ.get('IN_DOCKER', True))
DOCKER_API = "tcp://69.197.168.145:4243" if IN_DOCKER else "unix://var/run/docker.sock"
HOSTNAME = '69.197.168.145'

class ServiceSendEmail:
    def __init__(self, docker_api, ip_address):
        # self.docker_client = docker.DockerClient(base_url=docker_api)
        self.ip_address = ip_address
        self.ancestor = "aixblock/notification-server"
        self.headers = {'Content-Type': 'application/json'}
    
    def send_email(self, data):
        # container = self.docker_client.containers.list(filters={'ancestor': self.ancestor})[-1]
        # ports = container.ports
        # port = "8005"

        # for p in ports:
        #     if p == '8004/tcp':
        #         port = ports[p][0]['HostPort']
        #         break
        json_data = json.dumps(data)

        try:
            port = 8004
            url = f'http://{self.ip_address}:{port}/api/push/email'
            response = requests.post(url, headers=self.headers, data=json_data, timeout=120)
            
        except requests.exceptions.Timeout:
            port = 8005
            url = f'http://{self.ip_address}:{port}/api/push/email'
            response = requests.post(url, headers=self.headers, data=json_data)

        return response


def get_data(subject, from_user, to_list_users, text, html, attachements_file = None):
    data = {
            "subject": subject,
            "from":from_user,
            "to": to_list_users,
            # "text": text,
            "html": html,
            "attachments": attachements_file
            # [
            #     {
            #         "filename": attachements_file,
            #         "content-type": attachments_type,
            #         "content": attachments_content
            #     }
            # ]
        }
    return data

import time


def send_email_thread(docker_address, ip_address, data, max_retries=3, delay=5):
    attempt = 0
    while attempt < max_retries:
        try:
            notify_response = ServiceSendEmail(docker_address, ip_address)
            notify_response.send_email(data)
            print("Email sent successfully.")
            break  # Exit the loop if the email is sent successfully
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All attempts failed. Email not sent.")


# notify_reponse = ServiceSendEmail(DOCKER_API)

# data = {
#             "subject": "Welcome to AIxBlock - Registration Successful!",
#             "from": "no-reply@app.aixblock.io",
#             "to": ["tqphu27@gmail.com"],
#             "text":    "Hello Jane!\n\nBye\n",
# 			"html":    "<p>Hello <b>Jane!</b></p>",
#         }
# response = notify_reponse.send_email(data)

# print(response.status_code)
# print(response.text)
