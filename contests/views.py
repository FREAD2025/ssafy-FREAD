from django.shortcuts import get_object_or_404  # 객체가 존재하지 않으면 404 에러를 자동으로 반환해주는 기능
from rest_framework import status  # HTTP 상태 코드를 쉽게 사용할 수 있도록 제공 (예: 200 OK, 404 Not Found)
from rest_framework.decorators import api_view, permission_classes  # API 뷰로 만들어주는 데코레이터와 권한 설정을 위한 데코레이터
from rest_framework.permissions import IsAuthenticated, IsAdminUser  # 권한 클래스 (인증된 사용자, 관리자)
from rest_framework.response import Response  # API 응답을 만들어주는 클래스
from rest_framework.pagination import PageNumberPagination  # 목록을 여러 페이지로 나눠서 보여주는 기능

from .models import Contest  # 현재 앱의 Contest 모델을 가져옴 (데이터베이스 테이블과 연결된 클래스)
from .serializers import ContestSerializer, SimpleContestSerializer  # 현재 앱의 Serializer들을 가져옴 (모델 데이터를 JSON 등으로 변환해주는 도구)
from drf_spectacular.utils import extend_schema, OpenApiResponse   # Swagger (API 문서 자동 생성 도구)

# 전체 공모전 목록 조회 및 등록 (/api/v1/contests/)
@extend_schema(
    summary="공모전 전체 목록 조회 및 등록",
    description="""
    GET : 전체 공모전 리스트를 조회합니다. (모든 사용자 가능)
    POST : 관리자만 새로운 공모전을 등록할 수 있습니다. (관리자 권한 필요)
    """,
    responses={status.HTTP_200_OK: SimpleContestSerializer(many=True)},  # 성공 시 응답 데이터 형태
)
@api_view(['GET', 'POST'])  
def contest_list(request):
    # 공모전 전체 목록 조희
    if request.method == 'GET':
        queryset = Contest.objects.all().order_by('-created_at')  # 데이터베이스에서 모든 공모전을 가져와 등록일 역순으로 정렬 (최신 공모전 먼저)
        paginator = PageNumberPagination()  # 페이지네이션 기능을 사용하기 위한 객체 생성
        paginator.page_size = 15  # 한 페이지당 15개 표시
        page = paginator.paginate_queryset(queryset, request)  # 가져온 공모전 목록을 요청에 따라 페이지로 나눔
        """
        page 예시
        [
            {
                "id": 1,
                "title": "청년 창작 공모전",
                "organizer": "문화재단",
                "start_date": "2025-05-01",
                "end_date": "2025-05-31",
                "image": "https://example.com/contest1.jpg",
                "details_url": "https://example.com/contest1"
                ...
            },
            ...
            {
                "id": 10,
        """
        serializer = SimpleContestSerializer(page, many=True, context={'request': request})  # 나뉜 페이지의 공모전 데이터를 JSON 형태로 변환
        # 사용자가 로그인한 상태인지 확인하기 위해 request를 인자로 함께 넘겨줌 -> is_liked 필드의 값 결정
        return paginator.get_paginated_response(serializer.data)  # 페이지네이션된 응답과 함께 JSON 데이터를 반환
        # paginator.get_paginated_response(serializer.data) 예시
        """
        {
            "count": 25,  # 전체 공모전 개수
            "next": "http://localhost:8000/api/v1/contests/?page=2", # 다음 페이지의 URL
            "previous": null, # 이전 페이지 URL
            "results": [
                {
                    "id": 1,
                    "title": "청년 창작 공모전",
                    "organizer": "문화재단",
                    "start_date": "2025-05-01",
                    "end_date": "2025-05-31",
                    "target_audience": "대학생, 
                    "has_prize":true,
                    "is_liked": true
                },
                ...
            ]
        }
        """

    # 공모전 등록 (관리자만 가능)
    elif request.method == 'POST':
        if not request.user.is_staff:  # 요청한 사용자가 관리자가 아니라면
            return Response({'detail': '관리자 권한이 필요합니다.'}, status=status.HTTP_403_FORBIDDEN)  # 403 Forbidden 에러 반환 (권한 없음)
        serializer = ContestSerializer(data=request.data, context={'request': request})  # 요청으로 들어온 데이터로 Serializer 생성
        serializer.is_valid(raise_exception=True)  # 데이터 유효성 검사. 유효하지 않으면 에러 발생
        serializer.save()  # 유효한 데이터를 데이터베이스에 저장, 공모전 생성
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # 성공적으로 생성되었음을 알리는 201 Created 응답과 함께 생성된 데이터 반환

# 특정 공모전 상세 조회, 수정, 삭제 (/api/v1/contests/<int:contest_id>/)
@extend_schema(
    summary="공모전 상세 조회, 수정, 삭제",
    description="""
    GET : 특정 ID의 공모전 상세 정보 조회 (모든 사용자 가능)
    PUT,DELETE : 해당 공모전 정보를 수정하거나 삭제 (관리자만 가능)
    """,
    # responses={status.HTTP_200_OK: ContestSerializer}, 
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=ContestSerializer, description="요청 성공"),
        status.HTTP_204_NO_CONTENT: OpenApiResponse(description="공모전 삭제 성공 (DELETE)"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="잘못된 요청 데이터 (수정 시)"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 사용자"),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없는 사용자 (관리자만 수정/삭제 가능)"),
        status.HTTP_404_NOT_FOUND: OpenApiResponse(description="해당 공모전이 존재하지 않음"),
    } 
)
@api_view(['GET', 'PUT', 'DELETE'])  
def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)  # 주어진 ID의 공모전을 찾고, 없으면 404 에러 반환

    # 개별 공모전 상세 정보 조회
    if request.method == 'GET':
        serializer = ContestSerializer(contest, context={'request': request})  # 찾은 공모전 데이터를 JSON 형태로 변환
        return Response(serializer.data)  # JSON 데이터 반환

    # 아래 요청들은 관리자 권한이 필요함
    if not request.user.is_staff:  # 요청한 사용자가 관리자가 아니라면
        return Response({'detail': '관리자 권한이 필요합니다.'}, status=status.HTTP_403_FORBIDDEN)  # 403 Forbidden 에러 반환
        
    # 공모전 정보 수정
    if request.method == 'PUT':
        serializer = ContestSerializer(contest, data=request.data, partial=True, context={'request': request})  # 요청 데이터로 Serializer 생성
        serializer.is_valid(raise_exception=True)  # 데이터 유효성 검사
        serializer.save()  # 유효한 데이터를 데이터베이스에 저장하여 수정
        return Response(serializer.data)  # 수정된 데이터 반환

    # 공모전 삭제
    elif request.method == 'DELETE':
        contest.delete()  # 데이터베이스에서 해당 공모전 삭제
        return Response(status=status.HTTP_204_NO_CONTENT)  # 성공적으로 삭제되었음을 알리는 204 No Content 응답 반환

# --- 공모전 찜하기 (POST) / 찜 해제 (DELETE) ---
@extend_schema(
    summary="공모전 찜하기/찜 해제",
    description="""
    로그인한 사용자가 특정 공모전을 찜하거나 찜 해제합니다.
    POST 요청으로 찜하고, DELETE 요청으로 찜 해제합니다.
    """,
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="찜하기 또는 찜 해제 성공"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 사용자"),  # 인증되지 않은 경우
        status.HTTP_404_NOT_FOUND: OpenApiResponse(description="공모전을 찾을 수 없습니다."),  # 해당 ID의 공모전이 없는 경우
    }
)
@api_view(['POST', 'DELETE'])  # 이 뷰는 POST (찜하기)와 DELETE (찜 해제) 요청을 처리합니다.
@permission_classes([IsAuthenticated])  # 이 뷰는 로그인한 사용자만 접근 가능합니다.
def like_contest(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)  # 찜/해제할 공모전을 찾고, 없으면 404 에러 반환
    user = request.user  # 현재 로그인한 사용자 정보 가져오기

    if request.method == 'POST':
        # POST 요청: 찜하기
        if user in contest.liked_users.all():  # 이미 사용자가 이 공모전을 찜했다면
            return Response({'detail': '이미 찜한 공모전입니다.'}, status=status.HTTP_400_BAD_REQUEST)  # 400 Bad Request 에러 반환
        contest.liked_users.add(user)  # 공모전의 'liked_users' (찜한 사용자들) 목록에 현재 사용자 추가
        likes_count = contest.liked_users.count()  # 좋아요 수 조회
        return Response({
            'status': 'liked', 
            'message': '공모전을 찜했습니다.',
            'likes_count': likes_count
        }, status=status.HTTP_200_OK)  # 200 OK 응답과 함께 성공 메시지 반환

    elif request.method == 'DELETE':
        # DELETE 요청: 찜 해제
        if user not in contest.liked_users.all():  # 사용자가 이 공모전을 찜하지 않았다면
            return Response({'detail': '찜하지 않은 공모전입니다.'}, status=status.HTTP_400_BAD_REQUEST)  # 400 Bad Request 에러 반환
        contest.liked_users.remove(user)  # 공모전의 'liked_users' 목록에서 현재 사용자 제거
        likes_count = contest.liked_users.count()  # 좋아요 수 조회
        return Response({
            'status': 'unliked', 
            'message': '공모전 찜을 해제했습니다.',
            'likes_count': likes_count
        }, status=status.HTTP_200_OK)  # 200 OK 응답과 함께 성공 메시지 반환

urlpatterns = [
    # ... other urls
    # path('', contest_list), # 필요하다면 URLConf에 추가
    # path('<int:contest_id>/', contest_detail), # 필요하다면 URLConf에 추가
    # path('<int:contest_id>/like/', like_contest), # 필요하다면 URLConf에 추가
]