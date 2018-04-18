from django.contrib import admin
from ..api.models import Profile, Availability, Game, Game_Role, Session, Session_Profile, Report, Profile_Connected_Game_Account, Feedback
from django.db.models import Count

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
    list_display = ('id', 'birth_date', 'sessions_played','total_reports')
    def total_reports(self, obj):
        return Report.objects.filter(user_reported=obj).count()
admin.site.register(Profile, ProfileAdmin)
