from datetime import *
from django.shortcuts import render,redirect
from leave.models import *
from custom.models import RequestSet, Holiday
from django.contrib import messages
from settingapps.utils import  decrypt_id
from django.contrib.auth.models import User
from employee.models import EmployeeUser
from leave.forms import RequestLeaveForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from custom.utils import getlastid
from django.db.models import F, Sum




# Fungsi untuk menghitung jumlah hari tanpa Sabtu dan Minggu
def count_weekdays(start_date, end_date):
    today = datetime.today()
    count = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5 and not Holiday.objects.filter(day=current_date, day__year=today.year).exists():  # Hanya hari Senin-Jumat yang dihitung
            count += 1
        current_date += timedelta(days=1)
    return count


def printleaverequest(request, id):
    id = decrypt_id(id)
    
    today = datetime.today()
    leave1 = LeaveRequest.objects.get(id=id)
    leave = LeaveRequest.objects.filter(id=id)

    # Hitung jumlah hari untuk permintaan cuti yang diterima tanpa Sabtu dan Minggu
    leave_days = sum(count_weekdays(leave1.start_date, leave1.end_date) for leave1 in leave)

    leave_type = LeaveType.objects.filter(id=leave1.id, is_active=True)
    data_leave = []

    for leave in leave_type:
        history_leave = LeaveRequest.objects.filter(
            contract=request.contract,
            leavetype=leave,
            start_date__year=today.year,
            is_draft=False,
            category__in=['0','1'],
            is_aproved=True
        ).annotate(
            leave_days=Sum(
                F('end_date') - F('start_date') + 1,
                output_field=models.IntegerField()
            )
        )

        history_leave_half = LeaveRequest.objects.filter(
            contract=request.contract,
            leavetype=leave,
            start_date__year=today.year,
            is_draft=False, category='2',
            is_aproved=True
        ).annotate(
            leave_days=Sum(
                F('end_date') - F('start_date') + 1,
                output_field=models.IntegerField()
            )
        ).count()

        pending_leave = LeaveRequest.objects.filter(
            contract=request.contract,
            leavetype=leave,
            start_date__year=today.year,
            is_draft=False,
            category__in=['0','1'],
            is_aproved=False
        ).annotate(
            leave_days=Sum(
                F('end_date') - F('start_date') + 1,
                output_field=models.IntegerField()
            )
        )

        pending_leave_half = LeaveRequest.objects.filter(
            contract=request.contract,
            leavetype=leave,
            start_date__year=today.year,
            is_draft=False,
            category='2',
            is_aproved=False
        ).annotate(
            leave_days=Sum(
                F('end_date') - F('start_date') + 1,
                output_field=models.IntegerField()
            )
        ).count()

        # history_leave_half = sum(count_weekdays(leave1.start_date, leave1.end_date) for leave1 in history_leave_half)
        history_leave_half = 0.5 * history_leave_half
        # pending_leave_half = sum(count_weekdays(leave1.start_date, leave1.end_date) for leave1 in pending_leave_half)
        pending_leave_half = 0.5 * pending_leave_half


        # Hitung jumlah hari untuk permintaan cuti yang diterima tanpa Sabtu dan Minggu
        history_leave_days = sum(count_weekdays(leave1.start_date, leave1.end_date) for leave1 in history_leave)
        history_leave_days += history_leave_half

        # Hitung jumlah hari untuk permintaan cuti yang masih menunggu tanpa Sabtu dan Minggu
        pending_leave_days = sum(count_weekdays(leave2.start_date, leave2.end_date) for leave2 in pending_leave)
        pending_leave_days += pending_leave_half

        balance_leave = leave.total - history_leave_days
        available_leave = balance_leave - pending_leave_days

        data_leave.append({
            'leave_name': leave.name,
            'balance_leave': balance_leave,
            'history_leave': history_leave_days,
            'pending_leave': pending_leave_days,
            'available_leave': available_leave,
            'total_leave': leave.total,
        })

    context = {
        'tinan': today.year,
        'data_leave': data_leave,
        "leave": leave,
        "leave1": leave1,
        "leave_days": leave_days,
        "pajina_leave": "active",
    }
    return render(request, 'print/leave.html',context)