from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('subnet', subnet_form, name='subnetform'),
    path('actionUrl/<str:subnetname>/', subnet_form,name='actionUrl'),
    path('deleteSubnet/<str:id>/', delete_subnet, name='deleteSubnet'),
    path('addSubnetIp/<str:subnetname>/', subnetipaddress_form, name='addSubnetIp'),
    path('viewSubnetIps', view_subnet_ips, name='viewSubnetIps'),
    path('deleteSubnetIp/<str:ipaddress>/', delete_subnet_ip, name='deleteSubnetIp'),
    path('subnetcalculator', subnet_calculator, name='subnetcalculator'),
    path('uploadcsv', upload_csv, name='uploadcsv'),
]
