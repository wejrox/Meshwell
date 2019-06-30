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


def ban_users(self, request, queryset):
	'''
	Bans a given set of users, sets the reports on the entries.
	'''
	for obj in queryset:
		if hasattr(obj, 'user'):
			# This object is a Profile, so lookup the user.
			profile = obj
			user = obj.user

		# Revoke their login permissions.
		user.is_active = False
		user.save()

		# Get the report(s) for this user.
		user_reports = Report.objects.filter(user_reported=profile)

		# Create the banned user instance for the profile, append all report ids.
		banned_reasons = []
		banned_user = profile.banned_profile.create(profile=profile)
		reports = banned_user.profile.user_reported_report.all()
		banned_user.save()

		for report in reports:
			banned_user.report_reason.add(report)
			banned_reasons.append(report.get_report_reason_display())

		# Inform the user that they have been banned via the email they signed up with.
		subject = 'Ban'
		message = '''Hello {}, We are sorry to inform you that you have been banned from {} 
		for the following reasons: {}. 
		This will take place effective immediately. If you believe that you have been banned in error, 
		please contact our support team and we will decide on a course of action.

		Regards,
		The Meshwell Team.
		'''.format(user.username, "Meshwell", banned_reasons)
		email_from = settings.EMAIL_HOST_USER
		recipient_list = [user.email]
		send_mail( subject, message,email_from, recipient_list)

	self.message_user(request, "User is banned and Email has been sent")


def unban_users(self, request, queryset):
	'''
	Unbans a given set of users, deleting their entry from the banned_users table.
	'''
	for obj in queryset:
		if hasattr(obj, 'user'):
			# This object is a Profile, so lookup the user.
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
	'''
	Profile Admin panel.
	'''
	class Meta:
		ordering = ['-total_reports',]
	list_display = ('user', 'birth_date', 'sessions_played', 'total_reports', 'reason_reported_sent')
	readonly_fields = (('sessions_played'), ('birth_date'), ('user'), ('pref_server'), ('teamwork_commends'), 
						('skill_commends'), ('sportsmanship_commends'), ('communication_commends'), ('discord_id'))
	actions = ['ban', 'unban']
	ban = ban_users
	unban = unban_users

	def total_reports(self, obj):
		'''
		Gets the amount of times a user has been reported.
		'''
		return Report.objects.filter(user_reported=obj).count()

	def reason_reported_sent(self, obj):
		'''
		Gets the amount of times this user has reported someone else.
		'''
		return Report.objects.filter(report_reason=obj).count()

admin.site.register(Profile, ProfileAdmin)


class MyUserAdmin(UserAdmin):
	'''
	User admin panel.
	'''
	list_display = ('userprofile','username', 'first_name', 'last_name' , 'email')
	readonly_fields = ('first_name' , ('last_name') , ('email') , ('username'))
	actions = [unban_users]

	def userprofile(self, instance):
		'''
		Gets the user that is attached to this profile.
		'''
		return instance.profile.user

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


class Banned_UserAdmin(admin.ModelAdmin):
	'''
	Admin panel for viewing banned users.
	'''
	fields = ['profile', 'report_reason']
	list_display = ('profile','get_report_reason')

	def get_report_reason(self, obj):
		'''
		Gets a list of report reasons behind why a user was banned.
		'''
		return "\n".join([r.report_reason for r in obj.report_reason.all()])

admin.site.unregister(Banned_User)
admin.site.register(Banned_User, Banned_UserAdmin)
