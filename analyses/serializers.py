from rest_framework import serializers
from .models import Analysis, FreadAnalysis, SentenceAnalysis
from .utils.generate_analysis import generate_title_from_gpt

# 특정 유저의 통합분석내역 전체 리스트 (GET)
class AnalysisListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ('id', 'analysis_type', 'title', 'original_text', 'created_at',)



# 통합 분석 내역 생성 (POST)
class AnalysisCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ('id', 'user', 'analysis_type', 'original_text',)
        read_only_fields = ('id', 'analysis_type', 'user')

    def validate(self, data):
        original_text = data.get('original_text')

        if not original_text:
            raise serializers.ValidationError({'error_message': '텍스트가 누락되었습니다.'})

        return data

    def create(self, validated_data):
        # 분석 요청한 user 가져오기
        user = self.context['request'].user

        # 사용자가 입력한 텍스트 가져오기
        original_text = validated_data.get('original_text')

        # GPT를 통해 제목 생성
        title = generate_title_from_gpt(original_text)

        # 분석 종류 명시
        analysis_type = Analysis.FREAD

        # Analysis 객체 생성
        analysis = Analysis.objects.create(
            user=user,
            analysis_type=analysis_type,
            title=title,
            original_text=original_text,
        )

        return analysis
    


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
