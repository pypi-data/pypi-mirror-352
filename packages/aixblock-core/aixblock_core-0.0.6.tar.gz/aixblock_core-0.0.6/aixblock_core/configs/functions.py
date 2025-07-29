import json
from .models import InstallationService
import os
from core.settings.base import ENVIRONMENT

def import_service_installation():
    InstallationService.objects.all().delete()
    print("All CatalogModelMarketplace objects have been deleted.")
    env = "dev"
    if ENVIRONMENT == "prod":
        env =  "prod"
    elif  ENVIRONMENT == "stg":
        env = "stg"
    else:
        env = "dev"
    base_dir = os.path.dirname(__file__) 
    catalog_path = os.path.join(base_dir, 'seeds', 'installation_services.json')
    with open(catalog_path, 'r', encoding='utf-8') as file:
        installationServices = json.load(file)
        for item in installationServices:
            InstallationService.objects.create(
                name=item.get("name"),
                description=item.get("description"),
                version=item.get("version"),
                image=item.get("image"),
                registry=item.get("registry"),
                environment=item.get("environment"),
                status=item.get("status"),
            )
        return item
