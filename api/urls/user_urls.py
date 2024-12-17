from django.urls import path

from api.views import user_views


app_name = 'users'


urlpatterns = [
    path('', user_views.AllUsers.as_view(), name='all-users'),
    path('create/', user_views.UserAPIView.as_view(), name='create-user'),
    path('login/', user_views.AuthTokenAPIView.as_view(), name='user-token'),
    path('verify_token/', user_views.VerifyToken.as_view(), name='token-verification'),
    path('<str:email>/', user_views.RetrieveUserAPIView.as_view(), name='user'),
    path('<str:email>/update/', user_views.UpdateUserAPIView.as_view(), name='update-user'),
]