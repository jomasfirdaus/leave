from datetime import *
from django.shortcuts import render,redirect
from leave.models import *
from custom.models import RequestSet
from django.contrib import messages
from settingapps.utils import  decrypt_id
from django.contrib.auth.models import User
from employee.models import EmployeeUser
from leave.forms import RequestLeaveForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from custom.utils import getlastid
from django.db.models import F, Sum


#Your Code Here

# Fungsi untuk menghitung jumlah hari tanpa Sabtu dan Minggu
def count_weekdays(start_date, end_date):
    count = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Hanya hari Senin-Jumat yang dihitung
            count += 1
        current_date += timedelta(days=1)
    return count


def check_date(date):
    today = datetime.today()
    today = today - timedelta(days=1)
    status = False

    if date <= today.date():
        status = True
    else:
        status = False

    return status


def listaleaverequest(request):
    data = EmployeeUser.objects.get(user=request.user.id, user__is_active = True)
    contract =Contract.objects.get(employeeuser=data, is_active=True)
    today = datetime.today()
    dadosta = LeaveRequest.objects.filter(contract=contract, created_at__year=today.year).order_by('-id')

    leave_type = LeaveType.objects.filter(is_active=True)
    data_leave = []

    for leave in leave_type:
        history_leave = LeaveRequest.objects.filter(
            contract=contract,
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
            contract=contract,
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
            contract=contract,
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
            contract=contract,
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

        history_leave_half = 0.5 * history_leave_half
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
        'leave_type': leave_type,
        "dadosta" : dadosta,
        "pajina_leave" : "active",
    }
    return render(request, 'leave/leave.html',context)

def requestleave(request):
    data = EmployeeUser.objects.get(user=request.user.id, user__is_active = True)
    contract =Contract.objects.get(employeeuser=data, is_active=True)
    form = RequestLeaveForm()

    if request.method == 'POST':
        form = RequestLeaveForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.contract = contract
            instance.created_by = User.objects.get(id=request.user.id)

            # Jika kategori adalah 'Part Day' atau 'Half Day', set end_date sama dengan start_date
            if instance.category in ['0', '2']:  # '0' untuk 'Part Day', '2' untuk 'Half Day'
                instance.end_date = instance.start_date
                if instance.category == '2':
                    if instance.is_afternoon == False:
                        instance.start_work_date = instance.start_date
            
            if instance.category in ['0', '1']:
                instance.is_afternoon = False

            instance.save()
            messages.success(request, ' DraftLeave Request.')  # Success message
            return redirect('leave:listaleaverequest')
        else:
            error_messages = []  # Initialize an empty list to store custom error messages
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            print(str(error_messages))
            messages.error(request, 'There was an error. Please correct the form.')  # Error message
            return redirect('leave:requestleave')

    context = {
        "form" : form,
        "pajina_leave" : "active",
        "data": data,
    }
    return render(request, 'leave/request_leave.html',context)


def editrequestleave(request, id):
    id = decrypt_id(id)
    leaverequest = LeaveRequest.objects.get(id=id)
    form = RequestLeaveForm(instance=leaverequest)  # Menggunakan instance=leaverequest

    if request.method == 'POST':
        form = RequestLeaveForm(request.POST, instance=leaverequest)  # Menggunakan instance=leaverequest
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, 'Request updated successfully.')  # Pesan sukses
            return redirect('leave:listaleaverequest')
        else:
            messages.error(request, 'There was an error. Please correct the form.')  # Pesan kesalahan
            return redirect('leave:requestleave')

    context = {
        "form": form,
        "pajina_leave": "active",
    }
    return render(request, 'leave/request_leave.html', context)


def detalluleaverequest(request, id):
    id = decrypt_id(id)
    leaverequest = LeaveRequest.objects.get(id=id)

    timeline = RequestLeaveAprove.objects.filter(leaverequest=id)


    context = {

        "leaverequest" : leaverequest,
        "pajina_leave" : "active",
        "timeline" : timeline,
    }
    return render(request, 'leave/detallu_leaverequest.html',context)


def sendleaverequest(request, id):

    id = decrypt_id(id)
    data = EmployeeUser.objects.get(user=request.user.id, user__is_active = True)
    contract =Contract.objects.get(employeeuser=data, is_active=True)
    today = datetime.today()

    requestleave = LeaveRequest.objects.get(id=id)

    available_leave = 0
    total_leave_days = 0

    # Total Leave per Leave Type
    leave_type = LeaveType.objects.get(id=requestleave.leavetype.id)
    leave_type_days = int(leave_type.total)

    # Count between Start Date and End Date
    date2 = requestleave.end_date
    date1 = requestleave.start_date
    total_request_leave = date2 - date1

    # Weekend and Holiday Check
    for i in range(total_request_leave.days + 1):
        day = date1 + timedelta(days=i)
        if day.weekday() < 5: # 5 represents Saturday, 6 represents Sunday
            total_leave_days += 1
    
    # Count Requested and Aproved Leave
    history_leave = LeaveRequest.objects.filter(contract=contract, leavetype=leave_type, start_date__year=today.year, is_draft='False')

    # Hitung jumlah hari untuk permintaan cuti yang diterima tanpa Sabtu dan Minggu
    history_leave_days = sum(count_weekdays(leave.start_date, leave.end_date) for leave in history_leave)

    if history_leave_days is not None:
        available_leave = leave_type_days - history_leave_days
    else:
        available_leave = leave_type_days

    # Check Available Leave
    if not LeaveRequest.objects.filter(contract=contract,leavetype=requestleave.leavetype, start_date__year=today.year).exists():
        # Request Leave can not > Total Leave Type
        if total_leave_days > leave_type_days:
            messages.success(request, f'Sorry! Your request must be less then or equal {leave_type.total} days. Otherwise your request is/are {total_leave_days} days')
            return redirect('leave:requestleave')
        else:
            executeLeaveRequestSend(request, id)
            requestleave.is_draft = False
            requestleave.save()

            messages.success(request, 'Request created successfully.')  # Success message
            return redirect('leave:listaleaverequest')
    elif available_leave > 0:
        # Request Leave can not > Available Leave
        if total_leave_days > available_leave:
            messages.success(request, f'Sorry! Your request must be less then or equal {available_leave} days. Otherwise your request is/are {total_leave_days} days')
            return redirect('leave:listaleaverequest')
        else:
            requestleave.is_draft = False
            requestleave.save()
            executeLeaveRequestSend(request, id)

            messages.success(request, 'Request created successfully.')  # Success message
            return redirect('leave:listaleaverequest')
    else:
        messages.success(request, f'Sorry! You have no balance Leave Available for Leave Type ({leave_type.name})')
        return redirect('leave:listaleaverequest')


def cancelLeaveRequest(request, id):
    id = decrypt_id(id)
    data = LeaveRequest.objects.get(id=id)
    data.delete(request.user)
    messages.success(request, f'Leave Suceesfully Deleted')
    return redirect('leave:listaleaverequest')

def executeLeaveRequestSend(request, id):
    try:
        request_leave_aprove = RequestLeaveAprove.objects.filter(leaverequest__id=id)
        request_leave_aprove.delete(request.user)
    except ObjectDoesNotExist:
        print("RequestLeaveAprove instance not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    unique_group_names = RequestSet.objects.filter(category__name='leave').values('group__name').distinct()
    for group_name in unique_group_names:
        group_users = User.objects.filter(groups__name=group_name['group__name'], is_active=True)
        for user in group_users:

            employeeuser = EmployeeUser.objects.filter(user=user.id).last()
            contract = Contract.objects.filter(employeeuser=employeeuser).last()

            addtimeline = RequestLeaveAprove()
            addtimeline.leaverequest = LeaveRequest.objects.get(id=id)
            addtimeline.contract = contract
            addtimeline.status = "Review"
            addtimeline.created_by = request.user
            try:
                addtimeline.save()
            except Exception as e:
                logger.error(f"Error saving RequestLeaveAprove: {str(e)}")