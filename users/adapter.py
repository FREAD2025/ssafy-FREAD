# adapter.py:소셜 로그인을 통해 회원가입한 사용자에 대해
# 추가 설정이나 필드 저장을 하고 싶을 때 사용함
# is_social, social_provider를 설정하기 위해 추가함
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    # 소셜 로그인 직후 호출되는 함수
    # Django allauth가 새 유저를 생성한 후 실행됨
    def save_user(self, request, sociallogin, form=None):
        # 소셜 로그인으로 받은 정보를 user 모델에 채우기
        user = super().save_user(request, sociallogin, form)
        user.is_social = True
        user.social_provider = sociallogin.account.provider  # 'kakao'
        user.save()
        return user
    
    # 로그인 성공 후 유저 상태에 따라 리디렉션 
    def authentication_success_url(self, request):
        user = request.user

        # 소셜 로그인 후, 아직 추가 정보를 입력하지 않은 경우
        if not user.is_profile_completed:
            return '/api/v1/users/social/extra-info/'  # 프론트에서 해당 경로로 라우팅하여 사용자에게 추가 입력 폼 보여주기
        # 소셜 로그인 성공 후 리디렉션된 URL
        return super().authentication_success_url(request) # settings.py의 LOGIN_REDIRECT_URL 참조 
    
# settings.py에 설정 필요
# SOCIALACCOUNT_ADAPTER = 'users.adapter.CustomSocialAccountAdapter'

"""
adapter.py를 안쓰고 싶다면 현재는 카카오 로그인만 구현하고 있기에
views.py에
user.is_social = True
user.social_provider = 'kakao'
작성해주면 됨
"""