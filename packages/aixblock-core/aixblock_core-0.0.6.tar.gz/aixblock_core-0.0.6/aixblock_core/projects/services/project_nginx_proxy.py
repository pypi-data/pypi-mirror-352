import docker
import os

from projects.models import ProjectMLPort

IN_DOCKER = bool(os.environ.get('IN_DOCKER', True))
DOCKER_API = "tcp://108.181.196.144:4243" if IN_DOCKER else "unix://var/run/docker.sock"
HOSTNAME = '108.181.196.144'

class NginxReverseProxyManager:
    def __init__(self, docker_api, project_id = None, host_name=None):
        self.docker_client = docker.DockerClient(base_url=docker_api)
        self.project_id = project_id
        self.nginx_container_name = f"nginx_proxy_{project_id}_"
        self.host_name = host_name
        
    def generate_nginx_config(self, containers):
        nginx_config = ''
        upstreams = ''

        for container in containers:
            ports = container.ports

            for port_info in ports['9090/tcp']:
                host_port = port_info['HostPort']
                break

            upstreams += f"server                    {self.host_name}:{host_port} fail_timeout=0;"

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
                    proxy_pass              http://docker_ml;
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
                    ssl_certificate           /etc/nginx/ssl/your_domain.crt;
                    ssl_certificate_key       /etc/nginx/ssl/your_domain.key;

                    location / {{
                        proxy_read_timeout      300;
                        proxy_connect_timeout   300;
                        proxy_redirect          off;
                        proxy_pass              http://docker_ml;
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
                if container.status == "running":
                    # print(f"Stopping container {container.id}...")
                    container.stop()
                # print(f"Removing container {container.id}...")
                port_proxy = container.ports['80/tcp'][0]['HostPort']
                ProjectMLPort.objects.filter(project_id = self.project_id, port = int(port_proxy), host = self.host_name).delete()
                container.remove()


                print("Container removed successfully.")
                container.exec_run("service nginx restart")
        except Exception as e:
            print(e)

    def configure_reverse_proxy(self, containers):
        

        temporary_container = self.start_nginx_container()
        self.install_nginx()

        container_status = temporary_container.status
        if container_status != "running":
            try:
                temporary_container.start()
                ssl_cert_path = "/etc/nginx/ssl/your_domain.crt"
                ssl_key_path = "/etc/nginx/ssl/your_domain.key"
                temporary_container.exec_run("mkdir -p /etc/nginx/ssl", privileged=True)
                temporary_container.exec_run("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout {} -out {} -subj '/C=US/ST=State/L=City/O=Organization/OU=Organizational Unit/CN=Common Name'".format(ssl_key_path, ssl_cert_path), privileged=True)
                # if result.exit_code == 0:
                #     print("Câu lệnh đã chạy thành công.")
                # else:
                #     print("Câu lệnh chạy không thành công. Lỗi:", result.output.decode())

                nginx_config = self.generate_nginx_config(containers)
                
                temporary_container.exec_run(f"sh -c 'echo \"{nginx_config}\" > /etc/nginx/nginx.conf'", privileged=True)
                temporary_container.reload()

                port_proxy = temporary_container.ports['443/tcp'][0]['HostPort']
                print(port_proxy)

                if ProjectMLPort.objects.filter(project_id = self.project_id).exists():
                    ProjectMLPort.objects.filter(project_id = self.project_id).update(port = port_proxy, host = self.host_name)
                else:
                    ProjectMLPort.objects.create(project_id = self.project_id, port = port_proxy, host = self.host_name)

                temporary_container.exec_run("service nginx restart")
                
                return port_proxy

            except Exception as e:
                print(e)

        self.docker_client.close()

        print("Container configuration updated successfully.")
        
        # nginx_containers = self.docker_client.containers.list(filters={'ancestor': 'nginx:latest'}, all=True)
        # for container in nginx_containers:
        #     print(container)
        #     try:
        #         if container.status == "running":
        #             print(f"Stopping container {container.id}...")
        #             container.stop()
             
        #         print(f"Removing container {container.id}...")
        #         container.remove()
        #         print("Container removed successfully.")
        #     except Exception as e:
        #         print(e)
# nginx_proxy_manager = NginxReverseProxyManager(DOCKER_API)
