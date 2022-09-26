
from django.urls import path, include
from .views import UserTokenCreationViews, EventViews, SessionTokenCreationViews, SessionTokenValidationViews, UserTokenValidationViews

urlpatterns = [
    path('generate-user-token/',
         UserTokenCreationViews.as_view()),
    path('generate-session-token/',
         SessionTokenCreationViews.as_view()),
    path('validate-user-token/',
         UserTokenValidationViews.as_view()),
    path('validate-session-token/',
         SessionTokenValidationViews.as_view()),
    path('events/', EventViews.as_view()),
]
