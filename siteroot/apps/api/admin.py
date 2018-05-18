from django.contrib import admin
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Feedback, Banned_User
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage





# Register your models here.
admin.site.register(Availability)
admin.site.register(Game)
admin.site.register(Game_Role)
admin.site.register(Session)
admin.site.register(Session_Profile)
admin.site.register(Profile_Connected_Game_Account)
admin.site.register(Feedback)
admin.site.register(Banned_User)


#User Banning and emailing Function(CURRENTLY TESTING THIS)
def banning_users1(self, request, queryset):

	for obj in queryset:
		if hasattr(obj, 'user'):
			# This object is a Profile, so lookup the user
			#profile = obj
			profile = obj
			obj = obj.user
		obj.is_active = False
		obj.save()
		#import pdb; pdb.set_trace() ******DEBUGGING INPUT******
		banned_user = profile.banned_profile.create(profile=profile)
		reports = banned_user.profile.user_reported_report.all()
		banned_user.save()
		for report in reports:
			banned_user.report_reason.add(report)
			banned_reasons.append(report.get_report_reason_display())

		def get_report_reason(self, obj):
		#	return obj.banned_user.report_reason
		#get_report_reason.short_description = 'Reason'
			return "\n".join([r.report_reason for r in obj.report_reason.all()])


		# Send the email
		subject = 'Ban'
		message = '''Hello {},We are sorry to inform you that you have been banned from {},
		for the following reasons: .
		This will take place immediately.Thank you for understanding.

		Regards,
		The Meshwell Team
		'''.format(user.username, "meshwell" )
		email_from = settings.EMAIL_HOST_USER
		recipient_list = [user.email]
		send_mail( subject, message,email_from, recipient_list)

	self.message_user(request, "User is banned and Email has been sent")

#Banning function for PROFILE
def banning_users(self, request, queryset):

	for obj in queryset:
		if hasattr(obj, 'user'):
			# This object is a Profile, so lookup the user
			profile = obj
			user = obj.user
		user.is_active = False
		user.save()

		# Get the report(s) for this user
		user_reports = Report.objects.filter(user_reported=profile)

		# Go through each report, in case there are multiples,
		# add a record in the ban table

		banned_reasons = []

		#import pdb; pdb.set_trace() ******DEBUGGING INPUT******
		banned_user = profile.banned_profile.create(profile=profile)
		reports = banned_user.profile.user_reported_report.all()
		banned_user.save()
		for report in reports:
			banned_user.report_reason.add(report)
			banned_reasons.append(report.get_report_reason_display())
		# Send the email
		subject = 'Ban'
		message = '''Hello {},We are sorry to inform you that you have been banned from {},
		for the following reasons: {}.
		This will take place immediately.Thank you for understanding.

		Regards,
		The Meshwell Team
		'''.format(user.username, "meshwell",banned_reasons )
		email_from = settings.EMAIL_HOST_USER
		recipient_list = [user.email]
		send_mail( subject, message,email_from, recipient_list)

	self.message_user(request, "User is banned and Email has been sent")

def unbanning_users(self, request, queryset):
	for obj in queryset:
		if hasattr(obj, 'user'):
			# This object is a Profile, so lookup the user
			profile=obj
			obj = obj.user
		obj.is_active = True
		obj.save()
	Banned_User.objects.filter(profile=profile).delete()
	self.message_user(request, "User is unbanned")

class ReportAdmin(admin.ModelAdmin):
	prof = Profile.user
	list_display = ('user_reported', 'report_reason', 'sent_by', 'session')


admin.site.register(Report, ReportAdmin)

class ProfileAdmin(admin.ModelAdmin):
	class Meta:
		ordering = ['-total_reports',]
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
	actions = [banning_users1,unbanning_users]

	def userprofile(self, instance):
		return instance.profile.user

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

class Banned_UserAdmin(admin.ModelAdmin):
	fields = ['profile', 'report_reason']
	list_display = ('profile','get_report_reason')

	def get_report_reason(self, obj):
		return "\n".join([r.report_reason for r in obj.report_reason.all()])
admin.site.unregister(Banned_User)
admin.site.register(Banned_User, Banned_UserAdmin)
