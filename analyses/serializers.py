from rest_framework import serializers
from .models import Analysis, FreadAnalysis, SentenceAnalysis

# 특정 유저의 통합분석내역 전체 리스트 (GET)
class AnalysisListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ('id', 'analysis_type', 'title', 'original_text', 'word_count', 'created_at',)

# 통합 분석 내역 생성 (POST)
class AnalysisCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ('id', 'user', 'original_text',)
        read_only_fields = ('id', 'user')

# Fread 분석 결과 (GET)
class FreadAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreadAnalysis
        fields = ('total', 'logic', 'appeal', 'focus', 'simplicity', 'popularity', 'ai_comments_data', 'solutions_data',)


# 문장 개선 결과 (GET)
class SentenceAnalysisSerializer(serializers.ModelSerializer):
   class Meta:
        model = SentenceAnalysis
        fields = ('sentences_to_fix', 'suggestions_and_result', 'improved_full_text', 'final_word_count',)


# 맞춤법 검사 생성 (POST)
class GrammerCheckCreateSerializer(serializers.Serializer):
    original_text = serializers.CharField(
        max_length=5000,
        required=True,
        allow_blank=False,
        help_text='검사할 텍스트 (최대 5000자)'
    )


# 맞춤법 검사 결과 (GET)
class GrammerCheckSerializer(serializers.Serializer):
    sentences_to_fix = serializers.JSONField(
        max_length=5000,
        required=True,
        allow_blank=False,
        help_text='교정 필요 문장 정보 (JSON)')
    
    word_count = serializers.IntegerField(help_text='글자 수 (공백 포함)')
    
    improved_full_text = serializers.CharField(
        max_length=6000,
        required=True,
        allow_blank=False,
        help_text='교정 완료된 전문')
    
    final_word_count = serializers.IntegerField(help_text='최종 글자 수 (공백 포함)')
