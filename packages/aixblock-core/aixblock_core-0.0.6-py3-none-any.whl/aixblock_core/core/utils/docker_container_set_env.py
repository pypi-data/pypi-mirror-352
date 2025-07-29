
def set_env_for_container(container, command):
    container.exec_run(f'/bin/bash -c "{command}"')
    container.reload()

# Example
# env_vars = {
#             "MINIO_API_URL": f'{ip_address}:9001',
#         }
# # Construct the command to set environment variables and execute your command
# command = " && ".join([f"export {key}={value}" for key, value in env_vars.items()])
# set_env_for_container(container, command)