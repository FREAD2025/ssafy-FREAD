from django.contrib import admin
from .models import Contest

# Register your models here.
# admin.site.register(Contest)
@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    # 목록 페이지에서 보이게 할 필드 지정
    list_display = (
        'title',       # 제목
        'organizer',   # 주최사
        'start_date',  # 시작일
        'end_date',    # 마감일
        'has_prize',   # 상금 유무
        'created_at'   # 등록일
    )
    
    # 목록 페이지에서 필터 기능 추가 (오른쪽 사이드바에 나타남)
    list_filter = (
        'organizer',   # 주최사   
        'has_prize',   # 상금 제공 여부 필터
        'start_date',  # 시작일 기준 필터
        'end_date',    # 마감일 기준 필터
    )

    # 목록 페이지에서 검색 기능 추가
    search_fields = (
        'title',      # 제목으로 검색
        'organizer',  # 주최사로 검색
        'target_audience', # 대상
    )

    # 상세 페이지에서 필드 표시 순서 설정
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'organizer',
                'start_date',
                'end_date',
                'target_audience',
                'has_prize',
                'prize_details',
                'details_url',
                'image'
            )
        }),
    )

    # 읽기 전용 필드 (수정 불가능)
    readonly_fields = ('created_at',)