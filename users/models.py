from django.db import models
from django.contrib.auth.models import AbstractUser
from contests.models import Contest


# Create your models here.
class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,  # 장르명은 중복 불가
        verbose_name="장르명",  # 관리자 페이지 등에서 표시될 이름
    )

    def __str__(self):
        return self.name

    class Meta:  # 모델의 메타데이터 정의
        verbose_name = "장르"  # admin, 폼 등에서 표시되는 이름
        verbose_name_plural = "장르 목록"  # 복수형일 때 표시될 이름
        ordering = [
            "name"
        ]  # 이름 오름차순 정렬 # Genre.objects.all() 했을 때, 정렬 기준


# 장르 종류
# ('로맨스'),
# ('판타지'),
# ('SF/공상 과학'),
# ('미스터리 / 스릴러'),
# ('에세이'),
# ('시'),


class User(AbstractUser):
    # AbstractUser에서 상속 받는 필드
    # id, username, password, date_joined, last_login, is_active, is_staff, is_superuser
    # 이메일 (오버라이드)
    email = models.EmailField(unique=True, verbose_name="이메일 주소")  # 중복 불가
    # AbstractUser의 기본 필드 중 사용 안 함
    first_name = None
    last_name = None
    # 이름 (오버라이드)
    name = models.CharField(max_length=100, verbose_name="이름")
    # 전화번호
    phone_number = models.CharField(
        max_length=15, blank=True, verbose_name="전화번호"  # 선택 사항
    )
    # 장르 (다중 선택)
    genres = models.ManyToManyField(
        Genre,
        help_text="어떤 장르의 글을 가장 많이 쓰시나요? (최대 3개 선택 가능)",
        related_name="users",  # Genre 모델에서 User를 역참조할 때 사용할 이름
        verbose_name="주력 장르",
    )
    # 작가 상태 (선택지 중 택일)
    STATUS_CHOICES = [
        ("none", "아직 작가 활동은 안 해봤어요"),
        ("aspiring", "작가를 준비하고 있어요 (지망생)"),
        ("hobbyist", "취미로 글을 쓰고 있어요"),
        ("semi_pro", "연재 또는 상업 활동 중이에요"),
        ("professional", "전업 작가입니다"),
    ]
    author_status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        help_text="작가님의 글쓰기 경험을 알려주세요",
        verbose_name="작가 경력",
    )
    # 프로필 이미지
    profile_image = models.ImageField(
        upload_to="profile_pics/",  # MEDIA_ROOT/profile_pics/ 경로에 저장
        blank=True,  # 선택 사항
        null=True,  # ImageField로 DB에 NULL 값을 저장할 수 있도록 함
        verbose_name="프로필 사진",
    )
    # 소셜 로그인 가입 여부
    is_social = models.BooleanField(
        default=False, verbose_name="소셜 가입 여부"  # 기본 값 = False
    )
    # 소셜 이름
    social_provider = models.CharField(
        default="kakao",  # 기본 값 = 'kakao'
        max_length=20,
        blank=False,
        null=False,
        verbose_name="소셜 이름",
    )
    # 프로필 작성 완료 여부
    is_profile_completed = models.BooleanField(
        default=False,  # 기본 값 = 'False' # is_social과 함께 확인되어야 함
        verbose_name="프로필 작성 완료 여부",
    )
    # 찜한 공모전
    liked_contests = models.ManyToManyField(
        Contest, blank=True, related_name="liked_users", verbose_name="찜한 공모전"
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"


# 중요! settings.py 파일에 AUTH_USER_MODEL = 'users.User' 설정을 꼭 추가해주세요.
# 중요! ImageField를 사용하려면 Pillow 라이브러리를 설치해야 합니다. (pip install Pillow)
