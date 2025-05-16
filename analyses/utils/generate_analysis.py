import json
import requests
import openai
from django.conf import settings
from pydantic import BaseModel, Field  # 데이터 유효성검사 + 자동 타입 변환


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

                        솔루션은 아래 기준을 정확히 따릅니다:
                        - **코드 블록(````json`)을 절대 사용할 수 없습니다.**
                        - JSON 형식은 항상 평문(텍스트)으로 작성되어야 하며, 코드 블록이 포함되면 응답은 무효화됩니다.
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
        print(f'analysis - 분석 제목(title) : {json_response}')


        # JSON 파싱 (JSON -> dict)
        try:    # JSON 으로 잘 들어왔는지 확인
            data = json.loads(json_response) 
        except json.JSONDecodeError:
            print("GPT 응답 (analysis - 분석 제목(title)) 이 JSON 형식이 아님:", json_response)
            return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."   
        
        # Pydantic 모델로 유효성 검사
        try:
            validated = CommentResponseModel(**data) 
            return validated   # Pydantic 인스턴스 반환 (추후 디버깅용)
        except ValueError as e:
            print("Pydantic 유효성 검사 (analysis - 분석 제목(title)) 실패:", e)
            return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."
        
    except Exception as e:
        print(f"GPT 통합 분석 제목 생성 에러", e)
        return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."