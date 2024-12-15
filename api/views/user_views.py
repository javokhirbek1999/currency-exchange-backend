from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.template.loader import render_to_string

from rest_framework import generics, permissions, views, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from api.permissions import user_permissions
from api.serializers import user_serializer


class AllUsers(generics.ListAPIView):

    """API View for listing all available users."""

    permission_classes = (user_permissions.AllowAny,)
    serializer_class = user_serializer.UserSerializer
    queryset = get_user_model().objects.all()
