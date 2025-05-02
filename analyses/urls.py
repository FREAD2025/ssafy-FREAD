from django.urls import path
from .views import AnalysisView
from . import views

urlpatterns = [
    path('', AnalysisView.as_view(), name='통합 분석 결과(GET)'),
    path('fread/', views.aaaa, name='fread 분석 요청(POST)'),
    path('fread/<int:analysis_id>/', views.fread_analysis, name='fread 분석 결과(GET)'),
    path('sentence/', views.sentence_analysis, name='문장 개선하기(POST)'),
    path('sentence/<int:analysis_id>/', views.sentence_analysis, name='문장 개선 결과'),
    path('spellcheck/', views.spellcheck, name='맞춤법 검사'),
]

