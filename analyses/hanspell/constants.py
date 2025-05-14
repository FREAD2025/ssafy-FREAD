base_url = 'https://m.search.naver.com/p/csearch/ocontent/util/SpellerProxy'


class CheckResult:
    PASSED = 0 # 맞춤법 검사 결과 문제가 없음
    WRONG_SPELLING = 1 # 맞춤법에 문제가 있음
    WRONG_SPACING = 2 # 띄어쓰기에 문제가 있음
    AMBIGUOUS = 3 # 표준어가 의심됨
    STATISTICAL_CORRECTION = 4 # 통계적 교정에 따른 구절

