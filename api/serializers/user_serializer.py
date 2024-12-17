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


class UpdateUserDetailsSerializer(serializers.ModelSerializer):
    """Serializer for updating user details and password."""
    
    current_password = serializers.CharField(
        max_length=128, write_only=True, required=False, style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        max_length=128, write_only=True, required=False, style={'input_type': 'password'}
    )

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email', 'is_staff', 'current_password', 'new_password')
        extra_kwargs = {
            'is_staff': {'read_only': True},
        }

    def validate(self, attrs):
        # If a password change is requested, validate current password
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')

        if current_password and new_password:
            user = self.instance
            if not user.check_password(current_password):
                raise serializers.ValidationError({'current_password': 'Current password is incorrect.'})

            if current_password == new_password:
                raise serializers.ValidationError({'new_password': 'New password cannot be the same as the current password.'})
        
        return attrs

    def update(self, instance, validated_data):
        # Handle password update if provided
        current_password = validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)

        if current_password and new_password:
            instance.set_password(new_password)

        # Update other fields
        instance = super().update(instance, validated_data)
        instance.save()
        return instance

    

class TokenVerificationSerializer(serializers.Serializer):

    """Serializer for verifying the authentication tokens."""

    token = serializers.CharField(trim_whitespace=True)


    def validate_token(self, token_key):
        try:
            token = Token.objects.get(key=token_key) 

            return token.user
        except Token.DoesNotExist:
            msg = _('Invalid token')
            raise ValidationError(msg, code='invalid_token')   

        


class AuthTokenSerializer(serializers.Serializer):

    """Serializer for creating authentication token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )


    def validate(self, attrs):
        
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )


        if not user:
            msg = _('Validation Error, invalid credentials')
            raise serializers.ValidationError(msg, code='authentication')


        if not user.is_active:
            msg = _('User is blocked, please contact the admin')
            raise ValidationError(msg, code='not_active')

        attrs['user'] = user

        return attrs
        