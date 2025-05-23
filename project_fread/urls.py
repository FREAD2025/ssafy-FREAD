"""
URL configuration for project_fread project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from users.views import get_auth_token
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/analyses/", include("analyses.urls")),
    path("api/v1/contests/", include("contests.urls")),
    # allauth URL 포함 (카카오 소셜 로그인)
    path("accounts/", include("allauth.urls")),
    # Spectacular API 스키마 URL
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Spectacular Swagger UI URL
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Spectacular Redoc UI URL
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # 토큰 인증 설정
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    # 회원가입도 설정한다면
    # path('api/v1/auth/signup/', include('dj_rest_auth.registration.urls'))
]


class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter


# 개발 환경에서 Media 파일 및 Static 파일 제공
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path("api/v1/users/get-token/", get_auth_token, name="get-auth-token"),
    path("api/v1/auth/social/kakao/", KakaoLogin.as_view(), name="kakao_login"),
]
