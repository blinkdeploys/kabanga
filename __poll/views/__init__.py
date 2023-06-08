from .home import index_view
from .event import event_list, event_detail
from .position import position_list, position_detail
from .result import result_list, result_detail, result_station_list, result_candidate_list, result_position_list
from .result_approval import (
    result_approval_list,
    result_approval_list_presidential,
    result_approval_list_parliamentary,
    result_approval_list_presidential_constituency,
    result_approval_list_presidential_regional,
    result_approval_list_presidential_national,
    result_approval_list_parliamentary_constituency,
    result_approval_list_parliamentary_regional,
    result_approval_list_parliamentary_national,
    result_approval_detail,
    result_approval_form,


    approve_presidential_constituency,
    approve_presidential_regional,
    approve_presidential_national,
    approve_parliamentary_constituency,
    approve_parliamentary_regional,
    approve_parliamentary_national,
    approve_presidential_constituency,
    approve_presidential_regional,
    approve_presidential_national,
    approve_parliamentary_constituency,
    approve_parliamentary_regional,
    approve_parliamentary_national,
)
from .office import office_list, office_detail
from .submit import submit_complete_view
