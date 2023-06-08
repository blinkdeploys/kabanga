from django_rq import job     
from __report.utils import collate_results, collate_seats, clear_collated_results


@job # ("high", timeout=600) # timeout is optional
def collation_task(context=None):
    # print(f'running job ... {context}')
    total = 0
    total += collate_results()
    total += collate_seats()
    print(f'{total} records collated')
    print('::::::::::::::::::::::::::::::::::::::')
    return "Response from async method"

@job
def clear_collation_task():
    return clear_collated_results()
