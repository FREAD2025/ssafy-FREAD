from django.urls import path
from .views import analysis_view, spell_check_view
from . import views

urlpatterns = [
    path('', analysis_view.analysis, name='통합 분석 결과(GET)'),
    path('fread/', analysis_view.FreadAnalysisView.as_view(), name='fread 분석 요청(POST)'),
    path('fread/<int:analysis_id>/', analysis_view.FreadAnalysisView.as_view(), name='fread 분석 결과(GET)'),
    # path('sentence/', views, name='문장 개선하기(POST)'),
    # path('sentence/<int:analysis_id>/', views, name='문장 개선 결과'),
    path('spellcheck/', spell_check_view.spellcheck, name='맞춤법 검사'),
]
