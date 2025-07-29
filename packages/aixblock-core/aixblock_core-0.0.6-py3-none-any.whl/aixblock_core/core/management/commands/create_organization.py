from django.core.management.base import BaseCommand
from users.models import User  
from organizations.models import Organization 
from core.utils.common import create_hash

class Command(BaseCommand):
    help = 'Create a new organization with extended fields'

    def add_arguments(self, parser):
        parser.add_argument('title', type=str, help='The title of the organization')
        parser.add_argument('--created_by_id', type=int, help='ID of the user creating the organization')
        parser.add_argument('--token', type=str, help='A unique token for the organization')
        parser.add_argument('--team_id', type=int, help='Team ID associated with the organization')
        parser.add_argument('--status', type=str, default='actived', help='Status of the organization')

    def handle(self, *args, **options):
        title = options['title']
        created_by_id = options['created_by_id']
        token = options['token']
        team_id = options['team_id']
        status = options['status']

        # If created_by_id is not provided, use the first superuser's ID
        if not created_by_id:
            superuser = User.objects.filter(is_superuser=True).last()
            if not superuser:
                self.stdout.write(self.style.ERROR('No superuser found. Please specify a created_by_id or create a superuser.'))
                return
            created_by_id = superuser.id
        if not token:
            token = create_hash
        if not team_id:
            team_id = create_hash
        if not status:
            status = "actived"
        # Fetch the user instance for created_by_id
        try:
            created_by = User.objects.get(pk=created_by_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID "{created_by_id}" does not exist.'))
            return

        # Create the organization
        organization, created = Organization.objects.get_or_create(
            title=title,
            defaults={
                'created_by': created_by,
                'token': token,
                'team_id': team_id,
                'status': status
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created organization "{title}"'))
            # Update the created_by user's active_organization_id with the newly created organization's ID
            created_by.active_organization_id = organization.id
            created_by.save()
            self.stdout.write(self.style.SUCCESS(f'Updated user {created_by_id} active organization to "{organization.id}"'))
        else:
            self.stdout.write(self.style.WARNING(f'Organization "{title}" already exists'))