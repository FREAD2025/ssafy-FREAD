import json
import requests
import openai
from django.conf import settings
from pydantic import BaseModel, conlist, Field  # 데이터 유효성검사 + 자동 타입 변환

openai_api_key=settings.OPENAI_API_KEY

# 분석 제목(title) 생성 (gpt 호출) ===============================================================================================================
def generate_title_from_gpt(original_text, analyze_result): # (원본 텍스트 300자, 분석 결과)
    class CommentResponseModel(BaseModel):
        title: str    # 제목은 문자열

    prompt = f"원본 텍스트: { original_text }, 분석 결과: { analyze_result }"   # 분석 결과: fread=total 점수, 문장개선=개선점 1개

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        당신은 제공되는 원본 텍스트와 분석 결과를 바탕으로 해당 분석에 대한 제목을 생성하여 JSON 형식으로 반환하는 AI입니다.

                        - 제목은 문장 하나로 끝내야 하며, 너무 짧지도 길지도 않아야 합니다.

                        📥 반드시 아래 JSON 형식으로만 응답하세요:

                        {{
                            "title": "중세 판타지 소설에 대한 85점짜리 분석"
                        }}

                        🛑 **중요 제약 조건**:

                        - **null, 빈 문자열, 생략된 key**는 절대 허용되지 않습니다.
                        - 시스템은 응답을 파싱하여 자동 처리하므로, 위 조건을 어기면 서비스가 실패합니다.
                    """
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=2040,
            temperature=0.5,
        )

        json_response = response.choices[0].message.content.strip()
        # print(json_response)

        data = json.loads(json_response)    # JSON 파싱 (JSON -> dict)
        validated = CommentResponseModel(title=data) # Pydantic 모델로 유효성 검사 및 구조화
        return validated.title   # str 반환
    
    except Exception as e:
        print(f"GPT 통합분석 제목 생성 에러", e)
        return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."