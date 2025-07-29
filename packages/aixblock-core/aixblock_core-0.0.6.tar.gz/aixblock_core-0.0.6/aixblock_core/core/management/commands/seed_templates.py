from django.core.management.base import BaseCommand
from users.models import User
from annotation_template.functions import import_annotation_templates
from model_marketplace.functions import import_catalog_model_templates, import_model_templates
from compute_marketplace.functions import import_catalog_compute_templates,  import_compute_templates,import_computegpu_templates,import_computegpu_price_templates,import_computegpu_timeworking_templates
from configs.functions import import_service_installation
class Command(BaseCommand):
    help = 'Seed templates'

    def add_arguments(self, parser):
        # Add arguments to command
        parser.add_argument(
            '--annotation_templates',
            action='store_true',
            help='Seed annotation templates',
        )
        parser.add_argument(
            '--catalog_compute',
            action='store_true',
            help='Seed catalog compute templates',
        )
        parser.add_argument(
            '--catalog_model',
            action='store_true',
            help='Seed catalog model templates',
        )

        parser.add_argument(
            '--models',
            action='store_true',
            help='Seed model templates',
        )

        parser.add_argument(
            '--computes',
            action='store_true',
            help='Seed computes templates',
        )

        parser.add_argument(
            '--computes_gpu',
            action='store_true',
            help='Seed computes_gpu templates',
        )

        parser.add_argument(
            '--compute_gpu_price',
            action='store_true',
            help='Seed compute_gpu_price templates',
        )

        parser.add_argument(
            '--compute_gpu_timeworking',
            action='store_true',
            help='Seed compute_gpu_timeworking templates',
        )

        parser.add_argument(
            '--service_installation',
            action='store_true',
            help='Seed service_installation templates',
        )

    def handle(self, *args, **options):
        # The first superuser
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR('No superuser found. Please create a superuser first.'))
            return

        # Determine if any specific seed option is provided
        specific_seed_provided = options['models'] or options['computes'] or options['annotation_templates'] or options['catalog_compute'] or options['catalog_model']

        # Seed catalog_compute
        if options['catalog_compute'] or not specific_seed_provided:
            catalog_compute = import_catalog_compute_templates() 
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(catalog_compute)} catalog compute templates.'))

        # Seed catalog_model
        if options['catalog_model'] or not specific_seed_provided:
            catalog_model= import_catalog_model_templates() 
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(catalog_model)} catalog model templates.'))

        # Seed computes
        if options['computes'] or not specific_seed_provided:
            computes = import_compute_templates(user.id)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(computes)} computes templates.'))

        # Seed model
        if options['models'] or not specific_seed_provided:
            model = import_model_templates(user.id)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(model)} models templates.'))

        # Seed computes_gpu
        if options['computes_gpu'] or not specific_seed_provided:
            computes_gpu = import_computegpu_templates(user.id)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(computes_gpu)} compute_gpus templates.'))

        # Seed computes_gpu_price
        if options['compute_gpu_price'] or not specific_seed_provided:
            compute_gpu_price = import_computegpu_price_templates(user.id)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(compute_gpu_price)} compute gpu price templates.'))

        # # Seed computes_gpu_timeworking
        # if options['compute_gpu_timeworking'] or not specific_seed_provided:
        #     compute_gpu_timeworking = import_computegpu_timeworking_templates(user.id)
        #     self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(compute_gpu_timeworking)} compute timeworking templates.'))

        # Seed annotation_templates
        if options["annotation_templates"] or not specific_seed_provided:
            annotation_templates = import_annotation_templates(user.id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully imported {annotation_templates} annotation templates."
                )
            )

        if options["service_installation"] or not specific_seed_provided:
            service_installation = import_service_installation()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully imported {len(service_installation)} Service Installation."
                )
            )
