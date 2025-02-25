# Generated by Django 4.1.5 on 2023-04-06 18:36

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_restaurantqr_default_qr_alter_restaurantqr_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurantqr',
            name='code',
            field=models.UUIDField(default=uuid.UUID('f99dfd3e-f6b5-45c0-aa61-10cebba2989e')),
        ),
        migrations.AlterField(
            model_name='restaurantqr',
            name='default_qr',
            field=models.CharField(default='f99dfd3e-f6b5-45c0-aa61-10cebba2989e|https://apps.apple.com/app/punchme/id6447275121', max_length=255),
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_creator_set', to='users.customer')),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_set', to='users.customer')),
            ],
            options={
                'unique_together': {('customer', 'friend')},
            },
        ),
    ]
