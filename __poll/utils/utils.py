import os
import sys
import uuid
import random
import json
from datetime import datetime 
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.contenttypes.models import ContentType
from typing import Optional
from __poll.constants import TerminalColors
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect


def intify(value) -> int:
    if type(value) is int:
        value = value
    elif type(value) is str:
        value = int(value)
    else:
        value = 0
    return value

def snakeify(title, remove_special=True):
    if type(title) is str:
        title = title.lower().replace(' ', '_').replace('.', '')
        if remove_special:
            remove = ['+','-','=','!','~','`','*','|','"','\'','$','%','^','&','@','{','}','[',']',';',',','.','<','>','?','@','&','*','(',')','\/','/']
            for c in remove:
                title = title.replace(c, '')
        return title
    return ''

def upload_result_sheet(instance, filename):
    return upload_directory_path(instance, filename, dirname='results')

def upload_candidate_image(instance, filename):
    return upload_directory_path(instance, filename, dirname='candidates')

def upload_directory_path(instance, filename, dirname='results'):
    # Get Current Date
    todays_date = datetime.now()

    # set the complete filename, path and extension
    path = "{}{}{}{}/".format(dirname, todays_date.year, todays_date.month, todays_date.day)
    extension = "." + filename.split('.')[-1]
    stringId = str(uuid.uuid4())
    randInt = str(random.randint(10, 99))

    # Filename reformat
    filename_reformat = stringId + randInt + extension

    return os.path.join(path, filename_reformat)

def get_zone_ct(
        model,
        verbose: Optional[bool]=False
) -> Optional[ContentType]:
    
    # we can use settings.Debug instead of verbose

    zone_ct = None
    try:
        zone_ct = ContentType.objects.get_for_model(model)
    except Exception as e:
        if verbose is True:
            print(f'{TerminalColors.WARNING}Warning:{TerminalColors.ENDC} Exception encountered etching content type for model: {model.__name__}\n{e}')
    return zone_ct

def print_progress_bar(
    iteration,
    total,
    prefix = '',
    suffix = '',
    decimals = 1,
    length = 100,
    fill = '█',
    printEnd = "\r"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    prompt = f'{0}\r{prefix} |{bar}| {percent}% {suffix}'
    print(prompt, end=printEnd, flush=True)
    sys.stdout.flush()
    # Print New Line on Complete
    if iteration == total: 
        print()


def merge_column_excludes(fields):
    return '|'.join([f'{f}' for f in fields]) if len(fields) > 0 else ''


def make_title_key(title):
    if title is not None:
        return '{}'.format(title) \
                        .replace(' ', '_') \
                        .lower()
    return ''


def trim_vote_count(votes_number: int) -> str:
    value = f'{votes_number}'
    if votes_number > 0 and votes_number < 1000:
        value = '{}'.format(value)
    elif votes_number >= 1000 and votes_number < 1000000:
        value = '{}K'.format(value[:-3])
    elif votes_number >= 1000000 and votes_number < 1000000000:
        value = '{}M'.format(value[:-6])
    return value


def get_profile_photo(gender='f'):
    AVATAR_PATH = 'sql/faker/'
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




# class LazyEncoder(DjangoJSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, YourCustomType):
#             return str(obj)
#         return super().default(obj)

