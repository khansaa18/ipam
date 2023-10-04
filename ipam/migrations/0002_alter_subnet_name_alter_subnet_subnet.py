# Generated by Django 4.1 on 2023-08-18 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subnet',
            name='name',
            field=models.CharField(db_index=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='subnet',
            name='subnet',
            field=models.GenericIPAddressField(),
        ),
    ]
