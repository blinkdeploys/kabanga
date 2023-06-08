import os, json
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from __poll.models import (
    Airport, Category, ChecklistOpinion,
    EyeColor, HairColor, IdentificationType,
    Language, Office, RecordStatus, SpecialtyGroup,
    Specialty, State, WorldRegion, Region,
    Aircraft, AircraftConfiguration, AircraftOwnershipType,
    AOCCode, AMORating, ATOType, FlightPhase, NDTTechnique
)


class Command(BaseCommand):
    '''
    Remove all entries in the poll tables
    python manage.py depopulate_poll
    '''
    help = 'Empty data from poll table'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        all_models = [
            Airport, Category, ChecklistOpinion,
            EyeColor, HairColor, IdentificationType,
            Language, Office, RecordStatus, SpecialtyGroup,
            Specialty, State, WorldRegion, Region
        ]
        for model in all_models:
            try:
                model.objects.all().delete()
            except ModuleNotFoundError:
                print(f"[ModuleNotFoundError] Model {model.db_table} not found, skipping...")
                continue
            except Exception:
                print(f"[Exception] There was an exception handling a model {model.db_table}, skipping...")
                continue
            


