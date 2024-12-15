from django.contrib.auth import get_user_model, authenticate
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):

    """Serializer for User model."""

    confirm_password = serializers.CharField(max_length=250, write_only=True, style={'input_type': 'password'})

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'date_joined', 'date_updated', 'password', 'confirm_password', 'is_staff', 'is_active')
        extra_kwargs = {
            'date_joined': {'read_only': True},
            'date_updated': {'read_only': True},
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
        }
    

    def validate(self, attrs):
        
        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password')

        if password != confirm_password:
            raise ValidationError(_("Passwords didn't match"))

        return attrs
    
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        user = get_user_model().objects.get(email=validated_data['email'])


        user.set_password(validated_data['password'])
        user.save()

        validated_data['password'] = user.password


        return super().update(instance, validated_data)
