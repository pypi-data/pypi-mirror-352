from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.utils.crypto import get_random_string

class Command(createsuperuser.Command):
    help = 'Crate a superuser, and allow password to be provided'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--username', dest='username', default=None,
            help='Specifies the username for the superuser.',
        )
        parser.add_argument(
            '--password', dest='password', default=None,
            help='Specifies the password for the superuser.',
        )
        parser.add_argument(
            '--preserve', dest='preserve', default=True, action='store_true',
            help='Exit normally if the user already exists.',
        )

    def handle(self, *args, **options):
        password = options.get('password')
        username = options.get('username')
        database = options.get('database')
        email = options.get('email')
        if password and not username:
            raise CommandError("--username is required if specifying --password")

        if username and options.get('preserve'):
            exists = self.UserModel._default_manager.db_manager(database).filter(username=username).exists()
            if exists:
                self.stdout.write("User exists, exiting normally due to --preserve")
                return
            
        if not password:
            password = get_random_string()
        # super(Command, self).handle(*args, **options)
        self.UserModel._default_manager.create_superuser(username=username, email=email, password=password)

        #./manage.py create_superuser_with_password --username test1 --password 123321 --noinput --email 'blank@email.com'