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
from django.contrib.auth import views as auth_views
from django.contrib import admin
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # Core
    path('', site_views.index, name='index'),
    path('feedback/', site_views.feedback, name='feedback'),
    # Account pages
    path('account/profile/', site_views.profile, name='profile'),
    path('account/signup/', site_views.register, name='register'),
    path('account/deactivate/', site_views.deactivate_user, name='deactivate'),
    path('account/login/', auth_views.LoginView.as_view(), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^admin/', admin.site.urls),
    # API
    url(r'^api/', include(api_router.urls)),
]
