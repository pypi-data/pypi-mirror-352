import docker
from django.conf import settings
import tarfile
import io
class NginxReverseProxy:
    def __init__(self, docker_api, container_name):
        self.docker_client = docker.DockerClient(base_url=docker_api)
        self.nginx_container_name = f"nginx_proxy_{container_name}"
        
    def generate_nginx_config(self, ip_address, proxy_pass=None):
        if not proxy_pass:
            proxy_pass = "http://docker_ml"

        upstreams = f"server                    {ip_address} fail_timeout=0;"

        nginx_config = f"""
            worker_processes 1;

            events {{ worker_connections 1024; }}

            http {{

                sendfile on;
                large_client_header_buffers 4 32k;

                upstream docker_ml {{{upstreams}}}
            
                # let gitlab deal with the redirection
                server {{
                    listen                    80;
                    server_name               app.aixblock.io;
                    server_tokens             off;
                    root                      /dev/null;
            
                    # Increase this if you want to upload larger attachments
                    client_max_body_size      20m;
            
                    # individual nginx logs for this vhost
                    # access_log                /var/log/nginx/gitlab_access.log;
                    # error_log                 /var/log/nginx/gitlab_error.log;
            
                    location / {{
                    proxy_read_timeout      300;
                    proxy_connect_timeout   300;
                    proxy_redirect          off;
                    proxy_pass              {proxy_pass};
                    }}
                }}

                server {{
                    listen                    443 ssl;
                    server_name               app.aixblock.io;
                    server_tokens             off;
                    root                      /dev/null;

                    # Increase this if you want to upload larger attachments
                    client_max_body_size      20m;

                    # SSL configuration
                    ssl_certificate           /etc/nginx/ssl/reverse.aixblock.io.fullchain.pem;
                    ssl_certificate_key       /etc/nginx/ssl/reverse.aixblock.io.privkey.pem;

                    location / {{
                        proxy_read_timeout      300;
                        proxy_connect_timeout   300;
                        proxy_redirect          off;
                        proxy_pass              {proxy_pass};
                    }}
                }}
            }}
        """

        return nginx_config

    def start_nginx_container(self):
        container = self.docker_client.containers.run(
                'nginx:latest',
                command='sleep infinity',
                name= self.nginx_container_name,
                detach=True,
                remove=True,
                ports={
                    '80/tcp': None,
                    '443/tcp': None
                },
            )
        
        return container

    def install_nginx(self):
        try:
            nginx_container = self.docker_client.containers.get(self.nginx_container_name)
            nginx_container.exec_run('apt install -y nginx')
        except Exception as e:
            print(e)

    def restart_nginx_service(self):
        nginx_container = self.docker_client.containers.get(self.nginx_container_name)
        nginx_container.exec_run('nginx -s reload')
    
    def remove_nginx_service(self):
        try:
            containers = self.docker_client.containers.list(filters={'name': f"{self.nginx_container_name}_*"}, all=True)
            for container in containers:
                try:
                    if container.status == "running":
                        container.stop()
                    container.remove()
                    
                    print("Container removed successfully.")
                    container.exec_run("service nginx restart")
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)

    def create_tar_archive(self, files):
        # Tạo tar archive từ danh sách các file
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            for file_path, arcname in files:
                tar.add(file_path, arcname=arcname)
        tar_stream.seek(0)
        return tar_stream
    
    def configure_reverse_proxy(self, url, proxy_pass=None):
        containers = self.docker_client.containers.list(all=True, filters={"name": self.nginx_container_name})
        if containers:
            temporary_container = containers[0]
        else:
            temporary_container = self.start_nginx_container()

            self.install_nginx()

            container_status = temporary_container.status
            if container_status != "running":
                try:
                    temporary_container.start()
                    # ssl_cert_path = "/etc/nginx/ssl/your_domain.crt"
                    # ssl_key_path = "/etc/nginx/ssl/your_domain.key"
                    # temporary_container.exec_run("mkdir -p /etc/nginx/ssl", privileged=True)
                    # temporary_container.exec_run("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout {} -out {} -subj '/C=US/ST=State/L=City/O=Organization/OU=Organizational Unit/CN=Common Name'".format(ssl_key_path, ssl_cert_path), privileged=True)

                    local_privkey = "./templates/ssl_cert/reverse.aixblock.io.privkey.pem"
                    local_fullchain = "./templates/ssl_cert/reverse.aixblock.io.fullchain.pem"

                    files_to_copy = [
                        (local_privkey, "ssl/reverse.aixblock.io.privkey.pem"),
                        (local_fullchain, "ssl/reverse.aixblock.io.fullchain.pem")
                    ]
                    tar_stream = self.create_tar_archive(files_to_copy)

                     # Sao chép archive tar vào container tại /etc/nginx/
                    temporary_container.put_archive("/etc/nginx", tar_stream)

                    nginx_config = self.generate_nginx_config(url, proxy_pass)
                    
                    temporary_container.exec_run(f"sh -c 'echo \"{nginx_config}\" > /etc/nginx/nginx.conf'", privileged=True)

                    temporary_container.reload()

                    temporary_container.exec_run("service nginx restart")

                except Exception as e:
                    print(e)

        port_proxy = temporary_container.ports['443/tcp'][0]['HostPort']


        reverse_ssl = f'{settings.REVERSE_IP}:{port_proxy}'
        print("Container configuration updated successfully.")
        
        return reverse_ssl
        # self.docker_client.close()

# ip = "69.197.168.145"
# port = 9000
# nginx_proxy_manager = NginxReverseProxy(f'tcp://69.197.168.145:4243', f'{ip}_{port}')
# res_url = nginx_proxy_manager.configure_reverse_proxy(f'{ip}:{port}', f'http://{ip}:{port}')