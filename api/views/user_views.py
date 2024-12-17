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


class UserAPIView(generics.CreateAPIView):

    """API View for creating users."""

    permission_classes = (user_permissions.AllowAny,)
    serializer_class = user_serializer.UserSerializer


    def post(self, request, *args, **kwargs):
        
        user = request.data

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = get_user_model().objects.get(email=user_data['email'])

        return Response({'status': 'success', 'user': user_data}, status=status.HTTP_201_CREATED)        


class RetrieveUserAPIView(generics.RetrieveDestroyAPIView):

    """API View for retrieving, updating and deleting the user."""

    permission_classes = (user_permissions.IsOwnerOrReadOnly,)
    serializer_class = user_serializer.UserSerializer

    def get_object(self):
        return get_user_model().objects.get(email=self.kwargs.get('email'))
    

class UpdateUserAPIView(generics.RetrieveUpdateAPIView):
    
    """API View for retrieving and updating the user details, including password."""
    
    permission_classes = (user_permissions.IsOwner,)
    serializer_class = user_serializer.UpdateUserDetailsSerializer

    def get_object(self):
        return get_user_model().objects.get(email=self.kwargs.get('email'))

    

class VerifyToken(views.APIView):

    """API View for verifying the authentication tokens."""

    permission_classes = (user_permissions.AllowAny,)
    serializer_class = user_serializer.TokenVerificationSerializer
    
    def post(self, request):

        serializer = self.serializer_class(data=request.data)


        if serializer.is_valid():
            # Token is valid
            user = serializer.validated_data['token']
            
            return Response({
            'token': Token.objects.get(user=user).key,
            'user_id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': {
                'year': user.date_joined.year,
                'month': user.date_joined.month,
                'day': user.date_joined.day,
                'time': user.date_joined.time().strftime("%H:%M:%S")
            },
            'date_updated': {
                'year': user.date_updated.year,
                'month': user.date_updated.month,
                'day': user.date_updated.day,
                'time': user.date_updated.time().strftime("%H:%M:%S")
            },
        })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AuthTokenAPIView(ObtainAuthToken):

    """API View for obtaining authentication token."""

    permission_classes = (permissions.AllowAny,)
    serializer_class = user_serializer.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    
    def post(self, request, *args, **kwargs):
        
        serializer = user_serializer.AuthTokenSerializer(data=request.data, context={'request':request})
        print(request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
       
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': {
                'year': user.date_joined.year,
                'month': user.date_joined.month,
                'day': user.date_joined.day,
                'time': user.date_joined.time().strftime("%H:%M:%S")
            },
            'date_updated': {
                'year': user.date_updated.year,
                'month': user.date_updated.month,
                'day': user.date_updated.day,
                'time': user.date_updated.time().strftime("%H:%M:%S")
            },
        })