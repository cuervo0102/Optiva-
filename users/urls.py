from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, LogoutView,
    MeView, ChangePasswordView,
    UserListView, CreateUserView,
    UserDetailView, UnlockUserView,
    UsersByRoleView,
)

from .views import test_predict


urlpatterns = [
    path("login/",           LoginView.as_view(),         name="login"),
    path("logout/",          LogoutView.as_view(),         name="logout"),
    path("refresh/",         TokenRefreshView.as_view(),   name="token-refresh"),
    path("me/",              MeView.as_view(),             name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("users/",                    UserListView.as_view(),   name="user-list"),
    path("users/create/",             CreateUserView.as_view(), name="user-create"),
    path("users/<int:pk>/",           UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/unlock/",    UnlockUserView.as_view(), name="user-unlock"),
    path("users/role/<str:role>/",    UsersByRoleView.as_view(),name="users-by-role"),

    path("test-predict/", test_predict, name="test-predict"),
]