# Generated by Django 4.1.5 on 2023-03-28 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_restaurant_item1_alter_restaurant_item1_points_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerPoints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_points', models.IntegerField(default=0)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customer')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.restaurant')),
            ],
        ),
    ]
