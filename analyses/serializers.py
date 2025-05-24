from rest_framework import serializers
from .models import Analysis, FreadAnalysis
# from .utils.generate_analysis import generate_title_from_gpt

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

    def create(self, validated_data):   # 위의 validate 함수의 결과 데이터가 validated_data로 넘어옴
        # 분석 요청한 user 가져오기
        user = self.context['request'].user

        # 사용자가 입력한 텍스트 가져오기
        original_text = validated_data.get('original_text')

        # 분석 종류 명시
        analysis_type = Analysis.FREAD

        # Analysis 객체 생성 (title은 나중에 설정)
        analysis = Analysis(
            user=user,
            analysis_type=analysis_type,
            original_text=original_text,
        )

        return analysis
    


# Fread 분석 결과 (GET)
class FreadAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreadAnalysis
        fields = ('original_text', 'total', 'logic', 'appeal', 'focus', 'simplicity', 'popularity', 'ai_comments_data', 'solutions_data',)




# # 문장 개선 결과 (GET)
# class SentenceAnalysisSerializer(serializers.ModelSerializer):
#    class Meta:
#         model = SentenceAnalysis
#         fields = ('sentences_to_fix', 'suggestions_and_result', 'improved_full_text', 'final_word_count',)




# 맞춤법 검사 요청 : (POST) /api/v1/analyses/spellcheck/
class SpellCheckRequestSerializer(serializers.Serializer):
    original_text = serializers.CharField(
        max_length=5000, 
        required=True,
        allow_blank=False, 
        help_text='검사할 원본 텍스트 (최대 5000자)'
    )




# 맞춤법 검사 결과 응답 : (GET) /api/v1/analyses/spellcheck/
class SpellCheckResponseSerializer(serializers.Serializer):
    original_text = serializers.CharField(help_text="사용자가 입력한 원본 텍스트")
    corrected_text_plain = serializers.CharField(help_text="맞춤법 교정이 완료된 일반 텍스트")
    corrected_text_html = serializers.CharField(help_text="교정 부분이 HTML 태그(span)로 하이라이트된 텍스트")
    errors_count = serializers.IntegerField(help_text="발견된 총 오류 개수")
    original_word_count_with_spaces = serializers.IntegerField(help_text='원본 글자 수 (공백 포함)')
    corrected_word_count_with_spaces = serializers.IntegerField(help_text='교정 후 글자 수 (공백 포함)')