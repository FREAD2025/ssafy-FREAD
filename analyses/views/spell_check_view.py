# analyses/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

# utils.py에서 hanspell 사용하는 함수 임포트 (경로 및 이름 확인 필요)
from ..utils.spellcheck_utils import call_hanspell_spell_checker
# Serializers 임포트
from ..serializers import SpellCheckRequestSerializer, SpellCheckResponseSerializer
# ... (다른 Analysis, Fread, Sentence 관련 View 및 Serializer 임포트는 그대로 유지) ...

# 맞춤법 검사 (POST /api/v1/analyses/spellcheck/)
@extend_schema(
    summary="맞춤법 검사",
    description="입력된 텍스트의 맞춤법을 검사하고 교정된 결과를 반환합니다. (DB 저장 X, 네이버 맞춤법 검사기 사용)",
    request=SpellCheckRequestSerializer,
    responses={
        status.HTTP_200_OK: SpellCheckResponseSerializer,
        status.HTTP_400_BAD_REQUEST: {"description": "잘못된 요청 데이터 (예: 텍스트 누락)"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "외부 맞춤법 검사 API 호출 실패 또는 서버 오류"},
    }
)
@api_view(["POST"])
@permission_classes([AllowAny]) # 누구나 사용 가능
def spellcheck(request): # API 설계도에 맞게 함수 이름 사용
    request_serializer = SpellCheckRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    original_text = request_serializer.validated_data["original_text"]
    # request_serializer.validated_data 예시
    # {
    #     "original_text": "오늘 날씨가 마니 추워요."
    # }

    # utils 함수를 통해 hanspell 맞춤법 검사 수행
    spell_check_result = call_hanspell_spell_checker(original_text)
    # spell_check_result 예시
    # {
    #     'corrected_text_plain': '오늘 날씨가 많이 추워요.',
    #     'corrected_text_html': '오늘 날씨가 <span class="red_text">많이</span> 추워요.',
    #     'errors_count': 1
    # }
    
    if spell_check_result is None: # utils 함수에서 None 반환 시
        return Response(
            {"detail": "맞춤법 검사 서비스를 처리하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # 글자 수 계산 (공백 포함)
    original_word_count_with_spaces = len(original_text)
    corrected_word_count_with_spaces = len(spell_check_result.get('corrected_text_plain', ''))

    response_result = {
        'original_text': original_text,
        'corrected_text_plain': spell_check_result.get('corrected_text_plain', ''),
        'corrected_text_html': spell_check_result.get('corrected_text_html', ''),
        'errors_count': spell_check_result.get('errors_count', 0),
        'original_word_count_with_spaces': original_word_count_with_spaces,
        'corrected_word_count_with_spaces': corrected_word_count_with_spaces,
    }
    # response_result 예시
    # {
    #     'original_text': '오늘 날씨가 마니 추워요.',
    #     'corrected_text_plain': '오늘 날씨가 많이 추워요.',
    #     'corrected_text_html': '오늘 날씨가 <span class="red_text">많이</span> 추워요.',
    #     'errors_count': 1,
    #     'original_word_count_with_spaces': 13,
    #     'corrected_word_count_with_spaces': 13
    # }

    response_serializer = SpellCheckResponseSerializer(data=response_result)
    response_serializer.is_valid(raise_exception=True) # 맞춤법 검사 결과 데이터 유효성 검사

    return Response(response_serializer.data, status=status.HTTP_200_OK)

# ... (다른 Fread, Sentence 관련 View 함수들은 이전 코드 유지) ...