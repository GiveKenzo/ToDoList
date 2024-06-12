from django.contrib.auth import login, logout
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.serializers import (CreateUserSerializer, LoginSerializer,
                              ProfileSerializer, UpdatePasswordSerializer)

from .models import User


class SignupView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    
class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        login(request = request, user = serializer.save())
        return Response(serializer.data, status = status.HTTP_201_CREATED)

# Нам нужно получать, обновлять и удалять
class ProfileView(generics.RetrieveDestroyAPIView):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]#Аутентификация
    
    def get_object(self): #Возвращает пользователя, потому что queryset лежит user
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        # В данном случае logout просто почистит куки
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UpdatePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatePasswordSerializer
    
    def get_object(self):
        return self.request.user
