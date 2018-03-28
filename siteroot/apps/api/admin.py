from django.contrib import admin
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Game_Api_Connection, Feedback


# Register your models here.
admin.site.register(Profile)
admin.site.register(Availability)
admin.site.register(Game)
admin.site.register(Game_Role)
admin.site.register(Session)
admin.site.register(Session_Profile)
admin.site.register(Report)
admin.site.register(Profile_Connected_Game_Account)
admin.site.register(Game_Api_Connection)
admin.site.register(Feedback)
