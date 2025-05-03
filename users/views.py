from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import SignupSerializer, SocialExtraInfoSerializer
from django.contrib.auth import login as auth_login
from drf_spectacular.utils import extend_schema, OpenApiResponse # swagger
from rest_framework.permissions import IsAuthenticated

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

# 소셜 로그인 추가 정보 입력 (/api/v1/users/social/extra-info/)
@extend_schema(
    summary="소셜 로그인 추가 정보 입력",
    description="소셜 로그인 후 최초 한 번, 이름/장르/작가 유형 등의 추가 정보를 입력해야 회원가입이 완료됩니다.",
    request=SocialExtraInfoSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=SocialExtraInfoSerializer, description="추가 정보 입력 성공 및 업데이트된 사용자 정보 반환"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="잘못된 요청 데이터 또는 이미 추가 정보를 입력한 경우"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 사용자"),
    },
)
@api_view(['POST']) # PUT으로 바꾸는 것 고려해보기
@permission_classes([IsAuthenticated]) # 로그인한 사용자라면
def social_extra_info(request):
    user = request.user # 현재 로그인한 사용자
    if user.is_profile_completed:
        return Response({'detail': '이미 추가 정보를 입력하셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = SocialExtraInfoSerializer(instance=user, data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save() # Serializer의 update 메서드 호출
        return Response(serializer.data, status=status.HTTP_200_OK)
