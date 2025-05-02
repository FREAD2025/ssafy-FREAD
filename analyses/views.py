# from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Analysis, FreadAnalysis, SentenceAnalysis
from .serializers import AnalysisCreateSerializer, AnalysisListSerializer, FreadAnalysisSerializer, SentenceAnalysisSerializer, GrammerCheckCreateSerializer, GrammerCheckSerializer

# 통합 분석
class AnalysisView(APIView):
    def get(self, request):
        return
    
    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data)    # 사용자 입력값(original_text) 반영
        
        if serializer.is_valid():
            serializer.save(user=request.user)  # user 필드 채워주기
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            if 요청이 Fread를 통해 들어왔다면
                process_fread_analysis(serializer)
            elif 요청이 sentence를 통해 들어왔다면
                process_sentence_analysis(serializer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 프리드 분석
def fread_analysis(request):
    return

# 문장 개선
def sentence_analysis(request):
    return

# 맞춤법 검사
def spellcheck(request):
    return