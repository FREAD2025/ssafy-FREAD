from django.contrib import admin
from .models import Genre, User
# Register your models here.

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(User)  # User 모델 등록 + 커스터마이징
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'name', 'is_active', 'is_social') # 목록 테이블에 보여줄 필드 지정
    list_filter = ('is_active', 'is_social', 'author_status') # 우측에 필터 박스를 생성
    search_fields = ('username', 'email', 'name') # 상단에 검색창 생성
    readonly_fields = ('date_joined', 'last_login')  # 읽기 전용 필드 지정 (수정 불가)
    ordering = ('-date_joined',)  # 최근 가입 순 정렬
    list_per_page = 20  # 한 페이지에 20명씩 보기

