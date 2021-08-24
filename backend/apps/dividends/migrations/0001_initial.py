# Generated by Django 3.0.5 on 2021-08-24 09:00

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('equities', '0003_equity_md_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dividend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=4)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('ex_div_date', models.DateField(default=datetime.date(1900, 1, 1))),
                ('dividend', models.DecimalField(decimal_places=10, max_digits=20)),
                ('equity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='equities.Equity')),
            ],
        ),
    ]