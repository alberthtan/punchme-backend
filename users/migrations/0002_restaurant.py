# Generated by Django 4.1.5 on 2023-03-28 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('item1', models.CharField(max_length=255)),
                ('item1_points', models.IntegerField()),
                ('item2', models.CharField(max_length=255)),
                ('item2_points', models.IntegerField()),
                ('item3', models.CharField(max_length=255)),
                ('item3_points', models.IntegerField()),
                ('manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant', to='users.manager')),
            ],
        ),
    ]
