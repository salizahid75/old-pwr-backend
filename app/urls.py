from django.urls import path, re_path

from .views import data_file_view, spikes_view, peak_hours_view

urlpatterns = [
    re_path('data-file/?$', data_file_view),
    re_path('spikes/?$', spikes_view),
    re_path('peak-hours/?$', peak_hours_view),
]
