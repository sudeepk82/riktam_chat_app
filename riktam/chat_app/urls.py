from django.urls import include, path
from chat_app import views
from rest_framework import routers
from django.contrib.auth import views as auth_views


router = routers.DefaultRouter()
router.register("groups", views.GroupViewSet, basename="group")
router.register("messages", views.MessageViewSet, basename="message")
router.register("users", views.AppUserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    # path(
    #     "login/",
    #     views.DangerousLoginView.as_view(template_name="login.html"),
    #     name="login",
    # ),
    # path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]

# print(router.get_urls())
