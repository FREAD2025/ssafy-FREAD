# contests/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.contest_list, name='contest_list'),  # GET: 전체 공모전 리스트 조회, POST: 공모전 등록 (관리자)
    path('<int:contest_id>/', views.contest_detail, name='contest_detail'),  # GET: 공모전 상세 조회, PUT: 공모전 수정 (관리자), DELETE: 공모전 삭제 (관리자)
    path('<int:contest_id>/like/', views.like_contest, name='like_contest'),  # POST: 공모전 찜하기, DELETE: 찜 해제
]