from django.db import models

# Create your models here.
class Contest(models.Model):
    # 공모전 제목
    title = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='제목'
    )
    # 주최사
    organizer = models.CharField(
        max_length=100,
        blank=False,
        verbose_name='주최사'
    )
    # 시작일
    start_date = models.DateField(
        blank=False,
        verbose_name='시작일'
    )
    # 마감일
    end_date = models.DateField(
        blank=False,
        verbose_name='마감일'
    )
    # 참여 대상
    target_audience = models.TextField(
        blank=False, verbose_name='참여 대상'
    )
    # 상금 제공 유무
    has_prize = models.BooleanField(
        blank=False,
        default=False,
        verbose_name='상금 제공 유무'
    )
    # 상금 정보
    prize_details = models.TextField(
        blank=True, # 선택 입력
        null=False,
        verbose_name='상금 정보'
    )
    # 상세 정보 URL
    details_url = models.URLField(
        blank=True, # 선택 입력
        null=False,
        verbose_name='상세 정보 URL'
    )
    # 이미지
    image = models.ImageField(
        blank=True, # 선택 입력
        null=False,
        upload_to='contest_images/',
        verbose_name='상세 이미지'
    )
    # 등록일
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='등록일'
    )
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['end_date']           # 마감일 순으로 정렬
        verbose_name = '공모전'            # admin, 폼 등에서 표시되는 이름
        verbose_name_plural = '공모전 목록' # 복수형일 때 표시될 이름