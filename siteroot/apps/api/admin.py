from django.contrib import admin
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Feedback
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
#from django.contrib.auth.models import User
#from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Availability)
admin.site.register(Game)
admin.site.register(Game_Role)
admin.site.register(Session)
admin.site.register(Session_Profile)
admin.site.register(Profile_Connected_Game_Account)
admin.site.register(Feedback)

class ReportAdmin(admin.ModelAdmin):
	list_display = ('user_reported', 'report_reason', 'sent_by', 'session')
admin.site.register(Report, ReportAdmin)

class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'birth_date', 'sessions_played')
	readonly_fields = (('sessions_played'),('birth_date'),('user'),('pref_server'),('teamwork_commends'),('skill_commends'),('positivity_commends'),('communication_commends'),('discord_name'))#,'total_reports')

#USER BANNING FUNCTION, CURRENTLY UNDER DEVELOPMENT
	#readonly_fields = (('user'), ('birth_date'), ('sessions_played') , ('commendations'))
	#actions = ['ban_users']
	#def total_reports(self, obj):
		#return Report.objects.filter(user_reported=obj).count()

	#def ban_users(self, request, queryset):
		#self.user.objects.update(is_active = False)
		#self.message_user(request, "Banned and Sent Email")
		#User.save()
	#ban_users.short_description = "Ban & Email"


admin.site.register(Profile, ProfileAdmin)

class MyUserAdmin(UserAdmin):
	list_display = ('username', 'first_name', 'last_name' , 'email')
	readonly_fields = ('first_name' , ('last_name') , ('email') , ('username'))

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

#USER BANNING FUNCTION, CURRENTLY UNDER DEVELOPMENT
#def banning(self, request, queryset):
#	self.user.objects.all().update(is_active=false)
	#self.message_user(request, "BANNED")
	#user.save()
