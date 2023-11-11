from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from leave.models import *
from import_export import resources

# Register your models here.
class LeaveTypeResource(resources.ModelResource):
    class Meta:
        model = LeaveType
class LeaveTypeAdmin(ImportExportModelAdmin):
    resource_class = LeaveTypeResource
admin.site.register(LeaveType, LeaveTypeAdmin)

class LeaveRequestResource(resources.ModelResource):
    class Meta:
        model = LeaveRequest
class LeaveRequestAdmin(ImportExportModelAdmin):
    resource_class = LeaveRequestResource
admin.site.register(LeaveRequest, LeaveRequestAdmin)

class RequestLeaveAproveResource(resources.ModelResource):
    class Meta:
        model = RequestLeaveAprove
class RequestLeaveAproveAdmin(ImportExportModelAdmin):
    resource_class = RequestLeaveAproveResource
admin.site.register(RequestLeaveAprove, RequestLeaveAproveAdmin)
