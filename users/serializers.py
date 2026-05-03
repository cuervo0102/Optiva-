from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"]      = user.role
        token["full_name"] = user.full_name
        token["matricule"] = user.matricule
        token["email"]     = user.email
        return token

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs["username"])
            if user.is_locked:
                raise serializers.ValidationError(
                    "Account blocked Contact the administrator"
                )
        except User.DoesNotExist:
            pass

        try:
            data = super().validate(attrs)
            self.user.failed_login_attempts = 0
            self.user.save(update_fields=["failed_login_attempts"])
            data["user"] = {
                "id":        self.user.id,
                "username":  self.user.username,
                "email":     self.user.email,
                "full_name": self.user.full_name,
                "role":      self.user.role,
                "matricule": self.user.matricule,
                "photo_url": self.user.photo_url,
            }
            return data
        except Exception:
            try:
                user = User.objects.get(username=attrs["username"])
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.is_locked = True
                user.save(update_fields=[
                    "failed_login_attempts", "is_locked"
                ])
            except User.DoesNotExist:
                pass
            raise


class UserSerializer(serializers.ModelSerializer):

    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            "id", "username", "email",
            "first_name", "last_name", "full_name",
            "role", "phone", "photo", "photo_url",
            "matricule", "department",
            "hire_date", "is_active",
            "is_locked", "created_at",
        ]
        read_only_fields = ["id", "full_name", "created_at"]
        extra_kwargs = {
            "cnss":  {"write_only": True},
            "photo": {"write_only": True},
        }

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


class CreateUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    photo = serializers.ImageField(
        required=False,
        validators=[FileExtensionValidator(
            allowed_extensions=["jpg", "jpeg", "png", "webp"]
        )]
    )

    class Meta:
        model  = User
        fields = [
            "username", "email", "password",
            "first_name", "last_name", "role",
            "phone", "photo", "matricule", "cnss",
            "department", "hire_date",
        ]

    def validate_matricule(self, value):
        if User.objects.filter(matricule=value).exists():
            raise serializers.ValidationError(
                "This registration number is already in use"
            )
        return value

    def validate_cnss(self, value):
        if User.objects.filter(cnss=value).exists():
            raise serializers.ValidationError(
                "This CNSS number is already in use."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):

    photo = serializers.ImageField(
        required=False,
        validators=[FileExtensionValidator(
            allowed_extensions=["jpg", "jpeg", "png", "webp"]
        )]
    )

    class Meta:
        model  = User
        fields = ["first_name", "last_name", "phone", "photo", "email"]


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Old password is incorrect."
            )
        return value