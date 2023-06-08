from django.contrib.contenttypes.models import ContentType 


def save_supernational_collation_sheet(sheet):
    # source_model: NationalCollationSheet
    source_model = ContentType.objects.get(model='nationalcollationsheet').model_class()
    # target_model: SupernationalCollationSheet
    target_model = ContentType.objects.get(model='supernationalcollationsheet').model_class()
    cs = None
    if sheet is not None:
        parent_sheet = sheet.region.nation
        zone_ct = sheet.zone_ct
        party = sheet.party
        total_votes = 0
        total_votes_ec = 0
        total_invalid_votes = 0

        # get all the constituency votes for all member stations
        sheet_votes = source_model.objects \
                                    .filter(
                                        region__in=parent_sheet.regions.all(),
                                        party=party,
                                        zone_ct=zone_ct,
                                    ) \
                                    .values('total_votes', 'total_votes_ec', 'total_invalid_votes')
        if sheet_votes is not None:
            total_votes = 0
            total_votes_ec = 0
            total_invalid_votes = 0
            for sheet_vote in sheet_votes:
                count = sheet_vote.get('total_votes', 0)
                total_votes += count if count is not None else 0
                count = sheet_vote.get('total_votes_ec', 0)
                total_votes += count if count is not None else 0
                count = sheet_vote.get('total_invalid_votes', 0)
                total_invalid_votes += count if count is not None else 0

        # save total votes tot the station collation sheet
        try:
            cs, _ = target_model.objects \
                                .update_or_create(
                                    party=party,
                                    nation=parent_sheet,
                                    zone_ct=zone_ct,
                                    defaults=dict(
                                        total_votes=total_votes,
                                        total_invalid_votes=total_invalid_votes,
                                        total_votes_ec=total_votes_ec,
                                    )
                                )
            mode = 'C/U'
        except Exception as e:
            print(e)
    return cs


def save_national_collation_sheet(sheet):
    # source_model: RegionalCollationSheet
    source_model = ContentType.objects.get(model='regionalcollationsheet').model_class()
    # target_model: NationalCollationSheet
    target_model = ContentType.objects.get(model='nationalcollationsheet').model_class()
    cs = None
    if sheet is not None:
        parent_sheet = sheet.constituency.region
        zone_ct = sheet.zone_ct
        party = sheet.party
        total_votes = 0
        total_votes_ec = 0
        total_invalid_votes = 0

        # get all the constituency votes for all member stations
        sheet_votes = source_model.objects \
                                    .filter(
                                        constituency__in=parent_sheet.constituencies.all(),
                                        party=party,
                                        zone_ct=zone_ct,
                                    ) \
                                    .values('total_votes', 'total_votes_ec', 'total_invalid_votes')
        if sheet_votes is not None:
            total_votes = 0
            total_votes_ec = 0
            total_invalid_votes = 0
            for sheet_vote in sheet_votes:
                count = sheet_vote.get('total_votes', 0)
                total_votes += count if count is not None else 0
                count = sheet_vote.get('total_votes_ec', 0)
                total_votes += count if count is not None else 0
                count = sheet_vote.get('total_invalid_votes', 0)
                total_invalid_votes += count if count is not None else 0

        # save total votes tot the station collation sheet
        try:
            cs, _ = target_model.objects \
                                .update_or_create(
                                    party=party,
                                    region=parent_sheet,
                                    zone_ct=zone_ct,
                                    defaults=dict(
                                        total_votes=total_votes,
                                        total_invalid_votes=total_invalid_votes,
                                        total_votes_ec=total_votes_ec,
                                    )
                                )
            mode = 'C/U'
        except Exception as e:
            print(e)
    return cs


def save_regional_collation_sheet(sheet):
    # source_model: ConstituencyCollationSheet
    source_model = ContentType.objects.get(model='constituencycollationsheet').model_class()
    # target_model: RegionalCollationSheet
    target_model = ContentType.objects.get(model='regionalcollationsheet').model_class()
    cs = None
    if sheet is not None:
        parent_sheet = sheet.station.constituency
        zone_ct = sheet.zone_ct
        party = sheet.party
        total_votes = 0
        total_votes_ec = 0
        total_invalid_votes = 0

        # get all the constituency votes for all member stations
        sheet_votes = source_model.objects \
                                    .filter(
                                        station__in=parent_sheet.stations.all(),
                                        party=party,
                                        zone_ct=zone_ct,
                                    ) \
                                    .values('total_votes', 'total_votes_ec', 'total_invalid_votes')
        if sheet_votes is not None:
            total_votes = 0
            total_votes_ec = 0
            total_invalid_votes = 0
            for sheet_vote in sheet_votes:
                count = sheet_vote.get('total_votes', 0)
                total_votes += count if count is not None else 0
                count = sheet_vote.get('total_votes_ec', 0)
                total_votes += count if count is not None else 0
                count = sheet_vote.get('total_invalid_votes', 0)
                total_invalid_votes += count if count is not None else 0

        # save total votes tot the station collation sheet
        try:
            cs, _ = target_model.objects \
                                .update_or_create(
                                    party=party,
                                    constituency=parent_sheet,
                                    zone_ct=zone_ct,
                                    defaults=dict(
                                        total_votes=total_votes,
                                        total_invalid_votes=total_invalid_votes,
                                        total_votes_ec=total_votes_ec,
                                    )
                                )
            mode = 'C/U'
        except Exception as e:
            print(e)
    return cs


def save_constituency_collation_sheet(sheet):
    # source_model: StationCollationSheet
    source_model = ContentType.objects.get(model='stationcollationsheet').model_class()
    # target_model: ConstituencyCollationSheet
    target_model = ContentType.objects.get(model='constituencycollationsheet').model_class()
    cs = None
    if sheet is not None:
        parent_sheet = sheet.station
        zone_ct = sheet.zone_ct
        party = sheet.candidate.party
        total_votes = 0
        total_votes_ec = 0
        total_invalid_votes = 0

        # get all the station votes for all candidates in the party
        sheet_votes = source_model.objects \
                                    .filter(
                                        candidate__in=party.candidates.all(),
                                        station=parent_sheet,
                                        zone_ct=zone_ct,
                                    ) \
                                    .values('total_votes', 'total_votes_ec', 'total_invalid_votes')
        if sheet_votes is not None:
            total_votes = 0
            total_votes_ec = 0
            total_invalid_votes = 0
            for sheet_vote in sheet_votes:
                count = sheet_vote.get('total_votes', 0)
                total_votes += count if count is not None else 0
                count = sheet_vote.get('total_votes_ec', 0)
                total_votes += count if count is not None else 0
                count = sheet_vote.get('total_invalid_votes', 0)
                total_invalid_votes += count if count is not None else 0

        # save total votes tot the station collation sheet
        try:
            cs, _ = target_model.objects \
                                .update_or_create(
                                    party=party,
                                    station=parent_sheet,
                                    zone_ct=zone_ct,
                                    defaults=dict(
                                        total_votes=total_votes,
                                        total_invalid_votes=total_invalid_votes,
                                        total_votes_ec=total_votes_ec,
                                    )
                                )
            mode = 'C/U'
        except Exception as e:
            print(e)
    return cs


def save_station_collation_sheet(result):
    # source_model: Result
    source_model = ContentType.objects.get(model='result').model_class()
    # target_model: StationCollationSheet
    target_model = ContentType.objects.get(model='stationcollationsheet').model_class()
    cs = None
    result_sheet = result.result_sheet
    if result is not None and result_sheet is not None:


        zone_ct = result_sheet.position.zone_ct
        station = result.station
        candidate = result.candidate
        total_votes = 0
        total_invalid_votes = result_sheet.total_invalid_votes
        total_votes_ec = 0

        # find total votes for this candidate from this station
        candidate_votes = source_model.objects \
                                    .filter(
                                        station=station,
                                        candidate=candidate,
                                    ).values('votes')
        if candidate_votes is not None:
            if candidate_votes[0] is not None:
                total_votes = candidate_votes[0].get('votes', 0)

        # save total votes tot the station collation sheet
        try:
            cs, _ = target_model.objects \
                                .update_or_create(
                                    station=station,
                                    candidate=candidate,
                                    zone_ct=zone_ct,
                                    defaults=dict(
                                        total_votes=total_votes,
                                        total_invalid_votes=total_invalid_votes,
                                        total_votes_ec=total_votes_ec,
                                    )
                                )
        except Exception as e:
            print(e)
        # try:
        #     cs = target_model.objects \
        #                                     .filter(
        #                                         candidate=candidate,
        #                                         station=station,
        #                                         zone_ct=zone_ct,
        #                                     ).first()
        #     cs.total_votes = total_votes
        #     cs.total_votes_ec = total_votes_ec
        #     mode = 'U'
        # except Exception as e:
        #     cs = target_model(
        #                 candidate=candidate,
        #                 station=station,
        #                 zone_ct=zone_ct,
        #                 total_votes = total_votes,
        #                 total_votes_ec = total_votes_ec,
        #             )
        #     mode = 'C'
        # cs.save()
                    
    return cs
