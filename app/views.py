from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status

from power.utils import ok_1, ok_0, ERRS
from trained_data import get_prediction, get_peaks

from authentication.decorators import is_authorized

@is_authorized
@api_view(["POST"])
def data_file_view(request, user_id):
    
    state = request.POST.get('state')
    time_format = request.POST.get('format')
    file = request.FILES.get('data_file')

    if not file:
        return ok_0(code=ERRS.INVALID_BODY, status=status.HTTP_400_BAD_REQUEST)

    res = get_prediction(file, state, time_format)
    
    if not res:
        return ok_0(code=ERRS.SERVER_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ok_1(data=res)
    
@is_authorized
@api_view(["POST"])
def spikes_view(request, user_id):
    
    state = request.POST.get('state')
    file = request.FILES.get('data_file')

    if not file or not state:
        return ok_0(code=ERRS.INVALID_BODY, status=status.HTTP_400_BAD_REQUEST)

    forecasting = get_prediction(file, state, "daily")
    
    if not forecasting:
        return ok_0(code=ERRS.SERVER_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    forecasting = {'t': forecasting['t'], 'df': forecasting['df'],  **get_peaks(forecasting, "daily")}

    return ok_1(data=forecasting)
    

@is_authorized
@api_view(["POST"])
def peak_hours_view(request, user_id):
    
    state = request.POST.get('state')
    file = request.FILES.get('data_file')

    if not file or not state:
        return ok_0(code=ERRS.INVALID_BODY, status=status.HTTP_400_BAD_REQUEST)

    forecasting = get_prediction(file, state, "hourly")
    
    if not forecasting:
        return ok_0(code=ERRS.SERVER_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    forecasting = {'t': forecasting['t'], 'df': forecasting['df'],  **get_peaks(forecasting, "hourly")}

    return ok_1(data=forecasting)
    