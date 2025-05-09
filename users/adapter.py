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

    # (선택 사항) 카카오로부터 받은 username(닉네임)을 User 모델의 username으로 기본 설정
    # 이 경우, 추가 정보 입력 시 사용자가 이 username을 확인/수정하게 됩니다.
    # if sociallogin.account.provider == 'kakao':
    #     kakao_data = sociallogin.account.extra_data
    #     nickname = kakao_data.get('properties', {}).get('nickname')
    #     if nickname and not user.username: # 기본 username이 없거나 비어있을 경우
    #         # username 중복을 피하기 위한 간단한 처리 (실제로는 더 견고한 로직 필요)
    #         # 예: nickname + provider_id[:4] 등
    #         potential_username = nickname
    #         # User 모델의 username 필드의 unique=True 제약조건을 고려해야 함
    #         # 실제 구현 시 User.objects.filter(username=potential_username).exists() 체크 필요
    #         user.username = potential_username # 이 부분은 중복 가능성 때문에 신중해야 함


# settings.py에 설정 필요
# SOCIALACCOUNT_ADAPTER = 'users.adapter.CustomSocialAccountAdapter'

"""
adapter.py를 안쓰고 싶다면 현재는 카카오 로그인만 구현하고 있기에
views.py에
user.is_social = True
user.social_provider = 'kakao'
작성해주면 됨
"""
