from django.urls import path
from . import views

urlpatterns = [
    # 인증
    path('signup/', views.signup, name='signup'), # POST : 회원가입
    path('login/', views.login, name='login'), # POST : 로그인
    path('logout/', views.logout, name='logout'), # POST : 로그아웃
    path('find-id/', views.find_id, name='find_id'), # POST : 이메일로 아이디 찾기
    path('reset-password/', views.reset_password, name='reset_password'), # POST : 임시 비번 발송
    path('social/extra-info/', views.social_extra_info, name='social_extra_info'), # POST : 소셜 로그인 유저의 추가 정보
    path('password/change/', views.password_change, name='password_change'), # POST : 비밀번호 변경

    # 마이페이지
    path('mypage/', views.mypage, name='mypage'), # GET : 마이페이지(프로필 일부, 분석내역 일부, 찜한 공모전 일부 확인)
    path('profile/', views.profile, name='profile'),  # PUT: 내 정보 수정, DELETE: 회원 탈퇴
    path('liked-contests/', views.liked_contests, name='liked_contests'), # GET : 내가 찜한 공모전 전체 조회

    # 세션 유지(로그인 상태) 확인
    path('session-check/', views.session_check, name='session_check'), # GET : 현재 사용자의 로그인 상태 확인 (프론트엔드에서 로그인 유지 여부 확인)
]

"""
# views.py
# 참고, swagger 주석
@api_view(['POST'])
@extend_schema(summary='회원가입', description='일반 회원가입 API')
def signup(request):
    ...
"""
"""
import login as auth_login
"""