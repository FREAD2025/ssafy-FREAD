# from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import asyncio

from .models import Analysis, FreadAnalysis, SentenceAnalysis
from .serializers import AnalysisCreateSerializer, AnalysisListSerializer, FreadAnalysisSerializer, SentenceAnalysisSerializer, GrammerCheckCreateSerializer, GrammerCheckSerializer
from .utils.generate_fread_analysis import generate_fread_analysis_score, generate_fread_ai_comments, generate_fread_solutions

# 통합 분석 내역 (GET)
def analysis(request):
    return

# 프리드 분석 (GET, POST)
class FreadAnalysisView(APIView):
    def get(self, request):
        return
    
    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        analysis = serializer.save()  # Analysis 생성 (자동으로 user, analysis_type, title, original_text 포함)
            
        # GPT 점수 데이터 생성
        score_data = generate_fread_analysis_score(original_text)
        
        # GPT ai_comments 생성
        ai_comments = generate_fread_ai_comments(original_text)

        # GPT solution 생성
        solutions_data = generate_fread_solutions(original_text)

        
        # 만약 gpt가 점수 데이터를 잘 못 생성했다면 (객체가 와야 하는데, 문자열(에러메시지)이 왔다면)
        if isinstance(score_data, str): 
            return Response({'error_message': score_data}, status=status.HTTP_400_BAD_REQUEST)  # 넘어온 문자열(에러메시지)을 클라에게 반환

        # 만약 gpt가 ai_comments 데이터를 잘 못 생성했다면 (딕셔너리가 와야 하는데, 문자열(에러메시지)이 왔다면)
        if isinstance(ai_comments, str): 
            return Response({'error_message': ai_comments}, status=status.HTTP_400_BAD_REQUEST)  # 넘어온 문자열(에러메시지)을 클라에게 반환
        
        # 만약 gpt가 solution 데이터를 잘 못 생성했다면 (딕셔너리가 와야 하는데, 문자열(에러메시지)이 왔다면)
        if isinstance(solutions_data, str): 
            return Response({'error_message': ai_comments}, status=status.HTTP_400_BAD_REQUEST)  # 넘어온 문자열(에러메시지)을 클라에게 반환
        
        # 모든 데이터가 잘 생성됐다면
        FreadAnalysis.objects.create(
            analysis_id = analysis,  # OneToOneField 연결
            total = score_data.total,
            logic = score_data.logic,
            appeal = score_data.appeal,
            focus = score_data.focus,
            simplicity = score_data.simplicity,
            popularity = score_data.popularity,
            ai_comments_data = ai_comments,
            # solutions_data=score_data.solutions,
)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 문장 개선
def sentence_analysis(request):
    return

# 맞춤법 검사
def spellcheck(request):
    return