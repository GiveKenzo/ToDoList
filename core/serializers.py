from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import (AuthenticationFailed, NotAuthenticated,
                                    ValidationError)

from core.models import User


class PasswordField(serializers.CharField):

    def __init__(self, **kwargs):
        kwargs['style'] = {'input_type': 'password'}
        kwargs.setdefault('write_only', True)
        super().__init__(**kwargs)
        self.validators.append(validate_password)

class CreateUserSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'email',
            'password',
            'password_repeat',
        )

    # Нужно  провалидировать, что у нас paswword_repeat совпадает с password
    def velidate(self, attrs: dict):
        if attrs['password']:
            raise ValidationError('Password must match')
        return attrs

    def create(self, validated_data: dict):
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required = True)
    password = PasswordField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password')
        
    def create(self, validated_data: dict):
        if not (user := authenticate(
                username = validated_data['username'],
                password = validated_data['password']
        )):
            raise AuthenticationFailed
        return user

# Все поля которые у нас есть, кроме пароля мы будем принимать и отдавать
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

# Реализация смены пароля
class UpdatePasswordSerializer(serializers.Serializer):
    user = serializers.HiddenField(default = serializers.CurrentUserDefault())
    old_password = PasswordField(required = True)
    new_password = PasswordField(required = True)
    
    # Валидация старого пароля
    def validate(self, attrs: dict):
        if not(user := attrs['user']):
            raise NotAuthenticated
        if not user.check_password(attrs['ola_password']):
            raise ValidationError({'old password': 'field is incorrect'})
        return attrs

    def create(self, validated_data: dict):
        return NotImplementedError
    
    # Новый пароль
    def update(self, instance, validated_data: dict):
        instance.password = make_password(validated_data['new_passwrod'])
        instance.save(update_fields = ('password', ))
        return instance
