from django.db import models
from django.conf import settings

class Analysis(models.Model):

    # 분석 요청한 사용자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name='분석 요청한 사용자'
    )

    # 분석 종류
    FREAD = 'FREAD'
    IMPROVMENT = 'IMPROVMENT'

    ANALYSIS_TYPE_CHOICES = [
        (FREAD, '프리드 분석'),   # 왼쪽:DB 저장값, 오른쪽:우리가 보는 값
        (IMPROVMENT, '문장 개선'),
    ]
    analysis_type = models.CharField(
        max_length=20,
        choices=ANALYSIS_TYPE_CHOICES,
        verbose_name='분석 카테고리'
    )

    # 분석 제목
    title = models.CharField(
        max_length=200,
        blank=True,
        null=False,
        verbose_name='분석 제목'
    )

    # 분석에 쓰인 원본 텍스트
    original_text = models.TextField(
        verbose_name='원본 텍스트'
    )

    # 원본 텍스트 글자수
    word_count = models.IntegerField(
        default=0,
        verbose_name='글자 수 (공백 포함)'
    )

    # 분석 생성 일시
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='분석 생성 일시'
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_analysis_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"
    
    class Meta:
        ordering = ['-created_at']  #.objects.all() 혹은 .objects.filter() 시 created_at 기준으로 정렬되어 가져와짐
        verbose_name = '분석 요청'
        verbose_name_plural = '분석 요청 목록'



class FreadAnalysis(models.Model):
    # PK
    # 통합 분석 모델의 pk를 공유해서 사용한다. 
    analysis_id = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='analysis_result',
        verbose_name='연결된 통합 분석'
    )

    total = models.FloatField(verbose_name='완성도')    # 타 점수들의 평균
    logic = models.IntegerField(verbose_name='설득력 점수')
    appeal = models.IntegerField(verbose_name='전달력 점수')
    focus = models.IntegerField(verbose_name='몰입도 점수')
    simplicity = models.IntegerField(verbose_name='문장 간결성 점수')
    popularity = models.IntegerField(verbose_name='대중성 점수')
    ai_comments_data = models.JSONField(verbose_name='예상 댓글 데이터 (JSON)')
    solutions_data = models.JSONField(verbose_name='솔루션 제안 데이터 (JSON)')

    def __str__(self):
        return f"Fread 분석 결과 (분석 ID: {self.pk})"

    class Meta:
        verbose_name = 'Fread 분석 결과'
        verbose_name_plural = 'Fread 분석 결과 목록'



class SentenceAnalysis(models.Model):
    # PK
    # 통합 분석 모델의 pk를 공유해서 사용한다. 
    analysis_id = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='analysis_result',
        verbose_name='연결된 통합 분석'
    )

    sentences_to_fix = models.JSONField(verbose_name='개선 필요 문장 정보 (JSON)')
    suggestions_and_result = models.JSONField(verbose_name='개선 제안 및 결과 (JSON)')
    improved_full_text = models.TextField(verbose_name='개선 완료된 전문')
    final_word_count = models.IntegerField(verbose_name='최종 글자 수 (공백 포함)')

    def __str__(self):
        return f"문장 개선 결과 (분석 ID: {self.analysis_id})"

    class Meta:
        verbose_name = '문장 개선 결과'
        verbose_name_plural = '문장 개선 결과 목록'