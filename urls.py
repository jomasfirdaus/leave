from django.urls import path 

from leave import views

app_name = "leave"

urlpatterns = [
	path('lista/leave/request', views.listaleaverequest, name='listaleaverequest'),
	path('request/leave', views.requestleave, name='requestleave'),
	path('detallu/leave/request/<str:id>/', views.detalluleaverequest, name='detalluleaverequest'),
	path('edit/request/leave/<str:id>/', views.editrequestleave, name='editrequestleave'),
    
	path('send/leave/request/<str:id>/', views.sendleaverequest, name='sendleaverequest'),
	path('cancel/leave/request/<str:id>/', views.cancelLeaveRequest, name='cancelLeaveRequest'),
    
	path('accept/leave/request/<str:id>/<str:last>/', views.acceptedleaverequest, name='acceptedleaverequest'),
	path('reject/leave/request/<str:id>/', views.rijectedpurchaserequest, name='rijectedpurchaserequest'),
]

