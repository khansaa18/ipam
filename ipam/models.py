from django.core.validators import validate_ipv46_address
from django.db import models
from swapper import get_model_name


class Subnet(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=False)
    subnet = models.CharField(max_length=100, blank=False,
                                          help_text="Enter a valid CIDR notation (e.g., 192.168.0.0/24)")
    description = models.CharField(max_length=100, blank=True)


class SubnetIpAddress(models.Model):
    subnet = models.CharField(max_length=100, blank=True)
    ipaddress = models.CharField(max_length=100, blank=True)
    machine = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=200, blank=True)
