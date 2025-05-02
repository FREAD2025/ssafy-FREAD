from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SignupSerializer
from django.contrib.auth import login as auth_login

@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save() # user 인스턴스 생성
        auth_login(request, user)  # 자동 로그인 처리
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
