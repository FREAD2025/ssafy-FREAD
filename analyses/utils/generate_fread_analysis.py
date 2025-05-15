import json
import asyncio  # GPT 호출 비동기적으로 처리
import requests
import openai
from pathlib import Path
from django.conf import settings
from pydantic import BaseModel, conlist, Field  # 데이터 유효성검사 + 자동 타입 변환



openai_api_key=settings.OPENAI_API_KEY

# 분야별 점수 계산 ===============================================================================================================
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
        # print(json_response)

        data = json.loads(json_response)    # JSON 파싱 (JSON -> dict)
        validated = FreadAnalysisCriteria(**data)  # Pydantic 모델로 유효성 검사 및 구조화
        return validated
    
    except Exception as e:
        print("GPT 분석 점수 생성 에러:", e)
        return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."
    


# 예상 댓글 생성 ===============================================================================================================
''' 총 50개 댓글 예상 형태
{
    "10대": {
        "male": [
            {"content": "댓글1"},
            {"content": "댓글2"},
            ...
        ],
        "female": [
            {"content": "댓글1"},
            {"content": "댓글2"},
            ...
        ]
    },
    "20대": {
        "male": [...],
        "female": [...]
    },
    ...
}'''

# 최종 댓글들 50개 + 대표 댓글 5개 리턴
def generate_fread_ai_comments(original_text):
    # 최종 json 데이터 형태
    grouped_ai_comments = {
        "10대": {"male": [], "female": []},
        "20대": {"male": [], "female": []},
        "30대": {"male": [], "female": []},
        "40대": {"male": [], "female": []},
        "50대": {"male": [], "female": []},
    }

    only_contents = []  # 댓글 내용만 있는 리스트 (대표 댓글 생성용)

    # 연령/성별 별 GPT 호출하여 댓글 생성 (5개씩)
    for age in [10, 20, 30, 40, 50]:
        for gender in ["male", "female"]:
            contents = create_ai_comment_content(original_text, age, gender)

            # 에러메시지(str)가 리턴됐다면
            if isinstance(contents, str):
                return contents  # 분석 전체 중단하고 에러메시지 반환

            for content in contents:
                grouped_ai_comments[f"{age}대"][gender].append({"content": content})   # 최종 json 형태로 묶으면서 저장
                only_contents.append(content)   # 대표 댓글 생성을 위해 댓글 내용만 따로 빼서 모으기
                    
    # 대표 댓글 생성
    final_summary_comments = generate_final_summary_comments(only_contents)

    # 에러메시지(str)가 리턴됐다면
    if isinstance(final_summary_comments, str):
        return final_summary_comments  # 분석 전체 중단하고 에러메시지 반환
    
    grouped_ai_comments["대표 댓글"] = final_summary_comments   # 최종적으로 grouped_ai_comments에 대표 댓글도 추가

    return grouped_ai_comments  # 최종 데이터 dict로 반환




# 댓글 내용 생성 (gpt 호출)
def create_ai_comment_content(original_text, age, gender):
    class CommentResponseModel(BaseModel):
        comments: conlist(str, min_items=5, max_items=5)    # type: ignore # 문자열(댓글) 5개로 이루어진 리스트여야 함

    prompt = original_text

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        당신은 {age}대 {gender} 독자 5명이 소설 한 편을 읽은 후 남길 실제 댓글을 생성하여 JSON 형식으로 반환하는 AI입니다.

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

        json_response = response.choices[0].message.content.strip()
        # print(json_response)

        data = json.loads(json_response)    # JSON 파싱 (JSON -> dict)
        validated = CommentResponseModel(comments=data) # Pydantic 모델로 유효성 검사 및 구조화
        return validated.comments   # list 반환
    
    except Exception as e:
        print(f"GPT AI댓글 내용 생성 에러: {age}, {gender}", e)
        return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."
 


    
# 대표 요약 댓글 5개 생성 (gpt 호출)
def generate_final_summary_comments(contents):
    class FinalCommentResponseModel(BaseModel):
        comments: conlist(str, min_items=5, max_items=5)    # type: ignore # 문자열(댓글) 5개로 이루어진 리스트여야 함

    prompt = contents

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        당신은 독자 50명의 댓글을 읽고, 핵심 반응을 5개의 대표 댓글로 요약하여 JSON 형식으로 반환하는 AI입니다.

                        - 댓글을 창조하는 것이 아닌, 기존 댓글들을 분석하여 요약을 해야 합니다.
                        - 기존의 댓글과 내용이 완전히 일치해서는 안됩니다. 
                        - 현실적인 한국인이 작성할 만한 어투와, 내용이어야 합니다.
                        - 각 댓글은 한 줄이며, 이모티콘을 포함해야 합니다.
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

        json_response = response.choices[0].message.content.strip()
        # print(json_response)

        data = json.loads(json_response)    # JSON 파싱 (JSON -> dict)
        validated = FinalCommentResponseModel(comments=data) # Pydantic 모델로 유효성 검사 및 구조화
        return validated.comments   # list 반환
    
    except Exception as e:
        print("GPT 대표 댓글 생성 에러:", e)
        return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."




# 솔루션 생성 ===============================================================================================================
def generate_fread_solutions(original_text):
    class SolutionResponseModel(BaseModel):
        solutions: conlist(str, min_items=3, max_items=3)    # type: ignore # 문자열(댓글) 5개로 이루어진 리스트여야 함

    prompt = original_text

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        당신은 경험 많은 소설 편집자이자 글쓰기 코치입니다. 

                        당신의 역할은 소설 한 편을 읽고, 해당 소설의 완성도를 높일 수 있는 솔루션을 제시하는 것입니다. 

                        솔루션은 아래 기준을 정확히 따릅니다:
                        - 총 3개의 솔루션을 제시합니다.
                        - 각 솔루션은 150자 이내로 간결하게 작성합니다.
                        - 각 솔루션은 명확하고 실용적이어야 하며, 구체적인 예시를 포함합니다. 
                        - 솔루션은 독자가 소설을 더 잘 이해하고 몰입할 수 있도록 돕는 방향으로 작성합니다. 
                        - 아래는 참고할 수 있는 예시일 뿐, 반드시 이 형식으로 작성할 필요는 없습니다.

                        예:
                        - "맞춤법을 더 신경 써 주세요. 예: '아름다워요' → '아름다워요.'"
                        - "캐릭터의 감정을 더 구체적으로 표현해 보세요. 예: '슬펐다' → '눈물이 맺혔다.'"
                        - "배경 묘사를 더 생동감 있게 추가해 보세요. 예: '밤하늘이 어두웠다' → '별빛이 희미하게 반짝였다.'"

                        프롬포트로 전달되는 소설 한 편을 읽고, 이 기준에 맞는 솔루션을 제시하세요.
                        당신은 소설 한 편을 읽고 그 한 편의 소설에 대한 솔루션을 제공하는 


                        📥 반드시 아래 JSON 형식으로만 응답하세요:

                        {{
                            solutions:[
                                "맞춤법을 더 신경 써 주세요. 예: '그녀는 맛있는것을 좋아하게 돼었다.' → '그녀는 맛있는 것을 좋아하게 되었다.'",
                                "캐릭터의 감정을 더 구체적으로 표현해 보세요. 예: '슬펐다' → '눈물이 맺혔다.'",
                                "배경 묘사를 더 생동감 있게 추가해 보세요. 예: '밤하늘이 어두웠다' → '별빛이 희미하게 반짝였다.'"
                            ]
                        }}

                        🛑 **중요 제약 조건**:

                        - **솔루션은 반드시 3개여야 하며**, 2개 또는 4개는 절대 허용되지 않습니다.
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
        validated = SolutionResponseModel(solutions=data) # Pydantic 모델로 유효성 검사 및 구조화
        return validated.solutions   # list 반환
    
    except Exception as e:
        print("GPT 솔루션 생성 에러:", e)
        return "잠시 분석이 원활하지 않았어요. 다시 시도해주세요."