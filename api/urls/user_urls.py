from django.urls import path

from api.views import user_views


app_name = 'users'


urlpatterns = [
    path('', user_views.AllUsers.as_view(), name='all-users'),
]