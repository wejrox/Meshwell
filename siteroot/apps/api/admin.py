from django.contrib import admin
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Feedback, Banned_User
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings



# Register your models here.
admin.site.register(Availability)
admin.site.register(Game)
admin.site.register(Game_Role)
admin.site.register(Session)
admin.site.register(Session_Profile)
admin.site.register(Profile_Connected_Game_Account)
admin.site.register(Feedback)
#admin.site.register(Banned_User)

#User Banning and emailing Function(CURRENTLY TESTING THIS)
#def banning_users(user, request, queryset):

#	for obj in queryset:
#		if hasattr(obj, 'user'):
			# This object is a Profile, so lookup the user
#			obj = obj.user
#		obj.is_active = False
		#rep = get_report.report_reason
		#banned_user = Banned_User.objects.create(profile=request.user.profile)
		#banned_user.report_reason.add(request.user.profile.user_reported_report.all())
		#banned_user = Banned_User.objects.create(profile=request.user.profile)
		#banned_user.report_reason.set(request.user.profile.user_reported_report.all())
#		banned_user = Banned_User.objects.create(profile=request.user.profile)
#		banned_user.report_reason.add(request.user.profile.user_reported_report.all())
		#banned_user.save()
		#Sends ban email to user,does not send through the variables yet
#		subject = 'Ban'
#		message =   'You have been banned for being trash'
#		email_from = settings.EMAIL_HOST_USER
#		recipient_list = [obj.email]
#		send_mail( subject, message,email_from, recipient_list )
		#obj.save()


#	self.message_user(request, "User is banned and Email has been sent")

def banning_users(self, request, queryset):

	for obj in queryset:
		if hasattr(obj, 'user'):
			# This object is a Profile, so lookup the user
			profile = obj
			user = obj.user
		user.is_active = False

		# Get the report(s) for this user
		user_reports = Report.objects.filter(user_reported=profile)

		# Go through each report, in case there are multiples,
		# add a record in the ban table

		banned_reasons = []

		for report in user_reports:
			ban_record = Banned_User.objects.create(profile=profile, report_reason=report) #date_banned=datetime.datetime.today())
			banned_reasons.append(report.get_report_reason_display())
			#report_reason.set(report.get_report_reason_display())

			#banned_user.save()
		# Send the email
		subject = 'Ban'
		message = 'You have been banned for the following reasons: []'
		message.format(','.join(banned_reasons))
		email_from = settings.EMAIL_HOST_USER
		recipient_list = [user.email]
		send_mail( subject, message,email_from, recipient_list)

	self.message_user(request, "User is banned and Email has been sent")

def unbanning_users(self, request, queryset):
	for obj in queryset:
		if hasattr(obj, 'user'):
			# This object is a Profile, so lookup the user
			obj = obj.user
		obj.is_active = True
		obj.save()
	self.message_user(request, "User is unbanned")

class ReportAdmin(admin.ModelAdmin):
	prof = Profile.user
	list_display = ('user_reported', 'report_reason', 'sent_by', 'session')


admin.site.register(Report, ReportAdmin)

class ProfileAdmin(admin.ModelAdmin):

	list_display = ('user', 'birth_date', 'sessions_played', 'total_reports', 'reason_reported_sent')
	readonly_fields = (('sessions_played'),('birth_date'),('user'),('pref_server'),('teamwork_commends'),('skill_commends'),('sportsmanship_commends'),('communication_commends'),('discord_id'))#,'total_reports')
	actions = ['ban1', 'unban1','email_ban']
	ban1 = banning_users
	unban1 = unbanning_users

	def total_reports(self, obj):
		return Report.objects.filter(user_reported=obj).count()
	def reason_reported_sent(self, obj):
		return Report.objects.filter(report_reason=obj).count()
		#return instance.report.sent_by

admin.site.register(Profile, ProfileAdmin)

class MyUserAdmin(UserAdmin):
	list_display = ('userprofile','username', 'first_name', 'last_name' , 'email')
	readonly_fields = ('first_name' , ('last_name') , ('email') , ('username'))
	actions = [banning_users, unbanning_users]

	#ban = ban_users
	#unban = remove_ban

	def userprofile(self, instance):
		return instance.profile.user

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

class Banned_UserAdmin(admin.ModelAdmin):
	list_display = ('profile','profile')

admin.site.register(Banned_User, Banned_UserAdmin)
