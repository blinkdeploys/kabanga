import time
from __report.utils import collate_results, collate_seats
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    '''Collate results for all the levels and positions'''
    help = 'Collate results for all the levels and positions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='clear all exisitng collations',
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='reduced reporting',
        )
        parser.add_argument('--verbose',
                            action='store_true',
                            help='more noisy')
        # parser.add_argument('-models', '--models', type=str, nargs='+', help='The model to run if empty, then all models will be populated')
        # parser.add_argument('-verbose', '--verbose', type=int, nargs='+', help='Run the population showing each line from the scripts')

    def handle(self, *args, **kwargs):

        # noisy or quiet
        use_verbose = True if kwargs['verbose'] else False
        # is_verbose = True
        # if kwargs['quiet']:
        #     is_verbose = False
                
        # clear collations
        can_clear = False
        if kwargs['clear']:
            can_clear = True

        total = 0
        start = time.time()

        # collate results
        total += collate_results(use_verbose=use_verbose)

        # collate seats
        total += collate_seats(can_clear=can_clear,
                               use_verbose=use_verbose)

        end = time.time()
        print(f'Time elapsed {end - start} seconds')


        # display results
        self.stdout.write(self.style.SUCCESS(f'Collation completed! {total} total records collated.'))
