# analyses/utils.py (또는 analyses/utils/spellcheck_utils.py)

from analyses.hanspell import spell_checker  # 경로 확인 필요!

# 프로젝트 구조에 따라 from ..hanspell import spell_checker 가 될 수도 있음

from analyses.hanspell.constants import CheckResult
import re
import json


# hanspell의 글자 수 제한(500자)에 맞춰 텍스트를 분할하여 리스트를 반환하는 함수
# 안전하게 400자로 분할하자
def split_text_for_hanspell(original_text, max_len=400):
    """
    hanspell의 글자 수 제한(500자)에 맞춰 텍스트를 분할합니다.
    문장 종결 부호(.!?)를 우선으로 분할하고, 없으면 max_len에서 자릅니다.
    """
    text_to_split = original_text
    text_list = []

    start_index = 0

    while start_index < len(text_to_split):  # 남은 텍스트가 있으면
        # 남은 텍스트가 max_len보다 짧거나 같으면 그대로 추가
        if len(text_to_split[start_index:]) <= max_len:
            text_list.append(text_to_split[start_index:])
            break

        # max_len 범위 내에서 문장 종결 부호 찾기
        chunk_candidate = text_to_split[start_index : start_index + max_len]
        sentence_break_last_index = -1

        # 뒤에서부터 문장 종결 부호 검색
        for i in range(len(chunk_candidate) - 1, -1, -1):
            if chunk_candidate[i] in [".", "!", "?"]:
                sentence_break_last_index = i
                break

        # 만약 문장 종결 부호를 찾았다면
        if sentence_break_last_index != -1:
            # 문장 종결 부호 기준으로 자르기
            text_list.append(chunk_candidate[: sentence_break_last_index + 1])
            start_index += (
                sentence_break_last_index + 1
            )  # 그 다음부터 다시 글자 수 확인
        else:  # 문장 종결 부호가 없다면 max_len에서 자른 chunk_candidate 삽입
            text_list.append(chunk_candidate)
            start_index += max_len

    return text_list


# 처음 <content> 태그와 마지막 </content> 태그는 남기고 중간 태그는 제거
def merge_content_tags(html_text):
    # 처음 <content> 태그 찾기
    start_content = re.search(r"<content>", html_text)
    end_content = re.search(r"</content>\s*$", html_text)

    # 중간의 <content> 태그만 제거
    if start_content and end_content:
        start_pos = start_content.end()
        end_pos = end_content.start()
        middle_text = html_text[start_pos:end_pos]

        # 중간의 중복된 <content> 태그 제거
        middle_text = re.sub(r"</?content>", "", middle_text)

        # 최종 결과 생성
        result_text = html_text[:start_pos] + middle_text + html_text[end_pos:]
        return result_text

    return html_text


# 맞춤법 검사를 수행하는 함수
def call_hanspell_spell_checker(original_text):
    """
    Serializer에 맞춰 아래와 같은 형태로 반환함
    Returns:
        dict: {
                'corrected_text_plain': str,
                'corrected_text_html': str, # 교정 부분이 <span> 태그로 하이라이트된 HTML
                'errors_count': int
              }
        None: 오류 발생 시
    """
    total_result = {
        "result": True,
        "original": "",
        "checked": "",
        "errors": 0,
        "time": 0.0,
        "words": {},
        "html": "",
    }
    text_list = split_text_for_hanspell(original_text)
    # full_corrected_html_parts = []

    if not text_list: # 입력 텍스트가 비어있거나 공백만 있는 경우
        return {
            "corrected_text_plain": original_text,
            "corrected_text_html": original_text.replace('\n', '<br>'), # 원본을 HTML 형식으로
            "errors_count": 0,
        }

    try:
        for chunk in text_list:
            if not chunk.strip(): # 빈 청크는 continue
                continue

            # spell_checker.check()는 (Checked 객체, 교정된 HTML 문자열) 튜플 반환
            # Checked 객체: original, checked, errors 등
            # html_output: 교정 부분이 <span> 태그로 감싸진 HTML
            check_result_tuple = spell_checker.check(chunk)

            if not check_result_tuple or len(check_result_tuple) != 2 or not hasattr(check_result_tuple[0], 'checked'):
                # hasattr : 객체(check_result_tuple[0])가 'checked'라는 속성을 가지고 있는지 확인
                
                # hanspell이 정상적인 결과를 반환하지 못한 경우 (예: passportKey 문제)
                print(f"spell_checker 처리 오류 (결과 없음 또는 형식 오류): {chunk[:50]}...")
                # HTML 출력을 위해 원본의 개행을 <br>로 변경
                # full_corrected_html_parts.append(chunk.replace("\n", "<br>"))
                raise Exception("Hanspell 청크 처리 중 오류 발생") # 루프 중단
                # continue  # 다음 청크로

            now_result = check_result_tuple[0]  # Checked 객체
            now_html = check_result_tuple[1]  # 교정된 HTML 문자열

            total_result["original"] += now_result.original
            total_result["checked"] += now_result.checked
            total_result["errors"] += now_result.errors
            total_result["words"].update(now_result.words)
            total_result["time"] += now_result.time
            total_result["html"] += now_html

        

        total_result["html"] = merge_content_tags(total_result["html"])
        print(total_result)
        return {
            "corrected_text_plain": total_result["checked"],
            "corrected_text_html": total_result["html"],
            "errors_count": total_result["errors"],
        }

        # 기능 정의서: "교정된 문장에 교정된 부분을 텍스트 색으로 표시"
        # -> `final_corrected_html`이 이 역할을 함
    except Exception as e:  # 네이버 서비스 점검, passportKey 획득 실패, 네트워크 오류 등 다양한 예외 가능
        print(f"맞춤법 검사 중 오류 발생 (call_hanspell_spell_checker): {str(e)}")
        return None # 오류 발생 시 None 반환