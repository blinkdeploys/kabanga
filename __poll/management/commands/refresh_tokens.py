from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from account.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    '''
    Import data from a JSON file into a Listings table
    python manage.py import_json_data.
    '''
    help = 'Import data from a JSON file into a Listings table'

    def add_arguments(self, parser):
        # parser.add_argument('file_path', type=str, help='The path to the JSON file')
        pass

    def handle(self, *args, **kwargs):
        handled = 0
        try:
            for user in User.objects.all():
                Token.objects.get_or_create(user=user)
                handled = handled + 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error refreshing token. Possible failure to fetch Token instance.'))
        self.stdout.write(self.style.SUCCESS(f'Tokens successfully created for {handled} user records.'))

