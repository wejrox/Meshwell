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
    path('catalog/', site_views.catalog, name='catalog'),
    path('about-us/', site_views.about_us, name='about-us'),
    # Account pages
    path('dashboard/', site_views.dashboard, name='dashboard'),
    path('dashboard/profile/', site_views.profile, name='profile'),
    path('account/signup/', site_views.register, name='register'),
    path('dashboard/connect_account/', site_views.connect_account, name='connect_account'),
    path('dashboard/connected_accounts/', site_views.connected_accounts, name='connected_accounts'),
    path('account/deactivate/', site_views.deactivate_user, name='deactivate'),
    path('account/login/', auth_views.LoginView.as_view(), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dasboard/edit_profile/', site_views.edit_profile, name='edit_profile'),
    path('dashboard/preference/', site_views.user_preference, name='user_preference'),
    # Admin
    url(r'^admin/', admin.site.urls),
    # API
    url(r'^api/', include(api_router.urls)),
    # Temporary Development
    path('css-standard/', site_views.css_standard, name='css-standard'),
]
