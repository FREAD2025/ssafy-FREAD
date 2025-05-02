from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SignupSerializer
from django.contrib.auth import login as auth_login
from drf_spectacular.utils import extend_schema, OpenApiResponse # swagger

# 회원 가입 (/api/v1/users/signup/)
@extend_schema( # swagger에서 표시
    summary="회원 가입",
    description="새로운 사용자를 등록하고, 성공적으로 가입하면 자동 로그인 처리합니다.",
    request=SignupSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(response=SignupSerializer, description="회원 가입 성공 및 사용자 정보 반환"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="유효하지 않은 요청 데이터"),
    }
)
@api_view(['POST']) 
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save() # user 인스턴스 생성
        auth_login(request, user)  # 자동 로그인 처리
        return Response(serializer.data, status=status.HTTP_201_CREATED)
