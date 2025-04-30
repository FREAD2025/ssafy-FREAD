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
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/analyses/', include('analyses.urls')),
    path('api/v1/contests/', include('contests.urls')),

    # allauth URL 포함 (카카오 소셜 로그인)
    path('accounts/', include('allauth.urls')),

    # Spectacular API 스키마 URL
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Spectacular Swagger UI URL
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Spectacular Redoc UI URL (선택 사항)
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# 개발 환경에서 Media 파일 및 Static 파일 제공
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# settings.py에서 확인 필요
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# 소셜 로그인 등을 위해 설치해야 할 패키지
# pip install djangorestframework
# pip install drf-spectacular
## pip install django-allauth
## pip install Pillow

# settings.py에서 확인해야 할 것들
"""
# 미디어 파일 설정 (이미지 업로드용)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 정적 파일 설정 (Swagger CSS, JS 등 포함)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # collectstatic 용

# Swagger 설정 및 소셜 로그인 구현 시 필요한 앱
INSTALLED_APPS += [
    'rest_framework', # drf
    'drf_spectacular', #  스펙타큘러 추가 -> swagger

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',

    'django.contrib.sites',  # allauth 필수
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # 다른 REST Framework 설정이 있다면 유지합니다.
}

SITE_ID = 1

SPECTACULAR_SETTINGS = {
    'TITLE': '개인 작가 agent 서비스 API', # 서비스 이름 (헤더)
    'DESCRIPTION': '개인 작가 agent 서비스 API 문서입니다.', # 서비스 설명
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # 필요한 다른 Spectacular 설정이 있다면 추가합니다.
}

# 로그인 리디렉션 설정 등도 필요시 추가
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
"""