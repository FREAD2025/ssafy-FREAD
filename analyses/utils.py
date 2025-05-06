import json
import requests
import openai
from pathlib import Path
from django.conf import settings
from pydantic import BaseModel, Field  # 데이터 유효성검사 + 자동 타입 변환


openai_api_key=settings.OPENAI_API_KEY

# 분야별 점수 계산
def generate_fread_analysis_score(original_text):
    class FreadAnalysisCriteria(BaseModel):
        logic: int = Field(..., gt=0, le=100)
        appeal: int = Field(..., gt=0, le=100)
        focus: int = Field(..., gt=0, le=100)
        simplicity: int = Field(..., gt=0, le=100)
        popularity: int = Field(..., gt=0, le=100)

        @property
        def total(self) -> float:
            return round(   # total은 소수점 첫째자리까지 계산.
                (self.logic + self.appeal + self.focus + self.simplicity + self.popularity) / 5, 1
            )
        
    prompt = original_text

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                        당신은 텍스트를 정량적으로 분석하여 다섯 가지 항목에 대해 점수를 매겨 JSON 형식으로 응답하는 AI 평가자입니다.

                        각 항목은 다음과 같으며, 각각 1~100점 사이의 **정수형 숫자**로만 점수를 부여해야 합니다.  
                        절대로 소수점이나 범위, 텍스트가 아닌 **정수만 응답하세요.**

                        ---

                        📊 평가 항목 및 기준 (각 항목당 1~100점, 정수):

                        1. logic (설득력, Persuasiveness)  
                        - 글이 독자에게 얼마나 논리적으로 납득될 수 있는가를 평가합니다.  
                        - 주장과 근거가 명확하게 연결되어 있는가?  
                        - 글 전체의 전개가 논리적 순서를 따르고 있는가?  
                        - 불필요한 감정적 호소 없이 논리 자체로 설득력을 갖추었는가?  
                        - 반론 가능성을 인지하고 이를 자연스럽게 다뤘는가?

                        2. appeal (전달력, Clarity & Relatability)  
                        - 텍스트가 독자에게 의미를 분명하게 전달하고, 감정적 공감을 이끌어내는 정도를 평가합니다.  
                        - 핵심 메시지가 명확하게 표현되어 있는가?  
                        - 비유, 예시, 구체적 언어를 통해 의미가 쉬운가?  
                        - 독자의 입장에서 감정 이입이 가능한가?  
                        - 복잡한 내용을 쉽게 풀어 쓰려는 노력이 있는가?

                        3. focus (몰입도, Immersion)  
                        - 글의 흐름이 자연스럽고 독자가 집중력을 유지하며 읽을 수 있는지를 평가합니다.  
                        - 흥미로운 전개, 긴장감, 또는 궁금증 유발이 있는가?  
                        - 중간에 산만하거나 늘어지는 부분 없이 집중이 유지되는가?  
                        - 묘사나 이야기의 리듬이 매끄러운가?  
                        - 서사적 흡인력 또는 논리적 일관성이 몰입을 유도하는가?

                        4. simplicity (문장 간결성, Conciseness & Structure)  
                        - 문장이 군더더기 없이 핵심을 전달하고, 구조적으로 정돈되어 있는지를 평가합니다.  
                        - 불필요한 수식이나 중복 표현이 제거되어 있는가?  
                        - 문장이 너무 길거나 복잡하지 않고, 적절하게 끊어지는가?  
                        - 단락 구성이 적절하며, 각 문장이 자연스럽게 이어지는가?  
                        - 전체적으로 읽기에 부담 없이 깔끔한 흐름을 가지는가?

                        5. popularity (대중성, Mass Appeal)  
                        - 텍스트가 다양한 연령과 배경의 독자에게 공감과 이해를 줄 수 있는지를 평가합니다.  
                        - 특정 계층만 이해할 수 있는 전문 용어나 문화적 맥락이 없는가?  
                        - 주제와 표현이 보편적이며, 대중적 취향을 반영하는가?  
                        - 글이 너무 특수하거나 실험적이지 않고, 넓은 독자층이 읽기에 부담이 없는가?  
                        - 소통하려는 태도가 드러나는가?


                        📥 반드시 아래 JSON 형식으로만 응답하세요:

                        {
                        "logic": 85,
                        "appeal": 90,
                        "focus": 88,
                        "simplicity": 92,
                        "popularity": 86
                        }

                        - 모든 값은 1~100 사이의 **정수**여야 합니다.
                        - 절대로 설명, 소수점, 기타 텍스트를 포함하지 마세요.
                        - JSON 외에는 아무것도 출력하지 마세요.
                        - 한 항목이라도 빈 값이 나와서는 안됩니다. 반드시 값을 계산해내야 합니다.

                        ---

                        🛑 중요 제약 조건:

                        - 위 다섯 항목 **전부 반드시 포함**되어야 하며, **하나라도 누락되면 안 됩니다.**
                        - **null, 빈 문자열, 생략, 생략된 key** 는 절대 허용되지 않습니다.
                        - 모든 항목의 값은 **반드시 유효한 1~100 사이의 정수**여야 합니다.
                        - **절대로 JSON 이외의 텍스트(설명, 해석, 서문 등)를 포함하지 마세요.**
                        - 시스템은 응답을 파싱하여 자동 처리하므로, 위 조건을 지키지 않으면 오류가 발생합니다.
                    """,
                },
                {"role": "user", "content": prompt},
            ],
            # response_format=FreadAnalysisCriteria,
            max_tokens=2040,
            temperature=0.5,
        )

        json_response = response.choices[0].message.content.strip()
        print(json_response)

        data = json.loads(json_response)    # JSON 파싱 (JSON -> dict)
        validated = FreadAnalysisCriteria(**data)  # Pydantic 모델로 검증 및 구조화
        return validated
    
    except Exception as e:
        print("GPT 분석 점수 생성 에러:", e)
        return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."
    


# 예상 댓글 생성
'''
{
age:
gender:
content:
}'''

def add_image_and_nickname(age, gender):
    return image_and_nickname

def generate_total_comments(comments_contents):
    return total_comments

comments_contents = []

def gpt(original_text, age, gender):
    prompt = original_text

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        당신은 {age}대 {gender} 독자 5명이 소설 한 편을 읽은 후 남길 실제 댓글을 생성하여 리스트로 반환하는 AI입니다.

                        - 각 댓글은 한 줄이며, 이모티콘을 포함해야 합니다.
                        - 각 댓글은 {age}대 {gender} 독자의 말투, 감정, 관심사를 고려하여 작성되어야 합니다.
                        - 현실적인 한국인이 작성할 만한 어투와, 내용이어야 합니다.
                        - 댓글은 문장 하나로 끝내야 하며, 너무 짧지도 길지도 않아야 합니다.

                        📥 반드시 아래 리스트 형식으로만 응답하세요:

                        [
                            "아니 진짜 웃기긴 한데 주인공 좀 답답함🤔",
                            "뭔가 작가님이 하신 남주 묘사 보면 엄청 잘생겼을거같지 않음??😍", 
                            ...
                        ]

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
        print(list_response)

        data = json.loads(list_response)    # JSON 파싱 (JSON -> list)
        return data
    
    except Exception as e:
            print("GPT 댓글 생성 에러:", e)
            return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."
    
    

def generage_ai_comments(original_text):
    all_comments = []

    for age in [10, 20, 30, 40, 50]:
        for gender in ["male", "female"]:
            try:
                contents = call_gpt(original_text, age, gender)
                for content in contents:
                    profile = get_random_profile(gender)
                    all_comments.append({
                        "age": age,
                        "gender": gender,
                        "nickname": profile["nickname"],
                        "profile_image": profile["profile_image"],
                        "content": content
                    })
            except Exception as e:
                print(f"댓글 생성 실패 ({age}, {gender}):", e)

    return all_comments
