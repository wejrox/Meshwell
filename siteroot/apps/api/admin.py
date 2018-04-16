from django.contrib import admin
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Game_Api_Connection, Feedback
from django.db.models import Count

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
	list_display = ('user_reported', 'report_reason', 'sent_by', 'session')
admin.site.register(Report, ReportAdmin)

class ProfileAdmin(admin.ModelAdmin):
<<<<<<< HEAD
	#pass
    list_display = ('id', 'birth_date', 'sessions_played','user_report')


    def user_report(self, obj):
	#def user_report(self, obj)
		#all_matching_sessions = []
        total = Report.report_reason
        return total

=======
    list_display = ('id', 'birth_date', 'sessions_played','total_reports')
    def total_reports(self, obj):
        return Report.objects.filter(user_reported=obj).count()
>>>>>>> 7b61725c6c091f34bc82b9edef41f5d9d728836c
admin.site.register(Profile, ProfileAdmin)
