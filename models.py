from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User, Group
from contract.models import Contract
from employee.models import EmployeeUser

# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class LeaveType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    year = models.CharField(max_length=4)
    total = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="LeaveTypecreatedbys")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="LeaveTypeupdatetedbys")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="LeaveTypedeletedbys")
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        template = '{0.name}'
        return template.format(self)
    
    def delete(self, user):
        self.deleted_at = str(timezone.now())
        self.deleted_by = user
        self.save()

    default_objects = models.Manager()  # The default manager
    objects = ActiveManager()

    class Meta:
        verbose_name_plural='01-Data-Leave-LeaveType'


class LeaveRequest(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=False, related_name="LeaveRequestcontract")
    category = models.CharField(choices=[('0','Part Day'), ('1','Multiple Days'), ('2','Half Day')], max_length=1)
    leavetype = models.ForeignKey(LeaveType, on_delete=models.CASCADE, null=True, blank=False, related_name="LeaveRequestleavetype")
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    start_work_date = models.DateField(null=True, blank=True)
    is_draft = models.BooleanField(default=True)
    is_afternoon = models.BooleanField(default=False)
    is_aproved = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="LeaveRequestcreatedby")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="LeaveRequestupdatedby")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="LeaveRequestdeletedby")
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        template = '{0.is_draft}'
        return template.format(self)

    def total(self):
        return int(round((self.end_date - self.start_date)))
    
    def delete(self, user):
        self.deleted_at = str(timezone.now())
        self.deleted_by = user
        self.save()

    default_objects = models.Manager()  # The default manager
    objects = ActiveManager()

    class Meta:
        verbose_name_plural='1-Data-Leave-LeaveRequest'


class RequestLeaveAprove(models.Model):
    leaverequest = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, null=True, blank=False, related_name="RequestLeaveAproveleaverequest")
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=False, related_name="RequestLeaveAproveuser")
    status = models.CharField(choices=[('Review','Review'),('Acepted','Acepted'),('Rejected','Rejected')],max_length=30, null=True, blank=True)
    description = models.TextField(null=False, blank=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="RequestLeaveAprovecreatedby")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="RequestLeaveAproveupdatedby")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="RequestLeaveAprovedeletedby")
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        template = '{0.status}'
        return template.format(self)
    
    def delete(self, user):
        self.deleted_at = str(timezone.now())
        self.deleted_by = user
        self.save()

    default_objects = models.Manager()  # The default manager
    objects = ActiveManager()

    class Meta:
        verbose_name_plural='1-Data-Purchase_Request-Request_Order_Aprove'