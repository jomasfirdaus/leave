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


def listaleaverequest(request):
    data = EmployeeUser.objects.get(user=request.user.id, user__is_active = True)
    contract =Contract.objects.get(employeeuser=data, is_active=True)
    today = datetime.today()
    dadosta = LeaveRequest.objects.filter(contract=contract).order_by('-id')

    leave_type = LeaveType.objects.filter(is_active=True)
    data_leave = []

    for leave in leave_type:
        history_leave = LeaveRequest.objects.filter(contract=contract, leavetype=leave, start_date__year=today.year, is_draft=False, is_historical=True)
        pending_leave = LeaveRequest.objects.filter(contract=contract, leavetype=leave, start_date__year=today.year, is_draft=False, is_historical=False)
        drafting_leave = LeaveRequest.objects.filter(contract=contract, leavetype=leave, start_date__year=today.year, is_draft=True)

        # Hitung jumlah hari untuk permintaan cuti yang diterima tanpa Sabtu dan Minggu
        history_leave_days = sum(count_weekdays(leave.start_date, leave.end_date) for leave in history_leave)

        # Hitung jumlah hari untuk permintaan cuti yang masih menunggu tanpa Sabtu dan Minggu
        pending_leave_days = sum(count_weekdays(leave.start_date, leave.end_date) for leave in pending_leave)

        # Hitung jumlah hari untuk permintaan cuti yang masih menunggu tanpa Sabtu dan Minggu
        drafting_leave_days = sum(count_weekdays(leave.start_date, leave.end_date) for leave in drafting_leave)

        balance_leave = leave.total - history_leave_days
        available_leave = balance_leave - pending_leave_days - drafting_leave_days

        data_leave.append({
            'leave_name': leave.name,
            'balance_leave': balance_leave,
            'history_leave': history_leave_days,
            'pending_leave': pending_leave_days,
            'drafting_leave': drafting_leave_days,
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
    today = datetime.today()

    form = RequestLeaveForm()

    if request.method == 'POST':
        form = RequestLeaveForm(request.POST)
        if form.is_valid():
            _, newid = getlastid(LeaveRequest)
            instance = form.save(commit=False)

            # Initial Variable
            leavetype = request.POST.get('leavetype')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_work_date = request.POST.get('start_work_date')

            available_leave = 0
            total_leave_days = 0

            # Total Leave per Leave Type
            leave_type = LeaveType.objects.get(id=leavetype)
            leave_type_days = int(leave_type.total)

            # Count between Start Date and End Date
            date2 = datetime.strptime(end_date, '%Y-%m-%d')
            date1 = datetime.strptime(start_date, '%Y-%m-%d')
            total_request_leave = date2 - date1

            # Weekend and Holiday Check
            for i in range(total_request_leave.days + 1):
                day = date1 + timedelta(days=i)
                if day.weekday() < 5: # 5 represents Saturday, 6 represents Sunday
                    total_leave_days += 1
            
            # Count Requested and Aproved Leave
            history_leave = LeaveRequest.objects.filter(contract=contract, leavetype=leave_type, start_date__year=today.year, is_draft__in=['False','True'])
            
             # Hitung jumlah hari untuk permintaan cuti yang diterima tanpa Sabtu dan Minggu
            history_leave_days = sum(count_weekdays(leave.start_date, leave.end_date) for leave in history_leave)

            if history_leave_days is not None:
                available_leave = leave_type_days - history_leave_days
            else:
                available_leave = leave_type_days

            # Check Available Leave
            if not LeaveRequest.objects.filter(contract=contract,leavetype=leavetype, start_date__year=today.year).exists():
                # Request Leave can not > Total Leave Type
                if total_leave_days > leave_type_days:
                    messages.success(request, f'Sorry! Your request must be less then or equal {leave_type.total} days. Otherwise your request is/are {total_leave_days} days')
                    return redirect('leave:requestleave')
                else:
                    Leave = LeaveRequest.objects.create(id=newid,created_by=request.user,contract=contract,leavetype_id=leavetype,start_date=start_date,end_date=end_date,start_work_date=start_work_date)

                    messages.success(request, 'Request created successfully.')  # Success message
                    return redirect('leave:listaleaverequest')
            elif available_leave > 0:
                # Request Leave can not > Available Leave
                if total_leave_days > available_leave:
                    messages.success(request, f'Sorry! Your request must be less then or equal {available_leave} days. Otherwise your request is/are {total_leave_days} days')
                    return redirect('leave:requestleave')
                else:
                    Leave = LeaveRequest.objects.create(id=newid,created_by=request.user,contract=contract,leavetype_id=leavetype,start_date=start_date,end_date=end_date,start_work_date=start_work_date)

                    messages.success(request, 'Request created successfully.')  # Success message
                    return redirect('leave:listaleaverequest')
            else:
                messages.success(request, f'Sorry! Your Leave is not Available for Leave Type ({leave_type.name})')
                return redirect('leave:requestleave')
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


# def editrequestleave(request, id):
#     id = decrypt_id(id)
#     leaverequest = LeaveRequest.objects.get(id=id)
#     form = RequestLeaveForm(instance=leaverequest)  # Menggunakan instance=leaverequest

#     if request.method == 'POST':
#         form = RequestLeaveForm(request.POST, instance=leaverequest)  # Menggunakan instance=leaverequest
#         if form.is_valid():
#             instance = form.save(commit=False)
#             instance.save()
#             messages.success(request, 'Request updated successfully.')  # Pesan sukses
#             return redirect('leave:listaleaverequest')
#         else:
#             messages.error(request, 'There was an error. Please correct the form.')  # Pesan kesalahan
#             return redirect('leave:requestleave')

#     context = {
#         "form": form,
#         "pajina_leave": "active",
#     }
#     return render(request, 'leave/request_leave.html', context)


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

    try:
        request_leave_aprove = RequestLeaveAprove.objects.filter(leaverequest__id=id)
        request_leave_aprove.delete()
    except ObjectDoesNotExist:
        print("RequestLeaveAprove instance not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    unique_group_names = RequestSet.objects.filter(category__name='leave_request').values('group__name').distinct()
    for group_name in unique_group_names:
        group_users = User.objects.filter(groups__name=group_name['group__name'], is_active=True)
        for user in group_users:

            employeeuser = EmployeeUser.objects.filter(user=request.user).last()
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

    requestleave = LeaveRequest.objects.get(id=id)
    requestleave.is_draft = False
    requestleave.save()

    return redirect('leave:listaleaverequest')


def cancelLeaveRequest(request, id):
    id = decrypt_id(id)
    data = LeaveRequest.objects.get(id=id)
    data.delete(request.user)
    messages.success(request, f'Leave Suceesfully Deleted')
    return redirect('leave:listaleaverequest')