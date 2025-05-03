from rest_framework import serializers
from .models import Genre
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

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
    
    # username의 중복 확인 메서드
    def validate_username(self, value):
        if User.objects.filter(username=value).exists(): # 이미 해당 value와 동일한 username이 있다면
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        return value

    # email의 중복 확인 메서드
    def validate_email(self, value):
        if User.objects.filter(email=value).exists(): # 이미 해당 value와 동일한 email이 있다면
            raise serializers.ValidationError("이미 등록된 이메일 주소입니다.")
        return value

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
        
        # 일반 회원가입은 정보 입력이 끝났다면 바로 완료
        user.is_profile_completed = True
        user.save()

        return user
        # 예. print(user.genres.all())   # <QuerySet [<Genre: 판타지>, <Genre: SF/공상 과학>]>
        # user 인스턴스의 genres 예시
        '''
        "genres": [
            { "id": 1, "name": "로맨스" },
            { "id": 2, "name": "SF/공상 과학" }
            ]
        '''

# 소셜 로그인 추가 정보 입력 : POST /api/v1/users/social/extra-info/)
class SocialExtraInfoSerializer(serializers.ModelSerializer):
    # 장르
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        required=True, 
        help_text='선호하는 장르 (최대 3개)'
    )
    # 이미지
    profile_image = serializers.ImageField(
        required=False, 
        allow_null=True
    )
    class Meta:
        model = User
        fields = ['username', 'name', 'genres', 'author_status', 'profile_image', 'email'] # 추가 작성할 필드 목록
        extra_kwargs = {
            # 필수 필드
            'username': {'required': True},
            'name': {'required': True},
            'author_status': {'required': True},
            'email': {'required': True},
        }
    
    # username의 중복 확인 메서드
    # 중복되지 않도록 폼에서 수정할 수 있어야 함 (프론트엔드)
    def validate_username(self, value):
        if self.instance and self.instance.username and self.instance.username == value:
            return value # 자기 자신의 기존 username은 허용
        if User.objects.filter(username=value).exists(): # 이미 해당 value와 동일한 username이 있다면
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        return value

    # email의 중복 확인 메서드
    def validate_email(self, value):
        if self.instance and self.instance.email and self.instance.email == value:
            return value  # 자기 자신의 기존 email은 허용
        if User.objects.filter(email=value).exists(): # 이미 해당 value와 동일한 email이 있다면
            raise serializers.ValidationError("이미 등록된 이메일 주소입니다.")
        return value
    
    # 주력 장르 3개까지 선택 제한
    def validate_genres(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("주력 장르는 최대 3개까지 선택할 수 있습니다.")
        return value
    # 현재 로그인된 사용자의 정보 업데이트
    def update(self, instance, validated_data):
        # instance 예시

        # genres는 mtm 필드로 일반 필드와 같이 setattr()로 처리할 수 없고 따로 처리해야 함
        genres_data = validated_data.pop('genres')

        # validated_data에 남아있는 필드들을 순회하면서, 해당 값을 instance의 필드에 할당
        for attr, value in validated_data.items():
            # setattr(object, name, value): object의 name 속성에 value를 할당함
            # 여기서는 instance (User 모델 인스턴스)의 속성(attr)에 validated_data의 값(value)을 할당함
            # validated_data 예시. {'name': '새이름', 'author_status': '신인'},
            setattr(instance, attr, value)
            # 활용 예시. instance.name = '새이름'

        # 장르 정보 업데이트
        instance.genres.set(genres_data)
        
        # 프로필 작성이 완료되었음을 표시
        instance.is_profile_completed = True
        instance.save() # 변경된 내용을 데이터베이스에 저장합니다.
        return instance # 업데이트된 User 모델 인스턴스를 반환합니다.

# 로그인 : POST /api/v1/users/login/
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="사용자 아이디")
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, help_text="비밀번호")

    def validate(self, data):
        # data 예시: {'username': 'test', 'password': '1234'}
        # authenticate(): Django의 내장 함수로, 주어진 사용자 이름과 비밀번호로
        # 데이터베이스에서 해당 User 객체를 찾아서
        # 인증에 성공하면 User 객체를 반환하고, 실패하면 None을 반환함
        user = authenticate(**data)
        # 예. **data로 authenticate(username='test', password='1234')와 동일함

        if user and user.is_active: # 인증에 성공했고, 해당 사용자가 활성화되어 있다면
            return user
        # 인증에 실패하거나 사용자가 비활성화된 상태라면
        raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")
    
# ID 찾기 : POST /api/v1/users/find-id/
class FindIdSerializer(serializers.Serializer):
    # 이메일 주소 입력받기
    email = serializers.EmailField(required=True, help_text="가입 시 사용한 이메일 주소를 입력하세요")

# 임시 비밀번호 이메일 발송 : POST /api/v1/users/reset-password/
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, help_text="가입 시 사용한 이메일 주소를 입력하세요")

# 비밀번호 변경 : POST /api/v1/users/password/change/
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, help_text="현재 비밀번호")
    new_password1 = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, help_text="새 비밀번호(8자 이상)", validators=[validate_password])
    # validate_password: django 기본 비밀번호 유효성 검사 함수
    # settings.py에 설정된 AUTH_PASSWORD_VALIDATORS에 따라 비밀번호 검사
    new_password2 = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, help_text="새 비밀번호 확인")

    # 특정 필드 수준 유효성 검사 (validate_<field_name> 메서드)
    # old_password의 값만 인자(value)로 전달되어 유효성 검사 진행
    # 기존 비밀번호가 실제 사용자의 비밀번호와 일치하는지 확인
    def validate_old_password(self, value):
        # self: serializer 인스턴스 자신
        # value: 사용자가 폼이나 api로 입력한 값
        # value 예시. "currentPassword123"
        user = self.context['request'].user # 현재 로그인한 사용자
        # context: drf에서는 뷰 함수에서 serializer를 호출(생성)할 때
        # request 객체를 자동으로 context에 포함시키는 경우가 많음
        # 예. serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if not user.check_password(value):
            # check_password(): 주어진 비밀번호(value)가 사용자의 비밀번호와 일치하는지 확인
            # 이전 비밀번호 value를 해싱해 db에 해싱된 비밀번호와 비교 -> True/False 반환
            raise serializers.ValidationError("기존 비밀번호가 올바르지 않습니다.")
        return value # 검증된 값(기존 비밀번호) 반환
    
    # 객체 수준 유효성 검사 (validate 메서드)
    # 모든 필드에 대한 유효성 검사가 완료된 후 전체 데이터를 대상으로 유효성 검사 진행
    # 새로운 비밀번호 확인(new1과 new2가 일치하는지, 8자 이상인지)
    def validate(self, data):
        # data: 유효성 검사를 위해 전달된 모든 입력 필드 값들
        # data 예시. OrderedDict([('old_password', 'currentPassword123'), ('new_password1', 'newSecurePassword!'), ('new_password2', 'newSecurePassword!')])
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError("새 비밀번호와 확인 비밀번호가 일치하지 않습니다.")
        return data

    # 유효성 검사를 통과한 새 비밀번호 저장
    # views에서 save() 호출 시 실행
    def save(self, **kwargs):
        # **kwargs: save() 메서드에서 인자로 전달된 값들
        # 따로 views에서 따로 넘겨주지 않았다면 빈 딕셔너리
        # 예. user = serializer.save(some_extra_info='value')로 넘겨받았다면
        # kwargs= {'some_extra_info': 'value'} 
        user = self.context['request'].user # 현재 로그인된 사용자 객체
        user.set_password(self.validated_data['new_password1']) # 새 비밀번호를 암호화하여 저장
        # user.set_password: 주어진 비밀번호를 해싱하여 db에 저장
        # validated_data: self에 저장된 유효성 검사를 통과한 데이터
        user.save()
        return user # 변경된 사용자 객체 반환
    
# 프로필 수정 : PUT /api/v1/users/profile/
class ProfileSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        required=True,
        help_text='선호하는 장르 ID 목록 (예: [1, 3, 5])'
    )
    class Meta:
        model = get_user_model()
        fields = [
                    'username','email', 'name', 'phone_number', 
                    'genres', 'author_status', 'profile_image'
                ]        
        # read_only_fields = 
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'phone_number': {'required': False, 'allow_blank': True},
            'author_status': {'required': True, 'allow_blank': False},
            'profile_image': {'required': False, 'allow_null': True},
        }
    
    # username 중복 확인
    def validate_username(self, value):
        if self.instance and self.instance.username == value:
            return value  # 자기 자신의 기존 username은 허용
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        return value

    # email 중복 확인
    def validate_email(self, value):
        # exclude로 자기 자신의 기존 email은 허용
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("이미 등록된 이메일 주소입니다.")
        return value
    
    # 장르 선택 개수 유효성 검사 (최대 3개까지)
    def validate_genres(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("선호 장르는 최대 3개까지 선택할 수 있습니다.")
        if not value:  # genres 필드가 비어있는지 확인
            raise serializers.ValidationError("선호 장르를 하나 이상 선택해야 합니다.")
        return value
    
    def update(self, instance, validated_data):

        genres_data = validated_data.pop('genres', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if genres_data is not None:
            instance.genres.set(genres_data) 

        instance.save()

        return instance