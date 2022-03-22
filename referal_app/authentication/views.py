from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .renderers import UserJSONRenderer
from .serializers import LoginSerializer, UserUpdateSerializer, UserSerializer
from .models import User, ConfirmCode
import time
import random
import string
digits = string.digits

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        phone = user['phone']
        if 'code' in user.keys(): 
            serializer = self.serializer_class(data=user)
            serializer.is_valid(raise_exception=True)
        else:
            confirm_code = ''.join(random.sample(digits, 4))
            ConfirmCode.objects.create(phone = phone, code = confirm_code)
            time.sleep(2)
            data = {'confirm code for phone': user['phone']}
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    update_serializer_class = UserUpdateSerializer
    def retrieve(self, request, *args, **kwargs):
        phone = request.user.phone
        referal_link = request.user.referal_link
        user_referals = User.objects.filter(referal=referal_link)
        list_ref = []
        for el in user_referals:
            list_ref.append(el.phone)
        data = {
            'phone': phone,
            'user_referals': list_ref,
            'referal': referal_link
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})
        if 'phone' in serializer_data.keys():
            if User.objects.filter(phone=serializer_data['phone']).exists():
                return Response({"update error": f"user with phone {serializer_data['phone']} already log up"}, status=status.HTTP_400_BAD_REQUEST)
        if 'referal' in serializer_data.keys():
            user_ref = request.user.referal
            if len(user_ref) != 0:
                return Response({"update_error": "you already have a referal"},status=status.HTTP_400_BAD_REQUEST)
            if not User.objects.filter(referal_link=serializer_data['referal']).exists():
                return Response({"update_error": "nonexistent referal link"},status=status.HTTP_400_BAD_REQUEST)
        updateble_data = ['phone', 'referal']
        for el in serializer_data.keys():
            if el not in updateble_data:
                return Response({"update_error": f"unknown atribute: {el}"}, status=status.HTTP_400_BAD_REQUEST)        
        serializer = self.update_serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.data
        response_data['new_token'] = request.user.token

        return Response(response_data, status=status.HTTP_200_OK)        