from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from . import views

from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static

# Loading plotly Dash apps script
import Dashboard.dash_app_code

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    url('^django_plotly_dash/', include('django_plotly_dash.urls')),
]
