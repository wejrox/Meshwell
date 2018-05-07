from django.contrib import admin
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Feedback, Banned_User
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages



# Register your models here.
admin.site.register(Availability)
admin.site.register(Game)
admin.site.register(Game_Role)
admin.site.register(Session)
admin.site.register(Session_Profile)
admin.site.register(Profile_Connected_Game_Account)
admin.site.register(Feedback)


#USER BANNING FUNCTION, CURRENTLY UNDER DEVELOPMENT, Email stub is also here
#Banning and emailing function can be merged into one so emails are sent when users are banned
#def ban_users(self, request, queryset):
#	queryset.update(is_active = False)
#	self.message_user(request, "User is banned and Email has been sent")


def banning_users(self, request, queryset):
    for obj in queryset:
        if hasattr(obj, 'user'):
            # This object is a Profile, so lookup the user
            obj = obj.user
        obj.is_active = False
        obj.save()
    self.message_user(request, "User is banned and Email has been sent")

def unbanning_users(self, request, queryset):
    for obj in queryset:
        if hasattr(obj, 'user'):
            # This object is a Profile, so lookup the user
            obj = obj.user
        obj.is_active = True
        obj.save()
    self.message_user(request, "User is unbanned")

def ban_users(self, request, queryset):
	queryset.update(is_active = False)
	banned_user = Banned_User.objects.create(profile=request.user.profile)
	banned_user.save()
	self.message_user(request, "user banned")

def remove_ban(self, request, queryset):
	print(queryset)
	queryset.update(is_active = True)
	#banned_user = Banned_User.objects.delete(profile=request.user.profile,report_reason=profile.report.report_reason)
	#banned_user.save()
	self.message_user(request, "Users ban has been lifted")

#Admin functions will be created here,as well as registration  of their specific models
class ReportAdmin(admin.ModelAdmin):
	list_display = ('user_reported', 'report_reason', 'sent_by', 'session')


admin.site.register(Report, ReportAdmin)

class ProfileAdmin(admin.ModelAdmin):

	list_display = ('user', 'birth_date', 'sessions_played', 'total_reports', 'reason_reported_sent')
	readonly_fields = (('sessions_played'),('birth_date'),('user'),('pref_server'),('teamwork_commends'),('skill_commends'),('sportsmanship_commends'),('communication_commends'),('discord_name'))#,'total_reports')
	actions = ['ban1', 'unban1']
	ban1 = banning_users
	unban1 = unbanning_users



	def total_reports(self, obj):
		return Report.objects.filter(user_reported=obj).count()
	def reason_reported_sent(self, obj):
		return Report.report_reason
		#return instance.report.sent_by

admin.site.register(Profile, ProfileAdmin)

class MyUserAdmin(UserAdmin):
	list_display = ('userprofile','username', 'first_name', 'last_name' , 'email')
	readonly_fields = ('first_name' , ('last_name') , ('email') , ('username'))
	actions = [ban_users, remove_ban]
	#ban = ban_users
	#unban = remove_ban

	def userprofile(self, instance):
		return instance.profile.user

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
