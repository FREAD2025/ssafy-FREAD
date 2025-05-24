# from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated  # 권한 클래스 (인증된 사용자, 관리자)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# import asyncio

from ..models import Analysis, FreadAnalysis
from ..serializers import AnalysisCreateSerializer, AnalysisListSerializer, FreadAnalysisSerializer
from ..utils.generate_fread_analysis import generate_fread_analysis_score, generate_fread_ai_comments, generate_fread_solutions
from ..utils.generate_analysis import generate_title_from_gpt

# 토큰 인증 설정
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes

# 통합 분석 내역 전체 조회(GET)
@ api_view(['GET'])
@ authentication_classes([TokenAuthentication, BasicAuthentication])
@ permission_classes([IsAuthenticated]) # 로그인한 사용자만 사용 가능
def analysis_list(request):
    analyses = Analysis.objects.filter(user=request.user)
    serializer = AnalysisListSerializer(analyses, many=True)
    return Response(serializer.data)



# 통합 분석 내역 중 1 삭제 (DELETE)
@ api_view(['DELETE'])
@ authentication_classes([TokenAuthentication, BasicAuthentication])
@ permission_classes([IsAuthenticated]) # 로그인한 사용자만 사용 가능
def analysis(request, analysis_id):
    analysis = Analysis.objects.get(pk=analysis_id)
    if analysis.user != request.user:   # 삭제 요청을 보낸 사람이 그 분석의 주인이 아닌 경우
        return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
    analysis.delete()
    print(f"{analysis_id}번 글이 삭제되었습니다.")
    return Response(status=status.HTTP_204_NO_CONTENT)



# 프리드 분석 (GET, POST)
class FreadAnalysisView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 사용 가능

    # 프리드 분석 결과 요청 시
    def get(self, request, analysis_id):
        fread_analysis = FreadAnalysis.objects.get(pk=analysis_id)
        serializer = FreadAnalysisSerializer(fread_analysis)
        return Response(serializer.data)
    

    # 프리드 분석 요청 시
    def post(self, request):
        try:
            # 통합 분석내역 (analysis) 생성
            serializer = AnalysisCreateSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            analysis = serializer.save()  # serializer에서 Analysis 생성 (title 제외) (자동으로 user, analysis_type, title, original_text 포함)
            
            # 사용자가 입력한 원본 텍스트
            original_text = analysis.original_text



            # GPT 점수 데이터 생성 (fread analysis)
            score_data = generate_fread_analysis_score(original_text)
        
            # 만약 gpt가 점수 데이터를 잘 못 생성했다면 (객체가 와야 하는데, 문자열(에러메시지)이 왔다면)
            if isinstance(score_data, str): 
                raise ValueError(score_data)    # 넘어온 문자열(에러메시지)을 except ValueError로 반환

            # gpt가 점수 데이터를 잘 생성했다면, 아까 미뤄뒀던 통합 분석 내역 (analysis)의 title 생성 (점수 데이터를 이용)
            title = generate_title_from_gpt(original_text[:300], score_data)

            # 만약 GPT가 title을 잘 못 생성했다면
            if isinstance(title, str): 
                raise ValueError(title)     # 넘어온 문자열(에러메시지)을 except ValueError로 반환



            # GPT ai_comments 생성 (fread analysis)
            ai_comments = generate_fread_ai_comments(original_text)

            # 만약 gpt가 ai_comments 데이터를 잘 못 생성했다면 (딕셔너리가 와야 하는데, 문자열(에러메시지)이 왔다면)
            if isinstance(ai_comments, str): 
                raise ValueError(ai_comments)     # 넘어온 문자열(에러메시지)을 except ValueError로 반환



            # GPT solution 생성 (fread analysis)
            solutions_data = generate_fread_solutions(original_text)
            
            # 만약 gpt가 solution 데이터를 잘 못 생성했다면 (딕셔너리가 와야 하는데, 문자열(에러메시지)이 왔다면)
            if isinstance(solutions_data, str): 
                raise ValueError(solutions_data)     # 넘어온 문자열(에러메시지)을 except ValueError로 반환
            
            

            # Analysis 객체의 제목 업데이트 (통합분석내역 최종 저장)
            analysis.title = title.title    # 얘는 Pydantic 인스턴스로 넘어왔으므로, title까지 해줘야 접근 가능
            analysis.save()  # 최종 저장


            # 모든 데이터가 잘 생성됐다면 (fread analysis)
            FreadAnalysis.objects.create(
                original_text = original_text,
                analysis_id = analysis,  # OneToOneField 연결
                total = score_data.total,
                logic = score_data.logic,
                appeal = score_data.appeal,
                focus = score_data.focus,
                simplicity = score_data.simplicity,
                popularity = score_data.popularity,
                ai_comments_data = ai_comments,
                solutions_data = solutions_data,
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response({'error_message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:      # 이 예외처리는 예측하지 못한 오류 발생 시 실행됨
            return Response({'error_message': '알 수 없는 오류가 발생했습니다.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    


# # 문장 개선
# def sentence_analysis(request):
#     return
