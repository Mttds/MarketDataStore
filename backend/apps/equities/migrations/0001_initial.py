# Generated by Django 3.0.5 on 2021-08-25 17:25

import apps.equities.models
import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Equity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(default=datetime.datetime(2021, 8, 25, 17, 25, 10, 447388, tzinfo=utc))),
                ('md_date', models.DateField(default=datetime.date(1900, 1, 1))),
                ('label', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=255)),
                ('industry', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=50)),
                ('currency', models.CharField(max_length=5)),
                ('market', models.CharField(max_length=50)),
                ('exchange', models.CharField(max_length=20)),
                ('market_cap', models.DecimalField(decimal_places=6, max_digits=22)),
                ('p_high', models.DecimalField(decimal_places=6, max_digits=16)),
                ('p_close', models.DecimalField(decimal_places=6, max_digits=16)),
                ('p_low', models.DecimalField(decimal_places=6, max_digits=16)),
                ('p_open', models.DecimalField(decimal_places=6, max_digits=16)),
                ('tickdata', djongo.models.fields.ArrayField(model_container=apps.equities.models.TickData)),
            ],
        ),
    ]
