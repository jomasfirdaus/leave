from django.shortcuts import render, redirect
from django.contrib import messages

from settingapps.utils import  decrypt_id, encrypt_id

from leave.models import LeaveRequest, RequestLeaveAprove
from leave.forms import LeaveRequestAproveForm



def acceptedleaverequest(request, id, last):
    form = LeaveRequestAproveForm()

    last = decrypt_id(last)

    id_decrypt = decrypt_id(id)
    dados = RequestLeaveAprove.objects.get(id=id_decrypt)
    idrequest = LeaveRequest.objects.get(id = dados.leaverequest.id)
    idrequest2 = encrypt_id(str(idrequest.id))

    if request.method == 'POST':
        form = LeaveRequestAproveForm(request.POST, instance = dados )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = "Acepted"
            instance.updated_by = request.user
            instance.save()
            if last == 'last':
                idrequest.is_aproved=True
                idrequest.save()
            messages.success(request, 'Success!')  # Success message
            return redirect('leave:detalluleaverequest', id = idrequest2)
        else:
            messages.success(request, 'Fail!')  # Success message
            return redirect('leave:detalluleaverequest', id = idrequest2)


    context = {
        "form" : form,
        "asaun" : "aceita",
        "dados" : dados ,
        "pajina_leave" : "active",
            }
    return render(request, 'leave/leave__actiondescription.html',context)


def rijectedpurchaserequest(request, id):
    form = LeaveRequestAproveForm()

    id_decrypt = decrypt_id(id)
    dados = RequestLeaveAprove.objects.get(id=id_decrypt)
    idrequest = LeaveRequest.objects.get(id = dados.leaverequest.id)
    idrequest2 = encrypt_id(str(idrequest.id))

    if request.method == 'POST':
        form = LeaveRequestAproveForm(request.POST, instance = dados )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.status = "Rejected"
            instance.updated_by = request.user
            instance.save()
            idrequest.is_draft = True
            idrequest.save()
            messages.success(request, 'Success!')  # Success message
            return redirect('leave:detalluleaverequest', id = idrequest2)
        else:
            messages.success(request, 'Fail!')  # Success message
            return redirect('leave:detalluleaverequest', id = idrequest2)


    context = {
        "form" : form,
        "asaun" : "rejeita",
        "dados" : dados ,
        "pajina_leave" : "active",
            }
    return render(request, 'leave/leave__actiondescription.html',context)




