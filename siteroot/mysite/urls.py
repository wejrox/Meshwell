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
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
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
    path('terms-of-service/', site_views.terms_of_service, name='terms-of-service'),
    path('privacy-policy/', site_views.privacy_policy, name='privacy-policy'),
    path('contact-us/', site_views.contact_us, name='contact-us'),
    # Account pages
    path('dashboard/', site_views.dashboard, name='dashboard'),
    path('dashboard/profile/', site_views.profile, name='profile'),
    path('dashboard/discord_disconnect_account/', site_views.discord_disconnect_account, name='discord_disconnect_account'),
    path('register/', site_views.register, name='register'),
    path('dashboard/connected_accounts/<int:pk>/remove/', site_views.remove_connected_account, name='remove_connected_account'),
    path('dashboard/connected_accounts/add/', site_views.connect_account, name='connect_account'),
    path('account/deactivate/', site_views.deactivate_user, name='deactivate'),
    path('login/', site_views.login_custom, name='login'),
    path('login_modal/', site_views.login_modal, name='login_modal'),
    path('logout/', site_views.a_logout, name='logout'),
    path('dashboard/edit_profile/', site_views.edit_profile, name='edit_profile'),
    path('dashboard/enter_queue/', site_views.enter_queue, name='enter_queue'),
    path('dashboard/exit_queue/', site_views.exit_queue, name='exit_queue'),
    path('dashboard/matchmaking_preferences/', site_views.matchmaking_preferences, name='matchmaking_preferences'),
    path('dashboard/availability/<int:pk>/remove/', site_views.remove_availability, name='remove_availability'),
    path('dashboard/availability/add/', site_views.add_availability, name='add_availability'),
    path('dashboard/availability/edit/', site_views.edit_availability, name='edit_availability'),
    path('dashboard/availability/<int:pk>/edit/', site_views.edit_availability, name='edit_availability'),
    path('dashboard/session/rate/', site_views.rate_session, name='rate_session'),
    path('dashboard/session/<int:pk>/rate/', site_views.rate_session, name='rate_session'),
    path('dashboard/manual_matchmaking/', site_views.manual_matchmaking, name='manual_matchmaking'),
    # Admin
    url(r'^admin/', admin.site.urls),
    # API
    url(r'^api/', include(api_router.urls)),
    # Password reset
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    # Discord Authentication
    url(r'^discord_callback/', site_views.discord_callback, name='discord_callback'),
]

# Development serving of media files (game images)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
