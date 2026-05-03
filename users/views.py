from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    CreateUserSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdmin, IsAdminOrManager, IsAdminOrSelf

User = get_user_model()


class LoginView(TokenObtainPairView):
    serializer_class   = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
            return Response(
                {"message": "Logout successfully"},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Token invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return Response(
            UserSerializer(request.user,
                           context={"request": request}).data
        )

    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "user": UserSerializer(
                    request.user,
                    context={"request": request}
                ).data
            })
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            request.user.set_password(
                serializer.validated_data["new_password"]
            )
            request.user.save()
            return Response(
                {"message": "Password changed successfully"}
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserListView(generics.ListAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsAdminOrManager]
    filterset_fields   = ["role", "is_active", "department"]
    search_fields      = ["username", "email", "full_name", "matricule"]
    ordering_fields    = ["created_at", "full_name", "role"]

    def get_queryset(self):
        return User.objects.all().order_by("-created_at")


class CreateUserView(generics.CreateAPIView):
    serializer_class   = CreateUserSerializer
    permission_classes = [IsAdmin]
    parser_classes     = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User successfully created",
            "user": UserSerializer(
                user, context={"request": request}
            ).data
        }, status=status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsAdmin]
    queryset           = User.objects.all()
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {"error": "Impossible to delete your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = False
        user.save()
        return Response(
            {"message": "User deactivated"},
            status=status.HTTP_200_OK
        )


class UnlockUserView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_locked = False
            user.failed_login_attempts = 0
            user.save()
            return Response({"message": "Account unlocked"})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class UsersByRoleView(generics.ListAPIView):
    """GET /api/auth/users/role/<role>/"""
    serializer_class   = UserSerializer
    permission_classes = [IsAdminOrManager]

    def get_queryset(self):
        return User.objects.filter(
            role=self.kwargs["role"],
            is_active=True
        )