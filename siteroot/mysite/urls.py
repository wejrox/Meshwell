"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import routers
from mysite import views as site_views
from django.views.generic import TemplateView
from apps.api import views as api_views

# Set up our default URL router
router = routers.DefaultRouter()

# Register the static pages

# Register dynamic pages
router.register(r'profile', api_views.ProfileViewSet, base_name='profile')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # Add a reference to core pages
    url(r'^$', site_views.index, name='index'),
    url(r'^api/', include(router.urls)),
    # Add a reference to the API authentication
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
