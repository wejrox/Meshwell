from django.contrib import admin
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Game_Api_Connection, Feedback

# Register your models here.
admin.site.register(Availability)
admin.site.register(Game)
admin.site.register(Game_Role)
admin.site.register(Session)
admin.site.register(Session_Profile)
admin.site.register(Profile_Connected_Game_Account)
admin.site.register(Game_Api_Connection)
admin.site.register(Feedback)

class ReportAdmin(admin.ModelAdmin):
	pass
	list_display = ('report_reason','sent_by', 'session', 'user_reported','user_profile' )
	def user_profile(self, obj):
		prof = Profile.birth_date
		return prof
admin.site.register(Report, ReportAdmin)

class ProfileAdmin(admin.ModelAdmin):
	#pass
    list_display = ('id', 'birth_date', 'sessions_played','user_report')


    def user_report(self, obj):
	#def user_report(self, obj)
		#all_matching_sessions = []
        total = Report.report_reason
        return total

admin.site.register(Profile, ProfileAdmin)
