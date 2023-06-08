import time
from poll.utils.utils import intify
from poll.models import (Position, Result, ResultSheet, SupernationalCollationSheet,
                         NationalCollationSheet, RegionalCollationSheet,
                         ConstituencyCollationSheet, StationCollationSheet,
                         ParliamentarySummarySheet)
from people.models import Candidate
from geo.models import Nation, Region, Constituency, Station
from poll.constants import TerminalColors
from django.db import connection
from poll.utils.utils import get_zone_ct, merge_column_excludes, make_title_key
from django.core.exceptions import ValidationError


ROWSTART = ''

def clear_collated_results():
    supernation_collations = SupernationalCollationSheet.objects.all()
    nation_collations = NationalCollationSheet.objects.all()
    region_collations = RegionalCollationSheet.objects.all()
    constituency_collations = ConstituencyCollationSheet.objects.all()
    station_collations = StationCollationSheet.objects.all()
    total_records = nation_collations.count() \
                    + region_collations.count() \
                    + constituency_collations.count() \
                    + station_collations.count() \
                    + supernation_collations.count()
    # clear_all = input(f'You are about to clear {total_records} collation records, do you want to proceed? Y/N: ')
    # clear_all = f'{clear_all.lower()}'
    # if clear_all in ['y', 'yes']:
    supernation_collations.delete()
    nation_collations.delete()
    region_collations.delete()
    constituency_collations.delete()
    station_collations.delete()
    return total_records


def get_collation_sheet_exclude_key(result, model, fields=[]):
    if model.__name__ == 'StationCollationSheet':
        if len(fields) <= 0:
            fields = ['station_id', 'zone_ct_id', 'candidate_id']
    elif model.__name__ == 'ConstituencyCollationSheet':
        if len(fields) <= 0:
            fields = ['party_id', 'zone_ct_id', 'station_id']
    elif model.__name__ == 'RegionalCollationSheet':
        if len(fields) <= 0:
            fields = ['party_id', 'zone_ct_id', 'constituency_id']
    elif model.__name__ == 'NationalCollationSheet':
        if len(fields) <= 0:
            fields = ['party_id', 'zone_ct_id', 'region_id']
    elif model.__name__ == 'SupernationalCollationSheet':
        if len(fields) <= 0:
            fields = ['party_id', 'zone_ct_id', 'nation_id']
    else:
        fields = []

    if len(fields) > 0:
        return merge_column_excludes([
                                        make_title_key(result[fields[0]]),
                                        make_title_key(result[fields[1]]),
                                        make_title_key(result[fields[2]]),
                                    ]).upper()
    else:
        return None


def update_single_collation(result,
                     collation_collection,
                     pk=None,
                     model=None,
                     counter=True
                     ):

    party_id = result['candidate__party__id']
    zone_ct_id = result['candidate__position__zone_ct_id']
    code_prefix = merge_column_excludes([zone_ct_id, party_id])

    # total_totals += votes
    votes = result['votes'] or 0
    # total_invalid_votes = result['result_sheet__total_invalid_votes'] or 0
    instance = None
    key_code = None


    if model.__name__ == 'StationCollationSheet':
        # save_station_collation_sheet
        key_code = get_collation_sheet_exclude_key(result, model, ['station__id',
                                                                    'candidate__position__zone_ct_id',
                                                                    'candidate_id',])
        if not counter: 
            instance = model(
                            station_id=result['station__id'],
                            zone_ct_id=result['candidate__position__zone_ct_id'],
                            candidate_id=result['candidate_id'],
                            total_votes=0,
                            total_invalid_votes=0,
                            total_votes_ec=0,
                        )
    elif model.__name__ == 'ConstituencyCollationSheet':
        # save_constituency_collation_sheet
        key_code = get_collation_sheet_exclude_key(result, model, ['candidate__party__id',
                                                                    'candidate__position__zone_ct_id',
                                                                    'station__id',])
        if not counter: 
            instance = model(
                            party_id=result['candidate__party__id'],
                            zone_ct_id=result['candidate__position__zone_ct_id'],
                            station_id=result['station__id'],
                            total_votes=0,
                            total_invalid_votes=0,
                            total_votes_ec=0,
                        )
    elif model.__name__ == 'RegionalCollationSheet':
        # save_regional_collation_sheet
        key_code = get_collation_sheet_exclude_key(result, model, ['candidate__party__id',
                                                                    'candidate__position__zone_ct_id',
                                                                    'station__constituency__id',])
        if counter: 
            collation_collection[key_code] = collation_collection.get(key_code, 0) + votes
        else:
            instance = model(
                            party_id=result['candidate__party__id'],
                            zone_ct_id=result['candidate__position__zone_ct_id'],
                            constituency_id=result['station__constituency__id'],
                            total_votes=0,
                            total_invalid_votes=0,
                            total_votes_ec=0,
                        )
    elif model.__name__ == 'NationalCollationSheet':
        # save_national_collation_sheet
        key_code = get_collation_sheet_exclude_key(result, model, ['candidate__party__id',
                                                                    'candidate__position__zone_ct_id',
                                                                    'station__constituency__region__id',])
        if not counter: 
            instance = model(
                            party_id=result['candidate__party__id'],
                            zone_ct_id=result['candidate__position__zone_ct_id'],
                            region_id=result['station__constituency__region__id'],
                            total_votes=0,
                            total_invalid_votes=0,
                            total_votes_ec=0,
                        )
    elif model.__name__ == 'SupernationalCollationSheet':
        # save_supernational_collation_sheet
        key_code = get_collation_sheet_exclude_key(result, model, ['candidate__party__id',
                                                                    'candidate__position__zone_ct_id',
                                                                    'station__constituency__region__nation__id',])
        if not counter: 
            instance = model(
                            party_id=result['candidate__party__id'],
                            zone_ct_id=result['candidate__position__zone_ct_id'],
                            nation_id=result['station__constituency__region__nation__id'],
                            total_votes=0,
                            total_invalid_votes=0,
                            total_votes_ec=0,
                        )
    else:
        pass

    if key_code:
        if counter: 
            collation_collection[key_code] = collation_collection.get(key_code, 0) + votes
        else:
            if instance:
                if pk is not None:
                    instance.id = pk
                collation = collation_collection.get(key_code, instance)
                collation.total_votes = collation.total_votes + votes
                '''
                if model.__name__ == 'StationCollationSheet':
                    # StationCS maintains the same invalid votes from the result sheet
                    collation.total_invalid_votes = total_invalid_votes
                else:
                    # collate from lower levels
                    # factor is the number of child zones ie for a constituency with 12 stations, factor = 12
                    collation.total_invalid_votes = collation.total_invalid_votes + (total_invalid_votes / factor)
                '''
                collation_collection[key_code] = collation

    return collation_collection


def bulk_upsert_collation(collation_totals,
                          collation_model,
                          collation_type,
                          collation_mode,
                          fields=[],
                          batch_size=2000,
                          use_verbose=False,
                          ):

    padding = '' if collation_type.lower()[0] == 'c' else '\t'
    # collation_totals = list(collation_totals.values())
    total = len(collation_totals)
    if total > 0:
        if use_verbose:
            print('{}ing ({})...\t\t\t{}'.format(collation_mode.capitalize(), collation_type, total), end="\r")
        try:
            count = 0
            stop = 0
            while total > 0:
                stop = batch_size if total >= batch_size else total
                collations = collation_totals[0:stop]
                if collation_mode[0].lower() == 'c':
                    collation_model.objects \
                                    .bulk_create(collations)
                else:
                    collation_model.objects \
                                    .bulk_update(collations, fields=fields)
                del collation_totals[0:stop]
                total = len(collation_totals)
                count += stop
                if use_verbose:
                    print(f'{collation_type} ({collation_mode.capitalize()}ed)\t\t{padding}{TerminalColors.OKGREEN}{count}\tOK{TerminalColors.ENDC}', end="\r")
            collation_totals = {}
            if use_verbose:
                print()
        except ValidationError as e:
            if use_verbose:
                print(f'{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')


def collate_results(use_verbose=False):
    # fetch all results, and prune only the required
    # rows to save on memory and processing

    DEBUG_GATE = False
    total_tables = 0

    results = Result.objects \
                    .values(
                        'votes',
                        'candidate_id',
                        'candidate__party__id',
                        'candidate__party__code',
                        'candidate__position__zone_ct_id',
                        'station_id',
                        'station__id',
                        'station__code',
                        'station__constituency__id',
                        'station__constituency__title',
                        'station__constituency__region__id',
                        'station__constituency__region__title',
                        'station__constituency__region__nation__id',
                        'station__constituency__region__nation__title',
                        # 'result_sheet__total_invalid_votes',
                    ) \
                    # .annotate( n=F('m'), a=F('b') )
    print(f'{ROWSTART}Collating Results... \t\t\t')
    if use_verbose:
        print('+----------------------------------------------------------+')

    if use_verbose:
        print(f'{ROWSTART}Deleting Collations... \t\t\t%', end='\r')
    SupernationalCollationSheet.objects.all().delete()
    NationalCollationSheet.objects.all().delete()
    RegionalCollationSheet.objects.all().delete()
    ConstituencyCollationSheet.objects.all().delete()
    StationCollationSheet.objects.all().delete()
    if use_verbose:
        print(f'{ROWSTART}Deleting Collations... \t\t\t{TerminalColors.OKBLUE}{ROWSTART}OK{TerminalColors.ENDC}')


    supernation_excludes = {}
    nation_excludes = {}
    region_excludes = {}
    constituency_excludes = {}
    station_excludes = {}

    '''
    station_excludes = {
                            get_collation_sheet_exclude_key(r, StationCollationSheet): r['id']
                            for r in StationCollationSheet.objects \
                                                        .values('id', 'station_id', 'zone_ct_id', 'candidate_id')
                        }
    constituency_excludes = {
                                get_collation_sheet_exclude_key(r, ConstituencyCollationSheet): r['id']
                                for r in ConstituencyCollationSheet.objects \
                                                            .values('id', 'party_id', 'zone_ct_id', 'station_id')
                            }
    region_excludes = {
                        get_collation_sheet_exclude_key(r, RegionalCollationSheet): r['id']
                         for r in RegionalCollationSheet.objects \
                                                        .values('id', 'party_id', 'zone_ct_id', 'constituency_id')
                    }
    nation_excludes = {
                        get_collation_sheet_exclude_key(r, NationalCollationSheet): r['id']
                        for r in NationalCollationSheet.objects \
                                                        .values('id', 'party_id', 'zone_ct_id', 'region_id')
                        }
    supernation_excludes = {
                                get_collation_sheet_exclude_key(r, SupernationalCollationSheet): r['id']
                                for r in SupernationalCollationSheet.objects \
                                                                .values('id', 'party_id', 'zone_ct_id', 'nation_id')
                            }
    '''


    supernation_create_totals = {}
    nation_create_totals = {}
    region_create_totals = {}
    constituency_create_totals = {}
    station_create_totals = {}

    supernation_update_totals = {}
    nation_update_totals = {}
    region_update_totals = {}
    constituency_update_totals = {}
    station_update_totals = {}


    total_totals = 0
    UPDATE_MODE = 'updat'
    CREATE_MODE = 'creat'

    return_collation_counter = False

    count = 0
    total = results.count()


    for result in results:
        if result.get('station_id', None) is not None \
            and result.get('candidate_id', None) is not None:

            total_totals += result['votes']

            if DEBUG_GATE:
                pass

            station_exclude = get_collation_sheet_exclude_key(result,
                                                            StationCollationSheet,
                                                            ['station__id',
                                                                'candidate__position__zone_ct_id',
                                                                'candidate_id',])
            if station_exclude in station_excludes.keys():
                station_update_totals = update_single_collation(result,
                                            station_update_totals,
                                            pk=station_excludes[station_exclude],
                                            model=StationCollationSheet,
                                            counter=return_collation_counter)
            else:
                station_create_totals = update_single_collation(result,
                                            station_create_totals,
                                            model=StationCollationSheet,
                                            counter=return_collation_counter)


            constituency_exclude = get_collation_sheet_exclude_key(result,
                                                                ConstituencyCollationSheet,
                                                                ['candidate__party__id',
                                                                    'candidate__position__zone_ct_id',
                                                                    'station__id',])
            if constituency_exclude in constituency_excludes.keys():
                constituency_update_totals = update_single_collation(result,
                                                constituency_update_totals,
                                                pk=constituency_excludes[constituency_exclude],
                                                model=ConstituencyCollationSheet,
                                                counter=return_collation_counter)
            else:
                constituency_create_totals = update_single_collation(result,
                                                constituency_create_totals,
                                                model=ConstituencyCollationSheet,
                                                counter=return_collation_counter)


            region_exclude = get_collation_sheet_exclude_key(result,
                                                            RegionalCollationSheet,
                                                            ['candidate__party__id',
                                                                'candidate__position__zone_ct_id',
                                                                'station__constituency__id',])
            if region_exclude in region_excludes.keys():
                region_update_totals = update_single_collation(result,
                                        region_update_totals,
                                        pk=region_excludes[region_exclude],
                                        model=RegionalCollationSheet,
                                        counter=return_collation_counter)
            else:
                region_create_totals = update_single_collation(result,
                                        region_create_totals,
                                        model=RegionalCollationSheet,
                                        counter=return_collation_counter)


            nation_exclude = get_collation_sheet_exclude_key(result,
                                                            NationalCollationSheet,
                                                            ['candidate__party__id',
                                                                'candidate__position__zone_ct_id',
                                                                'station__constituency__region__id',])
            if nation_exclude in nation_excludes.keys():
                nation_update_totals = update_single_collation(result,
                                        nation_update_totals,
                                        pk=nation_excludes[nation_exclude],
                                        model=NationalCollationSheet,
                                        counter=return_collation_counter)
            else:
                nation_create_totals = update_single_collation(result,
                                        nation_create_totals,
                                        model=NationalCollationSheet,
                                        counter=return_collation_counter)

            supernation_exclude = get_collation_sheet_exclude_key(result,
                                                                  SupernationalCollationSheet,
                                                                  ['candidate__party__id',
                                                                    'candidate__position__zone_ct_id',
                                                                    'station__constituency__region__nation__id',])
            if supernation_exclude in supernation_excludes.keys():
                supernation_update_totals = update_single_collation(result,
                                            supernation_update_totals,
                                            pk=supernation_excludes[supernation_exclude],
                                            model=SupernationalCollationSheet,
                                            counter=return_collation_counter)
            else:
                supernation_create_totals = update_single_collation(result,
                                            supernation_create_totals,
                                            model=SupernationalCollationSheet,
                                            counter=return_collation_counter)

            count += 1
            percent = round(100 * count / total, 2)
            if use_verbose:
                print(f'{ROWSTART}Counting Result Votes \t\t\t{percent}%', end='\r')
    if use_verbose:
        print()



    supernation_update_totals = list(supernation_update_totals.values())
    nation_update_totals = list(nation_update_totals.values())
    region_update_totals = list(region_update_totals.values())
    constituency_update_totals = list(constituency_update_totals.values())
    station_update_totals = list(station_update_totals.values())

    supernation_create_totals = list(supernation_create_totals.values())
    nation_create_totals = list(nation_create_totals.values())
    region_create_totals = list(region_create_totals.values())
    constituency_create_totals = list(constituency_create_totals.values())
    station_create_totals = list(station_create_totals.values())


    if use_verbose:
        print('+----------------------------------------------------------+')
        print(f'Total Vote Count: \t\t\t{total_totals}')
        # print('+----------------------------------------------------------+')
        # print(f'{ROWSTART}Collation (Excludes): ')
        # print(f'{ROWSTART}  Supernational \t\t\t{len(supernation_excludes.keys())}')
        # print(f'{ROWSTART}  National \t\t\t\t{len(nation_excludes.keys())}')
        # print(f'{ROWSTART}  Regional \t\t\t\t{len(region_excludes.keys())}')
        # print(f'{ROWSTART}  Constituency  \t\t\t{len(constituency_excludes.keys())}')
        # print(f'{ROWSTART}  Station \t\t\t\t{len(station_excludes.keys())}')
        # print('+----------------------------------------------------------+')
        # print(f'{ROWSTART}Collation (Updates): ')
        # print(f'{ROWSTART}  Supernational \t\t\t{len(supernation_update_totals)}')
        # print(f'{ROWSTART}  National \t\t\t\t{len(nation_update_totals)}')
        # print(f'{ROWSTART}  Regional \t\t\t\t{len(region_update_totals)}')
        # print(f'{ROWSTART}  Constituency  \t\t\t{len(constituency_update_totals)}')
        # print(f'{ROWSTART}  Station \t\t\t\t{len(station_update_totals)}')
        print('+----------------------------------------------------------+')
        print(f'{ROWSTART}Collation (Creates): ')
        print(f'{ROWSTART}  Station \t\t\t\t{len(station_create_totals)}')
        print(f'{ROWSTART}  Constituency  \t\t\t{len(constituency_create_totals)}')
        print(f'{ROWSTART}  Regional \t\t\t\t{len(region_create_totals)}')
        print(f'{ROWSTART}  National \t\t\t\t{len(nation_create_totals)}')
        print(f'{ROWSTART}  Supernational \t\t\t{len(supernation_create_totals)}')
        print('+----------------------------------------------------------+')
        # print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')

    # caluclate number of tables collated
    for item in [
        len(supernation_create_totals),
        len(nation_create_totals),
        len(constituency_create_totals),
        len(region_create_totals),
    ]:
        if item > 0:
            total_tables += 1

    batch_size = 500
    supernation_excludes = {}
    nation_excludes = {}
    region_excludes = {}
    constituency_excludes = {}
    station_excludes = {}

    batch_size = 2000

    if not return_collation_counter:

        if DEBUG_GATE:
            pass

        collation_type = 'Stations'
        collation_model = StationCollationSheet
        
        collation_mode = UPDATE_MODE
        collation_totals = station_update_totals
        station_update_totals = {}
        fields=[
                'station_id',
                'zone_ct_id',
                'candidate_id',
                'total_votes',
                'total_invalid_votes',
                'total_votes_ec',
        ]
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )

        collation_mode = CREATE_MODE
        collation_totals = station_create_totals
        station_create_totals = {}
        fields = []
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )


        collation_type = 'Constituencies'
        collation_model = ConstituencyCollationSheet
        
        collation_mode = UPDATE_MODE
        collation_totals = constituency_update_totals
        constituency_update_totals = {}
        fields=[
                'party_id',
                'zone_ct_id',
                'station_id',
                'total_votes',
                'total_invalid_votes',
                'total_votes_ec',
        ]
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )

        collation_mode = CREATE_MODE
        collation_totals = constituency_create_totals
        constituency_create_totals = {}
        fields = []
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )


        collation_type = 'Regions'
        collation_model = RegionalCollationSheet
        
        collation_mode = UPDATE_MODE
        collation_totals = region_update_totals
        region_update_totals = {}
        fields=[
                'party_id',
                'zone_ct_id',
                'constituency_id',
                'total_votes',
                'total_invalid_votes',
                'total_votes_ec',
        ]
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )

        collation_mode = CREATE_MODE
        collation_totals = region_create_totals
        region_create_totals = {}
        fields = []
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )


        collation_type = 'Nations'
        collation_model = NationalCollationSheet
        
        collation_mode = UPDATE_MODE
        collation_totals = nation_update_totals
        nation_update_totals = {}
        fields=[
                'party_id',
                'zone_ct_id',
                'region_id',
                'total_votes',
                'total_invalid_votes',
                'total_votes_ec',
        ]
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )
        
        collation_mode = CREATE_MODE
        collation_totals = nation_create_totals
        nation_create_totals = {}
        fields = []
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )


        collation_type = 'Supernations'
        collation_model = SupernationalCollationSheet
        
        collation_mode = UPDATE_MODE
        collation_totals = supernation_update_totals
        supernation_update_totals = {}
        fields=[
                'party_id',
                'zone_ct_id',
                'nation_id',
                'total_votes',
                'total_invalid_votes',
                'total_votes_ec',
        ]
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )
        
        collation_mode = CREATE_MODE
        collation_totals = supernation_create_totals
        supernation_create_totals = {}
        fields = []
        bulk_upsert_collation(collation_totals,
                        collation_model=collation_model,
                        collation_type=collation_type,
                        collation_mode=collation_mode,
                        fields=fields,
                        use_verbose=use_verbose
                        )
    if use_verbose:
        print('+----------------------------------------------------------+')
    print(f'{ROWSTART}Result Collation Complete\t\t\t%')

    return total_tables


def collate_seats(can_clear=True, use_verbose=False):
    print('Collating Seats...')
    total = 0
    # percollate all seats per candidate per station
    total_seats = Constituency.objects.count()
    total_seats_won = 0
    total_seats_declared = 0
    total_seats_outstanding = 0
    total_votes = 0
    sheets = dict()
    ParliamentarySummarySheet.objects.all().delete()
    zone_ct = get_zone_ct(Constituency)
    # get all candates with results
    candidates_with_results = [r.candidate_id for r in Result.objects.all()]
    # get all parliamentary positons
    parliamentary_positions = Position.objects.filter(zone_ct=zone_ct).all()
    # get all the canididates for parliamentary positons
    parliamentary_candidates = Candidate.objects \
                                        .filter(
                                            pk__in=candidates_with_results,
                                            position__in=parliamentary_positions,
                                        ).all()
    max_sheets = dict()
    for candidate in parliamentary_candidates:
        position_id = candidate.position.pk
        # get the sheet for the position the candidate is vieing for
        max_sheet = max_sheets.get(position_id, dict())
        # find the vote for the winning candidate
        max_votes = max_sheet.get('votes', 0)
        # find the winning candidate for the position
        max_candidate = max_sheet.get('candidate', None)
        # get the total votes for this position
        total_votes = max_sheet.get('total_votes', 0)
        # sum the votes for current candidate from all stations
        votes = sum([r.votes for r in candidate.results.all()])
        # add total votes
        total_votes += votes
        # find the max votes and winning candidate
        if max_votes < votes:
            max_votes = votes
            max_candidate = candidate
            max_sheet['votes'] = max_votes
            max_sheet['candidate'] = max_candidate
        # put the max sheet back into the pile with the total votes
        if total_votes > 0:
            max_sheet['total_votes'] = total_votes
            max_sheets[position_id] = max_sheet
            # print(position_id, max_sheet)
    # crate new records
    for position_id, sheet in max_sheets.items():
        candidate = sheet['candidate']
        constituency_id = candidate.position.zone_id
        votes = sheet['votes']
        total_votes = sheet['total_votes']

        constituency = Constituency.objects.filter(pk=constituency_id).first()
        position = Position.objects.filter(pk=position_id).first()

        s, _ = ParliamentarySummarySheet.objects \
                                        .update_or_create(
                                            position=position,
                                            defaults=dict(
                                                candidate=candidate,
                                                constituency=constituency,
                                                votes=votes,
                                                total_votes=total_votes,
                                            )
                                        )
        if use_verbose:
            print('+----------------------------------------------------------+')
        total_seats_declared += 1
        if use_verbose:
            # print(f'Position: \t\t\t{TerminalColors.OKBLUE}{position}{TerminalColors.ENDC}')
            print(f'Candidate \t{TerminalColors.OKBLUE}{candidate} ({candidate.party.code}){TerminalColors.ENDC}')
            print(f'Constituency: \t{TerminalColors.OKBLUE}{constituency}{TerminalColors.ENDC}')
            print(f'Votes: \t\t{TerminalColors.OKBLUE}{votes}{TerminalColors.ENDC}')
        if candidate.party.code == 'NDC':
            if use_verbose:
                print(f'NDC Won: \t\t{TerminalColors.OKBLUE}YES{TerminalColors.ENDC}')
            total_seats_won += 1
    total_seats_outstanding = total_seats - total_seats_declared
    total += ParliamentarySummarySheet.objects.all().count()
    if use_verbose:
        print('+----------------------------------------------------------+')
        print(f'Total Seats Won: \t\t{TerminalColors.OKBLUE}{total_seats_won}{TerminalColors.ENDC}')
        print(f'Total Seats Declared: \t\t{TerminalColors.OKBLUE}{total_seats_declared}{TerminalColors.ENDC}')
        print(f'Total Seats Outstanding: \t{TerminalColors.OKBLUE}{total_seats_outstanding}{TerminalColors.ENDC}')
        print(f'Total Votes: \t\t\t{TerminalColors.OKBLUE}{total_votes}{TerminalColors.ENDC}')
        print('+----------------------------------------------------------+')
    print('Seats Collating... \t\t\tDONE')
    return total
