"""API Router Configuration
This file contains the routing information for the API, which is
accessed via Views in mysite/views.py, and Urls in mysite/urls.py
"""
from rest_framework import routers
from apps.api import views

# Set up our default URL router
router = routers.DefaultRouter()

# Register dynamic pages
router.register(r'profile', views.ProfileViewSet, base_name='profile')
router.register(r'availability', views.AvailabilityViewSet, base_name='availability')
router.register(r'game', views.GameViewSet, base_name='game')
router.register(r'game_role', views.Game_RoleViewSet, base_name='game_role')
router.register(r'session', views.SessionViewSet, base_name='session')
router.register(r'session_profile', views.Session_ProfileViewSet, base_name='session_profile')
router.register(r'report', views.ReportViewSet, base_name='report')
router.register(r'profile_connected_game_account', views.Profile_Connected_Game_AccountViewSet, base_name='profile_connected_game_account')
router.register(r'game_api_connection', views.Game_Api_ConnectionViewSet, base_name='game_api_connection')
router.register(r'feedback', views.FeedbackViewSet, base_name='feedback')
