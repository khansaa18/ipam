import csv

from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.forms import forms
from django.shortcuts import render, get_object_or_404, redirect
from .forms import SubnetForm, SubnetIpAddressForm, LoginForm, SearchForm, SubnetCalculatorForm, CSVUploadForm
from .models import Subnet, SubnetIpAddress
import ipaddress


def index(request):
    if 'username' not in request.session:
        return redirect('login')

    return render(request, 'dashboard/dashboard.html')


def subnet_form(request, subnetname=None):
    if 'username' not in request.session:
        return redirect('login')

    subnet_instance = None

    if subnetname:
        subnet_instance = get_object_or_404(Subnet, name=subnetname)

    if request.method == "POST":
        form = SubnetForm(request.POST, instance=subnet_instance)
        if form.is_valid():
            form.save()
            return redirect('/subnet')
    else:
        form = SubnetForm(instance=subnet_instance)

    query_results = Subnet.objects.all()

    return render(request, 'subnet/subnet.html', {'form': form, 'query_results': query_results})


def delete_subnet(request, id):
    subnet_instance = get_object_or_404(Subnet, id=id)
    subnet_instance.delete()
    return redirect('/subnet')


def subnetipaddress_form(request, subnetname=None):
    if 'username' not in request.session:
        return redirect('login')

    page_number = 1
    if request.GET.get('page'):
        page_number = request.GET.get('page')

    if subnetname is None:
        return redirect('/subnet')

    subnetItem = get_object_or_404(Subnet, name=subnetname)
    subnet = subnetItem.subnet

    subnetIps, availableIpAddressChoices = GetSubnetIpListAndAvailableIps(subnet)

    if request.method == "POST":
        subnetipform = SubnetIpAddressForm(request.POST)
        subnetipform.fields['ipaddress'].choices = availableIpAddressChoices
        if subnetipform.is_valid():
            subnetipform.save()
            subnetIps, availableIpAddressChoices = GetSubnetIpListAndAvailableIps(subnet)
            subnetipform = SubnetIpAddressForm(initial={'subnet': subnet, 'ipaddress': availableIpAddressChoices})
            subnetipform.fields['ipaddress'].choices = availableIpAddressChoices

    else:
        subnetipform = SubnetIpAddressForm(initial={'subnet': subnet, 'ipaddress': availableIpAddressChoices})
        subnetipform.fields['ipaddress'].choices = availableIpAddressChoices

    paginator = Paginator(subnetIps, 5)
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    if (int(page_number) - 1) > 0 and (int(page_number) - 1) % 5 == 0:
        pagerange = range(int(page_number), int(page_number) + 5)
    else:
        if paginator.num_pages > 5:
            pagerange = range(1, 5)
        else:
            pagerange = range(1, paginator.num_pages + 1)

    page_obj = paginator.get_page(page_number)

    return render(request, 'ipaddress/addsubnetip.html',
                  {'subnetipform': subnetipform, 'subnet': subnet, 'pagerange': pagerange, 'page_obj': page_obj,
                   'totalitems': len(subnetIps)})


def login_view(request):
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.cleaned_data['email']
            password = loginform.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['username'] = user.username
                return redirect('/home')  # Replace 'homepage' with your homepage URL name
            else:
                error_message = "Invalid username or password"
    else:
        loginform = LoginForm()
        error_message = ""

    return render(request, 'login/login.html', {'loginform': LoginForm, 'error_message': error_message})


def logout_view(request):
    print('Logout')
    if 'username' in request.session:
        del request.session['username']
    logout(request)
    return redirect('login')


def view_subnet_ips(request):
    searchText = request.GET.get('search')
    selectedsubnet = request.GET.get('subnet')
    if searchText:
        searchForm = SearchForm(initial={'search': searchText, 'subnet': selectedsubnet})
    else:
        searchForm = SearchForm(initial={'subnet': selectedsubnet})

    page_number = 1
    if request.GET.get('page'):
        page_number = request.GET.get('page')

    if searchText:
        ips = SubnetIpAddress.objects.filter((Q(ipaddress__contains=searchText) | Q(machine__contains=searchText)) & Q(subnet=selectedsubnet))
    else:
        ips = SubnetIpAddress.objects.filter(subnet=selectedsubnet)

    subnets = Subnet.objects.all()
    subnetipchoices = []
    subnetIps = [item.subnet for item in subnets]
    for subnetip in subnetIps:
        subnetChoice = (subnetip, subnetip)
        subnetipchoices.append(subnetChoice)

    searchForm.fields['subnet'].choices = subnetipchoices

    paginator = Paginator(ips, 5)
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    if (int(page_number) - 1) > 0 and (int(page_number) - 1) % 5 == 0:
        pagerange = range(int(page_number), int(page_number) + 5)
    else:
        if paginator.num_pages > 5:
            pagerange = range(1, 5)
        else:
            pagerange = range(1, paginator.num_pages + 1)

    page_obj = paginator.get_page(page_number)

    return render(request, 'subnet/subnetipslist.html',
                  {'searchform': searchForm, 'ips': ips, 'subnets': subnets, 'pagerange': pagerange,
                   'page_obj': page_obj, 'totalitems': len(ips)})


def delete_subnet_ip(request, ipaddress):
    searchText = request.GET.get('search')
    selectedsubnet = request.GET.get('subnet')
    pagenumber = request.GET.get('page')

    subnet_ip_instance = get_object_or_404(SubnetIpAddress, ipaddress=ipaddress)
    subnet_ip_instance.delete()

    return redirect(f'/viewSubnetIps?subnet={selectedsubnet}&page={pagenumber}&search={searchText}')


def subnet_calculator(request):
    if request.method == 'POST':
        form = SubnetCalculatorForm(request.POST)
        if form.is_valid():
            ip = form.cleaned_data['ip_address']
            subnet_mask = form.cleaned_data['subnet_mask']

            network = ipaddress.IPv4Network(f'{ip}/{subnet_mask}', strict=False)

            context = {
                'form': form,
                'network': network,
            }
            return render(request, 'subnet/subnetcalculator.html', context)
    else:
        form = SubnetCalculatorForm()

    context = {'form': form}
    return render(request, 'subnet/subnetcalculator.html', context)


def GetSubnetIpListAndAvailableIps(subnetip):
    possibleIps = []
    network = ipaddress.ip_network(subnetip)
    for ip in network.hosts():
        possibleIps.append(str(ip))

    subnetIps = SubnetIpAddress.objects.filter(subnet=subnetip)
    ipaddressUsed = [item.ipaddress for item in subnetIps]

    availableIpAddress = [item for item in possibleIps if item not in ipaddressUsed]

    availableIpAddressChoices = []
    for ip in availableIpAddress:
        ipAddressChoice = (ip, ip)
        availableIpAddressChoices.append(ipAddressChoice)

    return subnetIps, availableIpAddressChoices


def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            # Convert the file content to a string
            file_content = csv_file.read().decode('utf-8')

            # Create a StringIO object to make it compatible with csv.DictReader
            from io import StringIO
            csv_stringio = StringIO(file_content)

            csv_reader = csv.DictReader(csv_stringio)

            with transaction.atomic():
                for row in csv_reader:
                    if Subnet.objects.filter(subnet=row['Subnet']).exists():
                        print('Subnet already exists skipping creation')
                    else:
                        Subnet.objects.create(
                            name=row['SubnetName'],
                            subnet=row['Subnet'],
                            description=row['SubnetDescription']
                        )

                    if SubnetIpAddress.objects.filter(ipaddress=row['SubnetIp']).exists():
                        transaction.set_rollback(True)
                        raise forms.ValidationError('Duplicate subnet ip detected')

                    SubnetIpAddress.objects.create(
                        subnet=row['Subnet'],
                        ipaddress=row['SubnetIp'],
                        machine=row['AssignedTo'],
                        description=row['IpDescription']
                    )

            return redirect('/uploadcsv')
    else:
        form = CSVUploadForm()

    return render(request, 'csv/uploadcsv.html', {'form': form})
