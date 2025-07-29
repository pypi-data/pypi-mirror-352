import pathlib
from django.conf import settings
from .models import AnnotationTemplate
from core.utils.io import find_dir, read_yaml
from model_marketplace.models import CatalogModelMarketplace
from django.db import transaction
from urllib.parse import urlparse
import logging
logger = logging.getLogger(__name__)

def import_annotation_templates(user_id):
    # Clear existing data from AnnotationTemplate and ModelMarketplace
    AnnotationTemplate.objects.all().delete()
  
    try:
        # Count annotations after deletion (should be 0)
        annotation_count = AnnotationTemplate.objects.count()

        # Directory where YAML configuration files are located
        annotation_templates_dir = find_dir('annotation_templates')
        configs = []

        if annotation_count > 0:
            catalog_list = CatalogModelMarketplace.objects.all()
            for catalog in catalog_list:
                annotations = AnnotationTemplate.objects.filter(catalog_key=catalog.key)
                for annotation in annotations:
                    annotation.catalog_model_id = catalog.id
                    annotation.save()
            return annotation_count

        # Process each YAML configuration file
        for config_file in pathlib.Path(annotation_templates_dir).glob('**/*.yml'):
            config = read_yaml(config_file)
            configs.append(config)

            if config.get('image', '').startswith('/static') and settings.HOSTNAME:
                config['image'] = settings.HOSTNAME + config['image']

            url = config.get('ml_url', '').replace("http://", "")
            ml_ip = ml_port = ''
            if url:
                parsed_url = urlparse(url)
                ml_ip = parsed_url.hostname
                ml_port = parsed_url.port

            catalog_model_key = config['catalog_model_key']
            catalog = CatalogModelMarketplace.objects.filter(key=catalog_model_key).first()

            if annotation_count == 0 and catalog:
                AnnotationTemplate.objects.create(
                    name=config["title"],
                    order=config.get("order", 0),
                    image=config["image"],
                    ml_image=config.get("ml_image", ""),
                    config=config["config"],
                    ml_ip=ml_ip,
                    ml_port=ml_port,
                    author_id=user_id,
                    details=config["details"],
                    group=config["group"],
                    catalog_model_id=catalog.id,
                    catalog_key=catalog_model_key,
                )

        return len(configs)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return 0
