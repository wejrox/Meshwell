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
from django.urls import path
from mysite import views as site_views
from apps.api.urls import router as api_router
from rest_framework.authtoken import views as token_views
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # Add a reference to core pages
    path('', site_views.index, name='index'),
    path('account/profile/', site_views.profile, name='profile'),
    path('feedback/', site_views.feedback, name='feedback'),
    path('account/', include('django.contrib.auth.urls')),
    url(r'^api/', include(api_router.urls)),
    # Add a reference to the API authentication
    url(r'^api-token-auth/', token_views.obtain_auth_token)
]
