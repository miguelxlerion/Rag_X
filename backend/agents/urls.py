from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("agents", views.AgentViewSet, basename="agent")

urlpatterns = [
    path("agents/test-config/", views.TestConfigView.as_view(), name="agent-test-config"),
    path("agents/seed-test-agents/", views.SeedTestAgentsView.as_view(), name="agent-seed-test"),
    path("free-models/", views.FreeModelsView.as_view(), name="free-models"),
    path("platform-config/", views.PlatformConfigView.as_view(), name="platform-config"),
    path("chat-agents/", views.ChatAgentsView.as_view(), name="chat-agents"),
] + router.urls
