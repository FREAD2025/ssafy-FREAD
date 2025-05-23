from rest_framework import serializers
from .models import Contest
from django.contrib.auth import get_user_model

User = get_user_model()

# 공모전 생성 및 공모전 상세 페이지 등 : POST /api/v1/contests/ 등
class ContestSerializer(serializers.ModelSerializer):
    """
    - 전체 공모전 목록 또는 상세 페이지 등에서 사용된다.
    - 사용자가 공모전을 '찜(like)'했는지 여부를 is_liked 필드로 확인할 수 있다.
    """
    image = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()  # 찜한 사용자 수 계산

    class Meta:
        model = Contest
        fields = [
            'id', 'title', 'organizer', 'start_date', 'end_date',
            'target_audience', 'has_prize', 'prize_details', 'details_url',
            'image', 'created_at', 'is_liked', 'likes_count',
        ]
        read_only_fields = ['id', 'created_at']

    def get_image(self, obj):
        request = self.context.get("request")
        # 이미지가 있으면 절대 URL로, 없으면 None
        if obj.image and hasattr(obj.image, "url"):
            return request.build_absolute_uri(obj.image.url)
        return None
    
    # 찜하기 기능
    def get_is_liked(self, obj):
        # obj는 각 공모전 객체
        # 예시
        """
        {
            "id": 1,
            "title": "창작 공모전",
            "organizer": "한국문학협회",
            "start_date": "2025-05-01",
            "end_date": "2025-06-01",
            "target_audience":...,
            ...
        }
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated: # 로그인한 사용자라면
            return obj.liked_users.filter(pk=request.user.pk).exists()
        return False
    
    # 좋아요 수 계산
    def get_likes_count(self, obj):
        return obj.liked_users.count() 


# 목록용 간단한 공모전 정보 제공: GET /api/v1/contests/ 등
class SimpleContestSerializer(serializers.ModelSerializer):
    """
    - 마이페이지 또는 특정 화면에서 공모전의 간단한 정보를 표시할 때 사용된다.
    - 사용자가 해당 공모전을 찜했는지 여부를 is_liked 필드로 확인할 수 있다.
    """
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()  # 찜한 사용자 수 계산

    class Meta:
        model = Contest
        fields = [
            'id', 'title', 'organizer', 'start_date', 'end_date', 
            'target_audience', 'has_prize', 'is_liked', 'likes_count', 'image', 'details_url', 'prize_details', 'created_at'
        ]
        read_only_fields = [
            'id', 'title', 'organizer', 'start_date', 'end_date', 
            'target_audience', 'has_prize', 'is_liked', 'likes_count', 'image', 'details_url', 'prize_details', 'created_at'
        ]

    # 찜하기 기능
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated: # 로그인한 사용자라면
            return obj.liked_users.filter(pk=request.user.pk).exists()
        return False
    
    # 좋아요 수 계산
    def get_likes_count(self, obj):
        return obj.liked_users.count()  
