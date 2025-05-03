from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import SignupSerializer, SocialExtraInfoSerializer, LoginSerializer, FindIdSerializer, PasswordResetSerializer, PasswordChangeSerializer
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from drf_spectacular.utils import extend_schema, OpenApiResponse # swagger
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.core.mail import send_mail # 이메일 발송
from django.utils.crypto import get_random_string
from django.conf import settings



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

# 로그인 (/api/v1/users/login/)
@extend_schema(
    summary="사용자 로그인 (세션 기반)",
    description="제공된 아이디와 비밀번호로 사용자를 인증하고, 성공하면 세션을 생성합니다.",
    request=LoginSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="로그인 성공"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="잘못된 요청 데이터"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증 실패 (아이디 또는 비밀번호 오류)"),
    }
)
@api_view(['POST'])
def login(request):
    # 1. 요청 데이터(username, password) 직렬화
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data # Serializer의 validate 메서드에서 반환된 User 객체
        auth_login(request, user)
        return Response({'message': '로그인 성공', 'user': {'id': user.pk, 'username': user.username, 'email': user.email, 'name': user.name}}, status=status.HTTP_200_OK)

# 로그아웃 (/api/v1/users/logout/)
@extend_schema(
    summary="사용자 로그아웃 (세션 기반)",
    description="현재 로그인한 사용자의 세션을 만료시키고 로그아웃 처리합니다.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="로그아웃 성공"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증 실패 (로그인되지 않은 사용자)"),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # 로그인한 사용자만 가능
def logout(request):
    auth_logout(request)
    return Response({'message': '로그아웃 성공'}, status=status.HTTP_200_OK)

# 세션 유지 확인 (/api/v1/users/session-check/)
@extend_schema(
    summary="로그인 상태 확인",
    description="현재 사용자가 로그인한 상태인지 확인합니다.",
    responses={
        200: OpenApiResponse(description="로그인 상태 (세션 유지됨)"),
        401: OpenApiResponse(description="로그아웃 상태 또는 세션 만료"),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_check(request):
    return Response({
        "message": "현재 로그인된 상태입니다.",
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "name": request.user.name,
            "email": request.user.email
        }
    }, status=200)

# ID 찾기 (/api/v1/users/find-id/)
@extend_schema(
    summary="아이디 찾기 (이메일로 바로 확인)",
    description="제공된 이메일 주소와 일치하는 사용자의 아이디를 데이터베이스에서 찾아 즉시 반환합니다.",
    request=FindIdSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(response={'username': str}, description="아이디 찾기 성공, 아이디 반환"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="유효하지 않은 요청 데이터"),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(description="해당 이메일 주소로 등록된 사용자 없음"),
    }
)
@api_view(['POST'])
def find_id(request):
    User = get_user_model()
    serializer = FindIdSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        email = serializer.validated_data['email'] # 유효성 검사를 통과한 validated_data에서 email 정보 가져오기
        # validated_data: OrderedDict([('email', 'testuser@example.com')])
        try:
            user = User.objects.get(email=email) # 제공된 email에 정확히 일치하는 User 객체 반환
            # 아이디 일부 마스킹 (예: 앞 2글자 + 나머지 '*' 처리)
            username_masked = user.username[:2] + '*' * (len(user.username) - 2) # 아이디 일부 마스킹 처리
            return Response({'username': username_masked}, status=status.HTTP_200_OK)
        except User.DoesNotExist: # 제공된 email과 대응되는 user를 찾지 못했다면
            return Response({'detail': '해당 이메일 주소로 등록된 사용자를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # 유효성 감사에 실패했다면 400 에러

# 임시 비밀번호 이메일 발급 (/api/v1/users/reset-password/)
@extend_schema(
    summary="임시 비밀번호 발급",
    description="제공된 이메일 주소와 일치하는 사용자를 찾아 임시 비밀번호를 생성하고 이메일로 발송합니다.",
    request=PasswordResetSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="임시 비밀번호 발송 성공, 이메일 발송됨"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="유효하지 않은 요청 데이터"),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(description="해당 이메일 주소로 등록된 사용자 없음"),
    }
)
@api_view(['POST'])
def password_reset_request(request):
    User = get_user_model()
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email'] # 유효성 검사를 통과한 validated_data에서 email 정보 가져오기
    try:
        user = User.objects.get(email=email) # 해당 이메일과 대응되는 user 객체 반환
        # 1. 임시 비밀번호 생성 (영문+숫자 10자리)
        # get_random_string: 영문 대소문자 (a-zA-Z)와 숫자 (0-9)를 포함한 무작위 문자열 생성
        temp_password = get_random_string(length=10)
        # 2. 사용자의 비밀번호를 임시 비밀번호로 변경하고 저장
        user.set_password(temp_password)
        user.save()
        # 3. 이메일 발송
        send_mail(
            subject='[Fread] 임시 비밀번호 안내',
            message=f'안녕하세요. FREAD입니다.\n 임시 비밀번호는 다음과 같습니다: {temp_password}\n로그인 후 반드시 마이페이지에서 비밀번호를 변경해 주세요.',
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email], # 이메일을 수신할 사람의 이메일 주소 목록
            fail_silently=False, # 이메일 발송에 실패하면 SMTPException 오류 발생
        )
        return Response({'message': '임시 비밀번호가 이메일로 발송되었습니다. 로그인 후 비밀번호를 변경해 주세요.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist: # 이메일과 일치하는 user가 없다면
        return Response({'detail': '해당 이메일 주소로 등록된 사용자를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

# 비밀번호 변경 (/api/v1/users/password/change/)
@extend_schema(
    summary="비밀번호 변경",
    description="현재 로그인된 사용자의 기존 비밀번호를 확인한 뒤, 새 비밀번호로 변경합니다.",
    request=PasswordChangeSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="비밀번호 변경 성공"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="잘못된 요청 데이터 (비밀번호 불일치, 형식 오류 등)"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="로그인되지 않은 사용자"),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # 로그인된 사용자만 가능
def password_change(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'}, status=status.HTTP_200_OK)

