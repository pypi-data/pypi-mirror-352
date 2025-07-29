import docker
from aixblock_core.core.utils.params import get_env
import json
import subprocess
import time
import shlex


def dockerContainerStartStop(
    base_image, action, ip_address, project_id=None, model_id=None, user_id=None, gpu_id=None, gpu_index=None
    ):
    network_name = f"aixblock_network_u{user_id}_g{gpu_id}_i{gpu_index}"

    client = docker.DockerClient(base_url=f"tcp://{ip_address}:4243")
    client.login(username="quoiwowai", password="Abc!23456")
    service = base_image.replace("/", "-").replace(":", "-")
    name = None
    filters = {"name": f"project-{project_id}_{model_id}_{service}"}
    if user_id and gpu_id and project_id is None and model_id is None : 
        name = f"{service}-{network_name}"
        filters = {"name": name}
    containers = client.containers.list(filters=filters, all=True)

    container = None  # Initialize container variable with a default value

    if action == "start" and len(containers) > 0:
        try:
            container = containers[0] 
            container.start()
            container.reload()  
            ports = container.ports.get("9090/tcp")
            if ports:
                port = ports[0]["HostPort"]
                print("Container port:", port)  # Print the port here
                return port
            else:
                print("Port 9090/tcp is not exposed by the container.")
                return None
        except Exception as e:
            print("An error occurred while starting the container:", e)
    elif action == "stop" and len(containers) > 0:
        try:
            container = containers[0]  # Update container variable
            container.stop()
            return "0"
        except Exception as e:
            print(e)
    elif action == "delete" and len(containers) > 0:
        try:
            container = containers[0]  # Update container variable
            container.stop()
            container.remove()
            return
        except Exception as e:
            print(e)
    return "0"


def dockerContainerReadConfig(ip_address):

    # Connect to the Docker daemon
    client = docker.DockerClient(base_url=f"tcp://{ip_address}:4243")

    # Login to the Docker registry
    client.login(username="quoiwowai", password="Abc!23456")

    # Pull the latest version of the image
    client.api.pull("wowai/system-monitor:latest", stream=True, decode=True)

    # Remove all existing containers
    for container in client.containers.list(all=True):
        if "wowai/system-monitor" in container.image.tags:
            container.remove(force=True)

    # Run the new container
    container = client.containers.run(
        "wowai/system-monitor",
        detach=True,
        runtime="nvidia",
        environment={"NVIDIA_VISIBLE_DEVICES": "all"},
        devices=["/dev/mem:/dev/mem"],
        cap_add=["SYS_RAWIO"],
        privileged=True,
    )

    # Wait for the container to gather system information
    time.sleep(60)

    # Fetch logs from the container
    result = container.logs()

    # Parse the logs as JSON
    system_info = json.loads(result)

    # Remove the container
    container.remove()

    return system_info


def remove_container_with_image(image_name):
    # Construct the command to list container IDs
    list_command = f"docker ps -a -q --filter ancestor={image_name}"

    # Run the command to get the list of container IDs
    result = subprocess.run(shlex.split(list_command), capture_output=True, text=True)

    # Get the output (container IDs) from the result
    container_ids = result.stdout.strip().split("\n")

    # If there are any container IDs, remove them
    if container_ids and container_ids[0]:
        # Construct the command to remove containers
        remove_command = f"docker rm {' '.join(container_ids)}"
        subprocess.run(shlex.split(remove_command))
    else:
        print(f"No containers found for the image {image_name}")
