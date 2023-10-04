from django import forms
from django.forms import TextInput, EmailInput, PasswordInput

from .models import Subnet, SubnetIpAddress


class SubnetForm(forms.ModelForm):
    class Meta:
        model = Subnet
        fields = ["name", "subnet", "description"]
        labels = {'name': "Name", "subnet": "IP", "description": "Description"}
        widgets = {
            'name': TextInput(attrs={
                'class': "form-control"
            }),
            'subnet': TextInput(attrs={
                'class': "form-control"
            }),
            'description': TextInput(attrs={
                'class': "form-control"
            })
        }


class SubnetIpAddressForm(forms.ModelForm):
    class Meta:
        model = SubnetIpAddress
        fields = '__all__'

    subnet = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), label="Subnet")
    ipaddress = forms.ChoiceField(label="Ip Address", widget=forms.Select(attrs={'class': 'form-control'}))
    machine = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Assigned To")
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Description")


class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Email address")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Password")


class SearchForm(forms.Form):
    subnet = forms.ChoiceField(label="Subnets", widget=forms.Select(attrs={'class': 'form-control'}))
    search = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Search", required=False)


class SubnetCalculatorForm(forms.Form):
    ip_address = forms.GenericIPAddressField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    subnet_mask = forms.IntegerField(min_value=0, max_value=32, widget=forms.TextInput(attrs={'class': 'form-control'}))


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
