from rest_framework import serializers
from .models import Genre
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# 장르 (읽기 전용) : GET /api/v1/users/mypage/ , /api/v1/users/profile/
class GenreSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Genre
        fields = ['id', 'name'] 
        # id 필드가 필요한 이유: mtm으로 관계를 맺고, 인스턴스를 식별하며 프론트엔드에서 활용하기 위함


# 회원 가입 : POST /api/v1/users/signup/
"""
[요청 예시]
{
  "username": "juhee",
  "email": "juhee@example.com",
  "name": "주희",
  "phone_number": "01012345678",
  "password": "safe_password123!",
  "password2": "safe_password123!",
  "genres": [1, 3, 5],
  "author_status": "aspiring"
}
"""
class SignupSerializer(serializers.ModelSerializer):
    # 장르 (필수)
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), # 사용자는 이 중에서 선택할 수 있다 -> 유효성 검사 시, 필드로 받은 값(예, 1과 3)이 queryset에 존재하는지 확인함(queryset.get(pk=1))
        many=True, # 여러 개의 장르 선택 가능
        required=True,
        help_text='선호하는 장르 ID 목록 (예: [1, 3])' # PrimaryKeyRelatedField를 사용해 id 값으로 장르 정보가 넘겨짐
    )
    # 비밀번호 확인
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'} # 비밀번호가 ●●●● 처럼 가려져 보이기 위한 장식 옵션
    ) # write_only로 읽기(데이터 응답)에는 포함되지 않음
      # 보안 상의 이유로 프론트엔드에는 노출하지 않기 위함
    # 프로필 이미지
    profile_image = serializers.ImageField(
        required=False, 
        allow_null=True
    )

    class Meta:
        model = get_user_model() 
        fields = [
            'username','password', 'password2','email', 'name', 'phone_number', 
            'genres', 'author_status', 'profile_image'
        ]
    # extra_kwargs: 추가적인 옵션 부여
    extra_kwargs = {
        'password': {
            'write_only': True,
            'style': {'input_type': 'password'},
            'validators': [validate_password] # Django의 기본 비밀번호 유효성 검사 규칙 적용
            # settings.py에 설정된 비밀번호 정책을 따름(AUTH_PASSWORD_VALIDATORS 부분)
            # 예. 너무 짧은 비밀번호, 너무 흔한 비밀번호, 숫자만 이루어진 비밀번호, 사용자 이름과 유사한 비밀번호	는 거절됨
        },
        'phone_number': {'required': False, 'allow_blank': True},
        'email': {'required': True},
        'name': {'required': True},
        'author_status': {'required': True},
        # username, password는 이미 모델에 의해 필수 처리되므로 required=True를 별도로 쓸 필요는 없음
    }
    # Model에 blank=False가 있는데도 Serializer에서 required=True를 또 쓰는 이유?
    # 1. 명시적으로 보여주기 위해 (가독성 및 문서화 목적)
    # 2. 입력 방식의 차이 때문
        # 모델은 DB 저장 기준이고, Serializer는 사용자 입력 값을 다루는 기준
        # 예: blank=False는 Django의 ModelForm에서만 HTML <form> 기준으로 동작하고,
        # REST API 요청에서는 동작하지 않는다.
    
    # 주력 장르의 선택 개수가 최대 3개 이내인지 확인하는 메서드
    # value 예시.
    """
    value = [<Genre: 로맨스>, <Genre: SF>, <Genre: 시>]
    PrimaryKeyRelatedField를 사용했기에 DRF는 [1, 3, 5]라는 ID를 받아서 자동으로 해당하는 Genre 객체 리스트로 바꿔줌
    """
    def validate_genres(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("주력 장르는 최대 3개까지 선택할 수  있습니다.")
        return value
    # validate_필드명 형태의 메서드: 특정 필드에 대한 유효성 검사를 수행함
    # DRF에서 별도로 호출하는 코드가 없어도, serializer의 is_valid() 메서드를 호출할 때 자동으로 메서드를 실행함
    
    # 비밀번호와 비밀번호 확인 필드가 일치하는지 검사하는 메서드
    # data 예시.
    """
    OrderedDict([
        ('username', 'juhee123'),
        ('password', 'Abcd1234!'),
        ('password2', 'Abcd1234!'),
        ('email', 'juhee@example.com'),
        ('name', '박주희'),
        ('phone_number', '01098765432'),
        ('genres', [<Genre: 로맨스>, <Genre: SF>, <Genre: 시>]),
        ('author_status', 'hobbyist')
    ])
    """
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "비밀번호가 일치하지 않습니다."})
        return data # 두 비밀번호가 다르다면 return
    # validate 메서드는 필드별 validate_필드명 메서드 이후에 호출됨
    
    # User 모델 인스턴스를 새로 생성하는 메서드
    # create(): 유효성 검사를 이후에 실행되는 메서드
    # .save() 호출하면 자동으로 create() 또는 update() 호출
    # 새로운 인스턴스를 만드는 상황이면 create()
    # 기존 인스턴스를 만드는 상황이면 update()
    def create(self, validated_data):
        validated_data.pop('password2') # 저장하지 않을 필드 제거
        genres_data = validated_data.pop('genres') # mtm 필드 처리
        # 예. validated_data = {'username': 'test', 'email': 'test@example.com', 'password': '1234'}
        user = User.objects.create_user(**validated_data) # 새로운 인스턴스 생성 # 비밀번호는 해싱 후 저장됨
        user.genres.set(genres_data) # .set(genres_data) 메서드: mtm 필드에 주어진 리스트의 ID에 해당하는 Genre 객체들을 연결함
        return user
        # 예. print(user.genres.all())   # <QuerySet [<Genre: 판타지>, <Genre: SF/공상 과학>]>
        # user 인스턴스의 genres 예시
        '''
        "genres": [
            { "id": 1, "name": "로맨스" },
            { "id": 2, "name": "SF/공상 과학" }
            ]
        '''
