# Generated by Django 4.1.5 on 2023-04-07 18:19

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_customerpoints_give_point_eligible_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurantqr',
            name='code',
            field=models.UUIDField(default=uuid.UUID('f64e0acd-f3ad-4b40-9c88-e5fde10599f5')),
        ),
        migrations.AlterField(
            model_name='restaurantqr',
            name='default_qr',
            field=models.CharField(default='f64e0acd-f3ad-4b40-9c88-e5fde10599f5|https://apps.apple.com/app/punchme/id6447275121', max_length=255),
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customer')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.restaurant')),
            ],
        ),
    ]
