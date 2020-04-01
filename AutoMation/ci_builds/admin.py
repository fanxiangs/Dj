from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Project, Bulletin, SmokeyResult, AutoResult, AutoRes, AutoProblemList


class ShowAutoResult(admin.ModelAdmin):
    list_display = ["VersionPath", "Time", "VersionModel", "NE", "Result"]


class ShowAutoRes(admin.ModelAdmin):
    list_display = ["Date", "VersionNum", "VersionPath", "options"]


class ShowSmokeResult(admin.ModelAdmin):
    list_display = ["date", "time", "res"]


class ShowAutoProblemList(admin.ModelAdmin):
    list_display = ["DiscoveryDate", "short_describe", 'NE', 'SeverityLevel', "Status"]


admin.site.register(Project)
admin.site.register(Bulletin)
admin.site.register(SmokeyResult, ShowSmokeResult)
admin.site.register(AutoResult, ShowAutoResult)
admin.site.register(AutoRes, ShowAutoRes)
admin.site.register(AutoProblemList, ShowAutoProblemList)
