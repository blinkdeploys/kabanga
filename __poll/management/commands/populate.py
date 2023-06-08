import os, json, time, datetime
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from __poll.models import (Event, Office, Position,
                         ResultSheet, Result, ResultApproval,
                         StationCollationSheet, ConstituencyCollationSheet,
                         RegionalCollationSheet, NationalCollationSheet,
                         SupernationalCollationSheet,
                         )
from __people.models import (Agent, Party, Candidate)
from __geo.models import (Nation, Region, Constituency, Station)
from account.models import User
from faker import Faker
import random
from __poll.constants import StatusChoices, GeoLevelChoices, NameTitleChoices, TerminalColors
from __poll.utils.utils import get_zone_ct, merge_column_excludes, make_title_key, print_progress_bar
from django.db.models.signals import post_save

BAR_LENGTH=10
faker = Faker()

AVATAR_PATH = 'sql/faker/'
JSON_PATH = 'sql/poll/'
STATUS_COUNT = len(StatusChoices.choices)
ROWSTART = '| '
ENDR = '\r'

def get_datetime():
    return str(datetime.datetime.now()) \
                .replace(':', '').replace('-', '') \
                .replace(' ', '').replace('.', '')


def get_profile_photo(gender='f'):
    mode = 'female' if gender == 'f' else 'male'
    default_avatar = ''
    # open a file
    try:
        with open(f"{AVATAR_PATH}avatars.json") as json_file_content:
            # load the json
            data = json.load(json_file_content)
            images = data[mode]
            # get a random number
            n = len(images)
            pos = random.randint(0, n-1)
            # fetch the image url at the random number
            return images[pos]
    except FileNotFoundError:
        raise FileNotFoundError(f'Fixture file (avatars.json) not in folder')
    return default_avatar


def get_file_item(file_name):
    if file_name is not None:
        if type(file_name) is str:
            file_name_parts = [f for f in file_name.replace('_', ' ') \
                                .replace('.json', '') \
                                .split(' ')]
            file_name = ''
            i = 0
            for fnp in file_name_parts:
                if i > 0:
                    file_name += fnp
                i += 1
            return file_name
    return ''


def get_all_files():
    return [pos_json for pos_json in os.listdir(JSON_PATH) if pos_json.endswith('.json')]


def exclude_exising_rows(rows, queryset, query, use_verbose=False):
    codes_existing = [p.__dict__[query] for p in queryset]

    if use_verbose:
        print(f'{ROWSTART}Calculating exising records...')
    n = len(rows)
    for i in range(0, n):
        row = rows[i]
        row_code = row.get(query, '')
        if row_code in codes_existing:
            rows[i] = None

    if use_verbose:
        print(f'{ROWSTART}Excluding exising parties...')
    rows = [row for row in rows if row is not None]

    if use_verbose:
        print(f"(All)\t\t{n}")
        print(f"(Not Existing)\t{len(rows)}")
        print(f"(Existing)\t{len(codes_existing)}")
    return rows


def model_exists(model, rows):
    exists = False
    instance = None
    seeded = []
    found = 0
    if len(rows) == 1:
        row = rows[0]
        exists = model.objects.filter(title=row['title']).first()
        instance = model(
                code=row['code'],
                title=row['title'])
        return (seeded, found)
    return ([], 0)


def update_collations(result, votes,
                     supernation_totals,
                     nation_totals,
                     region_totals,
                     constituency_totals,
                     station_totals,
                     counter=True
                     ):

    party_id = result['candidate__party__id']
    zone_ct_id = result['candidate__position__zone_ct_id']
    code_prefix = merge_column_excludes([zone_ct_id, party_id])

    # total_totals += votes

    # save_station_collation_sheet
    zone_code = make_title_key(result['station__id'])
    key_code = merge_column_excludes([code_prefix, zone_code]).upper()
    if counter: 
        station_totals[key_code] = station_totals.get(key_code, 0) + votes
    else:
        collation = station_totals.get(key_code, StationCollationSheet(
                                                    station_id=result['station__id'],
                                                    zone_ct_id=result['candidate__position__zone_ct_id'],
                                                    candidate_id=result['candidate_id'],
                                                    total_votes=0,
                                                    total_invalid_votes=0,
                                                    total_votes_ec=0,
                                                ))
        collation.total_votes = collation.total_votes + votes
        station_totals[key_code] = collation

    # save_constituency_collation_sheet
    zone_code = make_title_key(result['station__constituency__id'])
    key_code = merge_column_excludes([code_prefix, zone_code]).upper()
    if counter: 
        constituency_totals[key_code] = constituency_totals.get(key_code, 0) + votes
    else:
        collation = constituency_totals.get(key_code, ConstituencyCollationSheet(
                                                party_id=result['candidate__party__id'],
                                                zone_ct_id=result['candidate__position__zone_ct_id'],
                                                station_id=result['station__id'],
                                                total_votes=0,
                                                total_invalid_votes=0,
                                                total_votes_ec=0,
                                            ))
        collation.total_votes = collation.total_votes + votes
        constituency_totals[key_code] = collation

    # save_regional_collation_sheet
    zone_code = make_title_key(result['station__constituency__region__id'])
    key_code = merge_column_excludes([code_prefix, zone_code]).upper()
    if counter: 
        region_totals[key_code] = region_totals.get(key_code, 0) + votes
    else:
        collation = region_totals.get(key_code, RegionalCollationSheet(
                                                party_id=result['candidate__party__id'],
                                                zone_ct_id=result['candidate__position__zone_ct_id'],
                                                constituency_id=result['station__constituency__id'],
                                                total_votes=0,
                                                total_invalid_votes=0,
                                                total_votes_ec=0,
                                            ))
        collation.total_votes = collation.total_votes + votes
        region_totals[key_code] = collation

    # save_national_collation_sheet
    zone_code = make_title_key(result['station__constituency__region__nation__id'])
    key_code = merge_column_excludes([code_prefix, zone_code]).upper()
    if counter: 
        nation_totals[key_code] = nation_totals.get(key_code, 0) + votes
    else:
        collation = nation_totals.get(key_code, NationalCollationSheet(
                                                party_id=result['candidate__party__id'],
                                                zone_ct_id=result['candidate__position__zone_ct_id'],
                                                region_id=result['station__constituency__region__id'],
                                                total_votes=0,
                                                total_invalid_votes=0,
                                                total_votes_ec=0,
                                            ))
        collation.total_votes = collation.total_votes + votes
        nation_totals[key_code] = collation

    # save_supernational_collation_sheet
    if counter: 
        supernation_totals[key_code] = supernation_totals.get(key_code, 0) + votes
    else:
        collation = supernation_totals.get(key_code, SupernationalCollationSheet(
                                                    party_id=result['candidate__party__id'],
                                                    zone_ct_id=result['candidate__position__zone_ct_id'],
                                                    nation_id=result['station__constituency__region__nation__id'],
                                                    total_votes=0,
                                                    total_invalid_votes=0,
                                                    total_votes_ec=0,
                                                ))
        collation.total_votes = collation.total_votes + votes
        supernation_totals[key_code] = collation




def get_model(name, rows, count=0, use_verbose=True):

    found = 0
    seeded = []
    instances = []
    imported = 0
    PROMPT_PREFIX = name[0].upper() + name[1:]
    mode = f'{TerminalColors.WARNING}ERROR{TerminalColors.ENDC}'
    userid = 0
    instance_count = 0

    
    # OK
    if name == "user":
        model = User
        # User.objects.all().delete()
        if name not in seeded:
            seeded.append(name)
        # superusers
        user, _ = User.objects.update_or_create(
            username='admin',
            email='admin@kabanga.co',
            defaults=dict(
                password='pbkdf2_sha256$260000$dpfuKn0dBPUbxkxoNjapFr$wdc/sTwmlP1J159XtWp1nYoRHlNR+IdN1MOU03+xub4=',
                is_active=True,
                is_staff=True,
                is_superuser=True,
            )
        )
        user, _ = User.objects.update_or_create(
            username='eakatue',
            email='byron4000@rocketmail.com',
            defaults=dict(
                password='pbkdf2_sha256$260000$8gjcXneYMYvyZ5ThHyWRkj$m8znsuWbrUCp6EjUuE7TN46CZ9PuoBi+7JISDHT8MMM=',
                is_active=True,
                is_staff=True,
                is_superuser=True,
            )
        )
        if use_verbose:
            print(f'{ROWSTART}{TerminalColors.OKGREEN}Superusers created successfully.{TerminalColors.ENDC}')
        # model.set_password(password)
        # instance_count = len(instances)


    '''
    # geo

    # OK
    if name == "nation":
        model = Nation
        model.objects.all().delete()
        instances = []
        excludes = [] # [merge_column_excludes([m.code]) for m in model.objects.all()]
        for row in rows:
            exclude = merge_column_excludes([row['code']])
            if exclude not in excludes:
                instances.append(model(id=row['id'],
                                code=row['code'],
                                title=row['title']))
                excludes.append(exclude)
        if len(instances) > 0:
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f'{ROWSTART}{name.capitalize()} records created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}')
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')
        instance_count = len(instances)

    # OK
    if name == "region":
        model = Region
        model.objects.all().delete()
        instances = []
        excludes = [] # [merge_column_excludes([m.title]) for m in model.objects.all()]
        for row in rows:
            exclude = merge_column_excludes([row['title']])
            if exclude not in excludes:
                instances.append(model(id=row['id'],
                                title=row['title'],
                                nation_id=1))
                excludes.append(exclude)

        if len(instances) > 0:
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f'{ROWSTART}{name.capitalize()} records created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}')
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')
        instance_count = len(instances)


    # OK
    if name == "constituency":
        model = Constituency
        model.objects.all().delete()
        instances = []
        excludes = [] # [merge_column_excludes([m.region_id, m.title]) for m in model.objects.all()]
        for row in rows:
            exclude = merge_column_excludes([row['region_id'], row['title']])
            if exclude not in excludes:
                instances.append(model(id=row['id'],
                                region_id=row['region_id'],
                                title=row['title']))
                excludes.append(exclude)
        if len(instances) > 0:
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f'{ROWSTART}{name.capitalize()} records created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}')
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error creating rows: {e}{TerminalColors.ENDC}')
        instance_count = len(instances)


    # OK
    if name == "station":
        model = Station
        model.objects.all().delete()
        instances = []
        excludes = [] # [merge_column_excludes(['C', m.constituency_id, m.code]) for m in model.objects.all()]
        constituencies = Constituency.objects.all()
        constituencies_by_title = {}
        for constituency in constituencies:
            ccode = make_title_key(constituency.title)
            constituencies_by_title[ccode] = constituency.pk

        for row in rows:
            ccode = make_title_key(row['constituency_id'])
            constituency = constituencies_by_title.get(ccode, None)
            if constituency is not None:
                exclude = merge_column_excludes(['C', constituency, row['code']])
                if exclude not in excludes:
                    instances.append(model(code=row['code'],
                                    constituency_id=int(constituency),
                                    title=row['title']))
                    excludes.append(exclude)

        if len(instances) > 0:
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f'{ROWSTART}{name.capitalize()} records created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}')
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')
        instance_count = len(instances)
    '''


    '''
    # poll

    if name == "event":
        model = Event
        Event.objects.all().delete()
        offices = Office.objects.all()
        for office in offices:
            yr = faker.year()
            mth = faker.month()
            day = faker.day()
            start = f'{day}-{mth}-{yr}'
            end = f'{day + 1}-{mth}-{yr}'
            title = f'{office.title} Elections {yr}'
            if title is not None:
                model = Event(
                            title=title,
                            details=faker.sentence(),
                            office=office,
                            start=start,
                            end=end,
                            status_id=1)
                count = count + 1
        if use_verbose:
            print(f'{count} Election events successfully created')
        instance_count = len(instances)
    '''


    '''
    # OK
    if name == "office":
        model = Office
        model.objects.all().delete()
        instances = []
        excludes = [] # [merge_column_excludes([m.title]) for m in model.objects.all()]
        for row in rows:
            exclude = merge_column_excludes([row['title']])
            if exclude not in excludes:
                instances.append(model(id=row['id'],
                                level=row['level'],
                                title=row['title']))
                excludes.append(exclude)
        if len(instances) > 0:
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f'{ROWSTART}{name.capitalize()} records created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}')
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')
        instance_count = len(instances)


    # OK
    if name == "position":
        model = Position
        model.objects.all().delete()
        instances = []

        nation_ct = get_zone_ct(Constituency)
        nations = Nation.objects.all()

        constituency_ct = get_zone_ct(Constituency)
        constituencies = Constituency.objects.all()

        row_id = 0

        excludes = [] # [merge_column_excludes(['N', m.zone.code]) for m in constituencies]
        zone_ct = nation_ct
        for zone in nations:
            exclude = merge_column_excludes([zone.code])
            if exclude not in excludes:
                row_id = row_id + 1
                title = f'President, {zone.title}'
                instances.append(model(id=row_id,
                                zone_ct=zone_ct,
                                zone=zone,
                                title=title))
                excludes.append(exclude)

        excludes = [] # [merge_column_excludes(['C', make_title_key(m.zone.title)]) for m in constituencies]
        zone_ct = constituency_ct
        for zone in constituencies:
            exclude = merge_column_excludes([make_title_key(zone.title)])
            if exclude not in excludes:
                row_id = row_id + 1
                title = f'Parliamentary Representative, {zone.title}'
                instances.append(model(id=row_id,
                                zone_ct=zone_ct,
                                zone=zone,
                                title=title))
                excludes.append(exclude)

        if len(instances) > 0:
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f'{ROWSTART}{name.capitalize()} records created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}')
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')
        instance_count = len(instances)


    # OK
    if name == "result":
        model = Result
        parent_model = ResultSheet
        use_collation_counter = False
        line_clear = '                         '
        STATION_DIVIDE = 3

        results = model.objects \
            .values(
                    'votes',
                    'candidate_id',
                    'candidate__party__id',
                    'candidate__party__code',
                    'candidate__position__zone_ct_id',
                    'station_id',
                    'station__id',
                    'station__code',
                    'station__constituency__title',
                    'station__constituency__region__title',
                    'station__constituency__region__nation__title',
                    'station__constituency__id',
                    'station__constituency__region__id',
                    'station__constituency__region__nation__id',
                  ) \
            # .annotate( n=F('m'), a=F('b') )

        supernation_totals = {}
        nation_totals = {}
        region_totals = {}
        constituency_totals = {}
        station_totals = {}
        total_totals = 0

        excludes = []
        count = 0
        total = results.count()
        for result in results:
            if result.get('station_id', None) is not None and result.get('candidate_id', None) is not None:

                votes = result['votes']
                total_totals += votes

                update_collations(result, result['votes'],
                                    supernation_totals,
                                    nation_totals,
                                    region_totals,
                                    constituency_totals,
                                    station_totals,
                                    counter=use_collation_counter)

                excludes.append(merge_column_excludes([result['station_id'], result['candidate_id']]))
                count += 1
                percent = round(100 * count / total, 2)
                if use_verbose:
                    print(f'{ROWSTART}Calculating Results (existing) \t\t{percent}%', end=ENDR)
        if use_verbose:
            print(f'{ROWSTART}Calculating Results (existing) \t{len(excludes)}')

        if use_verbose:
            print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')

        instances = []
        # parent_instances = []

        zone_models = [Nation, Constituency]

        parent_count = 0
        count = 0

            
        for zone_model in zone_models:
            zone_ct = get_zone_ct(zone_model)

            positions = Position.objects \
                                .filter(zone_ct=zone_ct) \
                                .all()

            for position in positions:
                parent_count  = 0
                count  = 0

                candidates = Candidate.objects.filter(position=position).all()

                padding = "\t"
                if zone_model.__name__.lower() == 'constituency':
                    stations = Station.objects.filter(constituency=position.zone).all()
                else:
                    stations = Station.objects.all()

                station_count = len(stations)
                third_count = (station_count / STATION_DIVIDE) - (station_count % STATION_DIVIDE)
                random_third = random.randint(1, 3)
                random_stop = int(third_count * random_third)
                random_start = int(random_stop - third_count)
                stations = stations[random_start:random_stop]

                if use_verbose:
                    print(f'{ROWSTART}{zone_model.__name__[0].upper()}-P{position.pk} {line_clear}{padding}{TerminalColors.OKGREEN}{len(instances)}{TerminalColors.ENDC}', end=ENDR)

                station_count = 0
                for station in stations:
                    parent_count += 1
                    # parent_exclude = merge_column_excludes([station.pk, position.pk])
                    # if parent_exclude not in parent_excludes:
                    parent_instance, _ = parent_model.objects.update_or_create(
                                        # id=parent_count,
                                        station=station,
                                        position=position,
                                        defaults=dict(
                                            total_votes=0,
                                            total_valid_votes=0,
                                            total_invalid_votes=random.randint(0, 50),
                                            result_sheet=None,
                                            station_agent=None,
                                            station_approval_at=None,
                                            status=StatusChoices.ACTIVE,
                                        )
                                    )
                    station_count = 0

                    # indentation: candidates will not receive votes from
                    # stations with existing result sheets
                    for candidate in candidates:
                        exclude = merge_column_excludes([station.pk, candidate.pk])
                        if exclude not in excludes:
                            count += 1
                            votes = random.randint(0, 200)
                            instance = model(
                                # id=count,
                                station=station,
                                candidate=candidate,
                                votes=votes,
                                result_sheet_id=parent_instance.pk,
                                station_agent=None,
                                status=StatusChoices.ACTIVE,
                            )
                            station_count += 1
                            parent_instance.total_valid_votes += instance.votes


                            party_code = candidate.party.code
                            total_totals += votes


                            result = dict(
                                station__id=station.pk,
                                candidate_id=candidate.pk,
                                candidate__party__id=candidate.party.pk,
                                candidate__position__zone_ct_id=candidate.position.zone_ct_id,
                                station__constituency__id=station.constituency.pk,
                                station__constituency__region__id=station.constituency.region.pk,
                                station__constituency__region__nation__id=station.constituency.region.nation.pk,
                            )

                            update_collations(result, votes,
                                                supernation_totals,
                                                nation_totals,
                                                region_totals,
                                                constituency_totals,
                                                station_totals,
                                                counter=use_collation_counter)

                            instances.append(instance)

                    if use_verbose:
                        print(f'{ROWSTART}{zone_model.__name__[0].upper()}-P{position.pk} {line_clear}{padding}{TerminalColors.OKGREEN}{len(instances)}{TerminalColors.ENDC}', end=ENDR)
                    parent_instance.total_votes = parent_instance.total_valid_votes + parent_instance.total_invalid_votes
                    parent_instance.save()
                    # parent_instances.append(parent_instance)
            if use_verbose:
                print()

        if use_verbose:
            print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')

        if len(instances) > 0:
            if use_verbose:
                print(f'{ROWSTART}Creating Results...', end=ENDR)
            try:
                model.objects.bulk_create(instances, batch_size=10000)
                if use_verbose:
                    print(f'{ROWSTART}{name.capitalize()} Records Created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}')
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')

        if not use_collation_counter:

            # print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')
            
            if len(station_totals) > 0:
                if use_verbose:
                    print('{}Collating (Station)...\t\t\t{}'.format(ROWSTART, len(station_totals.keys())), end=ENDR)
                try:
                    station_totals = [v for k, v in station_totals.items()]
                    StationCollationSheet.objects.bulk_create(station_totals, batch_size=10000)
                    if use_verbose:
                        print(f'{ROWSTART}Stations (Collated)\t\t\t{TerminalColors.OKGREEN}{len(constituency_totals)}\tOK{TerminalColors.ENDC}')
                    station_totals = {}
                except ValidationError as e:
                    if use_verbose:
                        print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')

            # print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')

            if len(constituency_totals) > 0:
                if use_verbose:
                    print('{}Collating (Constituency)...\t\t\t{}'.format(ROWSTART, len(constituency_totals.keys())), end=ENDR)
                try:
                    constituency_totals = [v for k, v in constituency_totals.items()]
                    ConstituencyCollationSheet.objects.bulk_create(constituency_totals, batch_size=10000)
                    if use_verbose:
                        print(f'{ROWSTART}Constituencies (Collated)\t\t{TerminalColors.OKGREEN}{len(constituency_totals)}\tOK{TerminalColors.ENDC}')
                    constituency_totals = {}
                except ValidationError as e:
                    if use_verbose:
                        print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')

            # print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')
            
            if len(region_totals) > 0:
                if use_verbose:
                    print('{}Collating (Region)...\t\t\t{}'.format(ROWSTART, len(region_totals.keys())), end=ENDR)
                try:
                    region_totals = [v for k, v in region_totals.items()]
                    RegionalCollationSheet.objects.bulk_create(region_totals, batch_size=10000)
                    if use_verbose:
                        print(f'{ROWSTART}Regions (Collated) \t\t\t{TerminalColors.OKGREEN}{len(region_totals)}\tOK{TerminalColors.ENDC}')
                    region_totals = {}
                except ValidationError as e:
                    if use_verbose:
                        print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')

            # print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')
            
            if len(nation_totals) > 0:
                if use_verbose:
                    print('{}Collating (Nation)...\t\t\t{}'.format(ROWSTART, len(nation_totals.keys())), end=ENDR)
                try:
                    nation_totals = [v for k, v in nation_totals.items()]
                    NationalCollationSheet.objects.bulk_create(nation_totals, batch_size=10000)
                    if use_verbose:
                        print(f'{ROWSTART}Nations (Collated) \t\t\t{TerminalColors.OKGREEN}{len(nation_totals)}\tOK{TerminalColors.ENDC}')
                    nation_totals = {}
                except ValidationError as e:
                    if use_verbose:
                        print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')

            # print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')

            if len(supernation_totals) > 0:
                if use_verbose:
                    print('{}Collating (Supernational)...\t\t\t{}'.format(ROWSTART, len(supernation_totals.keys())), end=ENDR)
                try:
                    supernation_totals = [v for k, v in supernation_totals.items()]
                    SupernationalCollationSheet.objects.bulk_create(supernation_totals, batch_size=10000)
                    if use_verbose:
                        print(f'{ROWSTART}Supernationals (Collated) \t\t{TerminalColors.OKGREEN}{len(supernation_totals)}\tOK{TerminalColors.ENDC}')
                    supernation_totals = {}
                except ValidationError as e:
                    if use_verbose:
                        print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')

        if use_verbose:
            print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')

        # clear arrays in an attempt to reset memory
        # parent_instances = []
        nation_totals = {}
        region_totals = {}
        constituency_totals = {}
        station_totals = {}
        instance_count = len(instances)
        instances = []



    # people

    # OK
    if name == "party":
        model = Party
        model.objects.all().delete()
        instances = []
        excludes = [] # [merge_column_excludes([m.code]) for m in model.objects.all()]
        for row in rows:
            exclude = merge_column_excludes([row['code']])
            if exclude not in excludes:
                instances.append(model(id=row['id'],
                                code=row['code'],
                                title=row['title']))
                excludes.append(exclude)
        if len(instances) > 0:
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f'{ROWSTART}{name.capitalize()} records created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}')
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error: {e}{TerminalColors.ENDC}')
        instance_count = len(instances)


    # OK
    if name == "agent":
        model = Agent
        model.objects.all().delete()
        instances = []
        zone_models = [Nation, Region, Constituency, Station]

        user_insert_instances = []
        user_update_instances = []

        row_id = 0
        excludes = [] # [merge_column_excludes([m.zone.code]) for m in constituencies]

        i = 0
        agent_ct = get_zone_ct(Agent)

        if use_verbose:
            print(f'{ROWSTART}Calculating existing user records', end=ENDR)
        user_agent_codes = {}
        for u in User.objects.all():
            ucode = merge_column_excludes([u.role_ct_id, u.role_id])
            user_agent_codes[ucode] = u.pk

        for zone_model in zone_models:
            zone_ct = get_zone_ct(zone_model)
            if use_verbose:
                print(f'{ROWSTART}Calculating {zone_model.__name__} records...', end=ENDR)

            zone_count = 0
            zone_user_insert_count = 0
            zone_user_update_count = 0

            for zone in zone_model.objects.all():

                zone_key = zone.title
                if zone_model.__name__ in ['nation', 'station']:
                    zone_key = zone.code

                exclude = merge_column_excludes([make_title_key(zone_key)])
                if exclude not in excludes:

                    row_id = row_id + 1
                    zone_count = zone_count + 1
                    email = faker.email().replace('@', f'{str(row_id)}@')
                    first_name = faker.first_name()
                    last_name = faker.last_name()

                    instances.append(model(id=row_id,
                                            zone_ct=zone_ct,
                                            zone=zone,
                                            first_name=first_name,
                                            last_name=last_name,
                                            email=email,
                                            phone=faker.phone_number(),
                                            address=faker.address(),
                                            description=faker.sentence(),
                                            status=StatusChoices.ACTIVE
                    ))
                    excludes.append(exclude)

                    password = 'pbkdf2_sha256$260000$dpfuKn0dBPUbxkxoNjapFr$wdc/sTwmlP1J159XtWp1nYoRHlNR+IdN1MOU03+xub4='
                    username = f'{first_name[0].lower()}{last_name.lower()}.{get_datetime()}'
                    user_instance = User(role_ct=agent_ct, role_id=row_id, email=email,
                                        username=username, password=password,
                                        first_name=first_name, last_name=last_name,
                                        is_active=True, is_staff=True, is_superuser=False)
                    user_agent_code = merge_column_excludes([agent_ct.pk, row_id])
                    if user_agent_code in user_agent_codes.keys():
                        user_instance.id = user_agent_codes[user_agent_code]
                        user_update_instances.append(user_instance)
                        zone_user_update_count += 1
                    else:
                        user_insert_instances.append(user_instance)
                        zone_user_insert_count += 1


            if use_verbose:
                print(f'{ROWSTART}{zone_model.__name__} {name.capitalize()}s:                                       ')
            if zone_count > 0:
                if use_verbose:
                    print(f"{ROWSTART}Records added \t\t\t{TerminalColors.OKGREEN}{zone_count}{TerminalColors.ENDC}")
            if len(user_insert_instances) > 0:
                if use_verbose:
                    print(f"{ROWSTART}User records inserted \t\t\t{TerminalColors.OKGREEN}{zone_user_insert_count}{TerminalColors.ENDC}")
            if len(user_update_instances) > 0:
                if use_verbose:
                    print(f"{ROWSTART}User records updated \t\t\t{TerminalColors.OKGREEN}{zone_user_update_count}{TerminalColors.ENDC}")
            if use_verbose:
                print('+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +')
            

        if len(instances) > 0:
            if use_verbose:
                print(f'{ROWSTART}Creating {name.capitalize()} records', end=ENDR)
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f"{ROWSTART}{name.capitalize()}s created \t\t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}")
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error creating {name} records {e}{TerminalColors.ENDC}')

        if len(user_insert_instances) > 0:
            if use_verbose:
                print(f'{ROWSTART}Creating {len(user_insert_instances)} User records...', end=ENDR)
            try:
                User.objects.bulk_create(user_insert_instances)
                if use_verbose:
                    print(f"{ROWSTART}Users created \t\t\t{TerminalColors.OKGREEN}{len(user_insert_instances)}\tOK{TerminalColors.ENDC}")
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error upserting users {e}{TerminalColors.ENDC}')
        
        if len(user_update_instances) > 0:
            if use_verbose:
                print(f'{ROWSTART}Updating {len(user_update_instances)} User records...', end=ENDR)
            try:
                User.objects.bulk_update(user_update_instances,
                                        fields=['role_ct', 'role_id', 'email',
                                                'username', 'password', 'first_name', 'last_name',
                                                'is_active', 'is_staff', 'is_superuser'],
                                        batch_size=1000)
                if use_verbose:
                    print(f"{ROWSTART}Users updated \t\t\t{TerminalColors.OKGREEN}{len(user_update_instances)}\tOK{TerminalColors.ENDC}")
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.WARNING}Error upserting users {e}{TerminalColors.ENDC}')
        # print(f'-------------------------------------------------')
        instance_count = len(instances)


    # OK
    if name == "candidate":
        model = Candidate
        model.objects.all().delete()
        instances = []
        excludes = [] # [merge_column_excludes([m.party.pk, m.position.pk]) for m in model.objects.all()]
        positions = Position.objects.all()
        parties = Party.objects.all()
        for position in positions:
            for party in parties:
                exclude = merge_column_excludes([party.code, position.pk])
                if exclude not in excludes:
                    ismof = random.randint(0, 1)
                    email = faker.email().replace('@', f'_{str(userid)}@')
                    photo = get_profile_photo('m')
                    prefix = faker.prefix_male()
                    first_name = faker.first_name_male()
                    if ismof == 0:
                        photo = get_profile_photo('f')
                        prefix = faker.prefix_female()
                        first_name = faker.first_name_female()
                    last_name = faker.last_name()
                    instances.append(model(
                            photo=photo,
                            prefix=prefix,
                            first_name=first_name,
                            last_name=last_name,
                            other_names=faker.first_name(),
                            description=faker.sentence(),
                            party=party,
                            position=position,
                            status=StatusChoices.ACTIVE
                    ))
                    excludes.append(exclude)

        if len(instances) > 0:
            try:
                model.objects.bulk_create(instances)
                if use_verbose:
                    print(f"{ROWSTART}{name.capitalize()} records created \t\t{TerminalColors.OKGREEN}{len(instances)}\tOK{TerminalColors.ENDC}")
            except ValidationError as e:
                if use_verbose:
                    print(f'{ROWSTART}{TerminalColors.FAIL}Error: {e}{TerminalColors.ENDC}')
        instance_count = len(instances)
    '''


    if instance_count <= 0 and name is not None:
        if use_verbose:
            print(f'{ROWSTART}{TerminalColors.WARNING}{name.capitalize()} No data imported \t\t0{TerminalColors.ENDC}')




class Command(BaseCommand):
    '''
    Import data from a JSON file into a Listings table
    python manage.py import_json_data.
    '''
    help = 'Import data from a JSON file into a Listings table'

    def add_arguments(self, parser):
        parser.add_argument('--clear',
                            action='store_true',
                            help='clear all exisitng collations')
        parser.add_argument('--verbose',
                            action='store_true',
                            help='verbose reporting')
        parser.add_argument('-modes', '--modes',
                            type=str, nargs='+',
                            help=f"The type of models to populate.\r\n    [system]=System models, these models comprise the core essential data for the application.\r\n    [placeholder]=Placeholder models, these data models are created once with placeholder data and can be replaced with actual data for production.\n  [seed]=Seed models, these models are required for demonstrations purposes and will not be included in a fresh install.")
        parser.add_argument('-models', '--models',
                            type=str, nargs='+',
                            help='The model to populate. If empty, all models will be populated')
        # parser.add_argument('-verbose', '--verbose', type=int, nargs='+', help='Run the population showing each line from the scripts')

    def handle(self, *args, **kwargs):
        start_time = time.time()

        models_to_use = kwargs['models']
        use_single_model = False
        if models_to_use is not None:
            use_single_model = len(models_to_use) > 0
            models_to_use = models_to_use.split(' ')

        # noisy or quiet
        use_verbose = True if kwargs['verbose'] else False

        json_files = get_all_files()
        found_tables = []
        seeded = []
        
        for json_file in sorted(json_files):
            if use_verbose:
                print('--------------------------------------------------------------')
                print(f'{ROWSTART}Processing {get_file_item(json_file)}...'.upper(), end=ENDR)
            else:
                print(f'{ROWSTART}Processing {get_file_item(json_file)}...'.upper())
            try:
                with open(f"{JSON_PATH}{json_file}") as json_file_content:
                    data = json.load(json_file_content)
                    if use_single_model is False or (use_single_model is True and data["data"][0] in models_to_use):
                        get_model(data["name"], data["data"], use_verbose=use_verbose)
            except FileNotFoundError:
                raise FileNotFoundError(f'Fixture file {json_file} not in folder')
        if use_verbose:
            print('--------------------------------------------------------------')

        self.stdout.write(self.style.SUCCESS(f'Done: {len(json_files)} total tables checked, {len(found_tables)} tables found, {len(seeded)} tables seeded'))
        stop_time = time.time()
        self.stdout.write(self.style.SUCCESS(f'Time elapsed: {stop_time - start_time} seconds'))
