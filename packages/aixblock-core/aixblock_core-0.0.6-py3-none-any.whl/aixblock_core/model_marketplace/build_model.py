from .models import ModelMarketplace
from jenkinsapi.jenkins import Jenkins
import os
from jenkinsapi.custom_exceptions import NoBuildData, NotFound
import hashlib
from urllib.parse import urlparse
import time
from rest_framework import generics, status
import os
import datetime
import tempfile
from git import Repo
from roboflow import Roboflow
from datasets import load_dataset
from projects.services.project_cloud_storage import ProjectCloudStorage
from .models import CheckpointModelMarketplace
from core.settings.base import JENKINS_URL


# Function to generate a unique job name based on the Git URL
def generate_job_name(git_url):
    parsed_url = urlparse(git_url)
    repo_name = os.path.basename(parsed_url.path).replace(".git", "")
    unique_hash = hashlib.md5(git_url.encode()).hexdigest()
    return f"{repo_name}-{unique_hash}"


# Function to extract repository name from Git URL
def extract_repo_name(git_url):
    parsed_url = urlparse(git_url)
    repo_name = os.path.basename(parsed_url.path).replace(".git", "")
    return repo_name

def extract_hf_username(url):
    # Sử dụng biểu thức chính quy để tìm tên người dùng
    match = re.search(r'https://huggingface.co/([^/]+)/', url)
    if match:
        return match.group(1)
    return None

def build_model(model_source, model_id_url, model_token, model_name):
    if model_source == ModelMarketplace.ModelSource.DOCKER_HUB:
        return model_id_url
    if model_source == ModelMarketplace.ModelSource.GIT:
        return jenkins_build_image(model_id_url, model_token, True, model_name )
    if model_source == ModelMarketplace.ModelSource.HUGGING_FACE:
        return jenkins_build_image(model_id_url, model_token, True, model_name, "hf")
        
    if model_source == ModelMarketplace.ModelSource.ROBOFLOW:
        pass
    else:
        # unsupported source
        pass


def build_checkpoint(checkpoint, checkpoint_id_url, checkpoint_token):
    if checkpoint == ModelMarketplace.CheckpointSource.GIT:
        pass
    if checkpoint == ModelMarketplace.CheckpointSource.HUGGING_FACE:
        pass
    if checkpoint == ModelMarketplace.CheckpointSource.ROBOFLOW:
        pass
    if checkpoint == ModelMarketplace.CheckpointSource.KAGGLE:
        pass
    if checkpoint == ModelMarketplace.CheckpointSource.CLOUD_STORAGE:
        pass
    else:
        # unsupported source
        pass


import re
import unicodedata

def normalize_name(name):
    # Normalize the string to decompose special characters
    normalized_name = unicodedata.normalize('NFD', name)
    
    # Remove accents
    name_without_accents = ''.join(
        char for char in normalized_name 
        if unicodedata.category(char) != 'Mn'
    )
    
    # Replace all non-alphanumeric characters with hyphens
    name_with_hyphens = re.sub(r'[^a-zA-Z0-9]+', '-', name_without_accents)
    
    # Remove leading or trailing hyphens
    name_with_hyphens = name_with_hyphens.strip('-')
    
    return name_with_hyphens.lower()

# build image with jenkins server for model, checkpoint
def jenkins_build_image(git_url, git_token=None, delete_after_build=True, name = None, type="git"):
    model_name = None
    if name:
        model_name = normalize_name(name)

    # Jenkins URL and credentials
    def get_server_instance():
        jenkins_url = JENKINS_URL
        server = Jenkins(jenkins_url, username="admin", password="admin123@", timeout=20)
        return server

    def get_plugin_details(server):
        # Assuming get_server_instance is defined elsewhere

        for plugin in server.get_plugins().values():
            print("Short Name: {}".format(plugin.shortName))
            print("Long Name: {}".format(plugin.longName))
            print("Version: {}".format(plugin.version))
            print("URL: {}".format(plugin.url))
            print("Active: {}".format(plugin.active))
            print("Enabled: {}".format(plugin.enabled))

    jenkins = get_server_instance()
    # plugin = get_plugin_details(jenkins)

    # Generate a unique job name based on the Git URL
    job_name = model_name #generate_job_name(git_url)

    # Path to the job configuration XML
    job_config_path = os.path.join(os.path.dirname(__file__), "addjob.xml")

    # Read the job configuration XML
    with open(job_config_path, "r") as file:
        xml = file.read()

    # Modify the XML to include the agent label
    # xml = xml.replace(
    #     "<assignedNode></assignedNode>", "<assignedNode>jenkins-linux</assignedNode>"
    # )

    # Create or update the Jenkins job
    if job_name not in jenkins.jobs:
        job = jenkins.create_job(jobname=job_name, xml=xml)
    else:
        job = jenkins[job_name]
        job.update_config(xml)

    # repo_name = extract_repo_name(git_url)
    if type == "hf" and "http" not in git_url:
        git_url = "https://huggingface.co/" + git_url 
    if git_token:
        if type == "git":
            git_url = git_url.replace("https://", f"https://{git_token}@")
        else:
            hf_name = extract_hf_username(git_url)
            git_url = git_url.replace("https://", f"https://{hf_name}:{git_token}@")
    # Parameters for the Jenkins job (if required)
    image_name = f"wowai/{model_name}"
    parameters = {
        "GIT_URL": git_url,
        "IMAGE_NAME": image_name,
        "IMAGE_VERSION": "latest",
    }

    # Trigger build
    try:
        if job.is_queued_or_running():
            print("A build is already running for this job.")
        else:

            queue_item = job.invoke(build_params=parameters)
            print(
                f"Build triggered for {job_name}. Queue item number: {queue_item.queue_id}"
            )
            time.sleep(10)
            # Wait for the build to complete
            queue_item.block_until_complete()
            job = jenkins.get_job(job_name)
            current_number = job.get_next_build_number() -1
            complete_last_build = job.get_last_completed_build()
            if delete_after_build and complete_last_build.buildno == current_number:
                print(f"Deleting job {job_name} after build completion.")
                jenkins.delete_job(job_name)
                print(f"Job {job_name} deleted.")
            return image_name
    except Exception as e:
        print(f"An error occurred: {e}")


def model_source_git(model_upload, project, url, token= None):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone repository từ GitHub
        repo_url = url
        if token:
            repo_url = url.replace("https://", f"https://{token}@")
            
        Repo.clone_from(repo_url, temp_dir)
        # folder_path = find_file_in_directory(temp_dir, checkpoint_name)
        
        # Repo.clone_from(repo_url, temp_dir)
        model_upload.upload_directory(
            project=project,
            bucket_name=str(project.id),
            directory_path=temp_dir,
            new_thread=True
        )

def docker_hub(url, token= None):
    pass

def hugging_face_model_source(model_upload, project, repo_id, token= None):
    from huggingface_hub import snapshot_download
    with tempfile.TemporaryDirectory() as temp_dir:
        # dataset.save_to_disk(temp_dir)
        # hf_hub_download(repo_id="tals/albert-xlarge-vitaminc-mnli", filename="model.safetensors", cache_dir=temp_dir, resume_download=True)
        if token:
            snapshot_download(repo_id=repo_id, cache_dir=temp_dir, resume_download=True, token=token)
        else:
            snapshot_download(repo_id=repo_id, cache_dir=temp_dir, resume_download=True)

        model_upload.upload_directory(
            project=project,
            bucket_name=str(project.id),
            directory_path=temp_dir,
            new_thread=True
        )

def roboflow(id,token= None):
    pass

def kaggle(id, token= None):
    pass

def cloud_storage(id, token=None):
    pass

def find_file_in_directory(start_dir, target_file):
    for root, dirs, files in os.walk(start_dir):
        if target_file in files:
            return root
    return None

def git_checkpoint(checkpoint_upload, project, checkpoint_name, url, token=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone repository từ GitHub
        repo_url = url
        if token:
            repo_url = url.replace("https://", f"https://{token}@")
        Repo.clone_from(repo_url, temp_dir)
        folder_path = find_file_in_directory(temp_dir, checkpoint_name)
        
        # Repo.clone_from(repo_url, temp_dir)
        checkpoint_upload.upload_directory(
            project=project,
            bucket_name=str(project.id),
            directory_path=folder_path,
            new_thread=True
        )

def kaggle_checkpoint(checkpoint_upload, project, username, token, checkpoint_path):
    os.environ['KAGGLE_USERNAME'] = username
    os.environ['KAGGLE_KEY'] = token
    import kagglehub

    path = kagglehub.model_download(checkpoint_path)  

    checkpoint_upload.upload_directory(
        project=project,
        bucket_name=str(project.id),
        directory_path=path,
        new_thread=True
    )

    if os.path.exists(path):
        import shutil
        shutil.rmtree(path)

def hugging_face_checkpoint(checkpoint_upload, project, repo_id, checkpoint_name, token= None):
    from huggingface_hub import hf_hub_download
    with tempfile.TemporaryDirectory() as temp_dir:
        # dataset.save_to_disk(temp_dir)
        # hf_hub_download(repo_id="tals/albert-xlarge-vitaminc-mnli", filename="model.safetensors", cache_dir=temp_dir, resume_download=True)
        if token:
            hf_hub_download(repo_id=repo_id, filename=checkpoint_name, cache_dir=temp_dir, resume_download=True, token=token)
        else:
            hf_hub_download(repo_id=repo_id, filename=checkpoint_name, cache_dir=temp_dir, resume_download=True)

        folder_path = find_file_in_directory(temp_dir, checkpoint_name)
        checkpoint_upload.upload_directory(
            project=project,
            bucket_name=str(project.id),
            directory_path=folder_path,
            new_thread=True
        )

def create_s3_storage(dir_name = "checkpoint/"):
    model_upload = ProjectCloudStorage(bucket_prefix="project-", object_prefix=dir_name)
    return model_upload
