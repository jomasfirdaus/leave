from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
# from population.models import Population,DetailFamily,Family,Religion,Profession,Citizen,Aldeia,Village,User,Migration,Death,Migrationout,Temporary,ChangeFamily
# from population.utils import getnewidp,getnewidf
# from population.forms import Family_form,Family_form,FamilyPosition,Population_form,DetailFamily_form,CustumDetailFamily_form,Death_form,Migration_form,Migrationout_form,Changefamily_form
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone

# from custom.utils import getnewid, getjustnewid, hash_md5, getlastid
from django.db.models import Count
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date
from django.http import JsonResponse

from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from rekrutamentu.forms import FileUploadForm
from leave.models import *
from custom.models import RequestSet

from settingapps.utils import  decrypt_id, encrypt_id
from django.core.paginator import Paginator

from django.utils import translation
from django.utils import timezone
from datetime import datetime

from django.contrib.auth.models import User, Group

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from purchase_request.forms import RequestOrderForm, ItemRequestForm
from employee.models import EmployeeUser
import logging
from django.core.exceptions import ObjectDoesNotExist



def aceptedleaverequest(request, id):
    id = decrypt_id(id)
    itemprosses = RequestLeaveAprove.objects.get(id=id)
    id_request = encrypt_id(str(itemprosses.leaverequest.id))
    item = itemprosses
    item.status = "Acepted"
    last_aprove = RequestLeaveAprove.objects.filter(id=id, status="Acepted").count()
    if  last_aprove < 1:
        item.is_historical = True
    item.save()
    return redirect('leave:detalluleaverequest', id = id_request )


def rijectedleaverequest(request, id):
    id = decrypt_id(id)
    itemprosses = RequestOrderAprove.objects.get(id=id)
    id_request = encrypt_id(str(itemprosses.request_order.id))
    item = itemprosses
    item.status = "Rejected"
    item.save()
    return redirect('leave:detalluleaverequest', id = id_request )




