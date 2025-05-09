import json
import requests
import openai
from django.conf import settings
from pydantic import BaseModel, conlist, Field  # 데이터 유효성검사 + 자동 타입 변환

openai_api_key=settings.OPENAI_API_KEY

# 분석 제목 생성 (gpt 호출) ===============================================================================================================
def generate_title_from_gpt(original_text, analyze_result): # (원본 텍스트 300자, 분석 결과)
    class CommentResponseModel(BaseModel):
        comments: conlist(str, min_items=5, max_items=5)    # type: ignore # 문자열(댓글) 5개로 이루어진 리스트여야 함

    prompt = f"원본 텍스트: { original_text }, 분석 결과: { analyze_result }"

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        당신은 제공되는 원본 텍스트와 분석 결과를 바탕으로  생성하여 JSON 형식으로 반환하는 AI입니다.

                        - 각 댓글은 한 줄이며, 이모티콘을 포함해야 합니다.
                        - 각 댓글은 {age}대 {gender} 독자의 말투, 감정, 관심사를 고려하여 작성되어야 합니다.
                        - 현실적인 한국인이 작성할 만한 어투와, 내용이어야 합니다.
                        - 댓글은 문장 하나로 끝내야 하며, 너무 짧지도 길지도 않아야 합니다.

                        📥 반드시 아래 JSON 형식으로만 응답하세요:

                        {{
                            "comments": [
                                "아니 진짜 웃기긴 한데 주인공 좀 답답함🤔",
                                "뭔가 작가님이 하신 남주 묘사 보면 엄청 잘생겼을거같지 않음??😍",
                                ...
                            ]
                        }}

                        🛑 **중요 제약 조건**:

                        - **댓글은 반드시 5개여야 하며**, 4개 또는 6개는 절대 허용되지 않습니다.
                        - 현실적인 한국인이 작성할 만한 어투와, 내용이어야 합니다.
                        - **null, 빈 문자열, 생략된 key**는 절대 허용되지 않습니다.
                        - 시스템은 응답을 파싱하여 자동 처리하므로, 위 조건을 어기면 서비스가 실패합니다.
                    """
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=2040,
            temperature=0.5,
        )

        list_response = response.choices[0].message.content.strip()
        # print(list_response)

        data = json.loads(list_response)    # JSON 파싱 (JSON -> dict)
        validated = CommentResponseModel(comments=data) # Pydantic 모델로 유효성 검사 및 구조화
        return validated.comments   # dict 반환
    
    except Exception as e:
        print(f"GPT 댓글 생성 에러: {age}, {gender}", e)
        return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."