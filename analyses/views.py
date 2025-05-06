# from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Analysis, FreadAnalysis, SentenceAnalysis
from .serializers import AnalysisCreateSerializer, AnalysisListSerializer, FreadAnalysisSerializer, SentenceAnalysisSerializer, GrammerCheckCreateSerializer, GrammerCheckSerializer
from .utils import generate_fread_analysis_score

# 통합 분석 내역 (GET)
def analysis(request):
    return

# 프리드 분석 (GET, POST)
class FreadAnalysisView(APIView):
    def get(self, request):
        return
    
    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data)    # 사용자 입력값(original_text) 반영
        if serializer.is_valid():
            serializer.save(user=request.user, analysis_type=Analysis.FREAD)  # user, analysis_type필드 채워주기
            
            # 점수 계산 결과 불러오기
            score_data = generate_fread_analysis_score(request.data)

            # 만약 gpt가 점수 데이터를 잘 못 생성했다면
            if isinstance(score_data, str): 
                return Response({'error_message': score_data}, status=status.HTTP_400_BAD_REQUEST)  # 넘어온 문자열(에러메시지)을 번환
            
            # 모든 데이터가 잘 생성됐다면
            FreadAnalysis.objects.create(
                analysis_id=analysis,  # OneToOneField 연결
                total=score_data.total,
                logic=score_data.logic,
                appeal=score_data.appeal,
                focus=score_data.focus,
                simplicity=score_data.simplicity,
                popularity=score_data.popularity,
                # ai_comments_data=ai_comments,
                # solutions_data=score_data.solutions,
)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 문장 개선
def sentence_analysis(request):
    return

# 맞춤법 검사
def spellcheck(request):
    return