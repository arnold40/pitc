# Generated by Django 5.2 on 2025-05-07 15:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('quarter_from', models.CharField(max_length=2)),
                ('year_from', models.IntegerField()),
                ('quarter_to', models.CharField(max_length=2)),
                ('year_to', models.IntegerField()),
                ('pdf_report', models.FileField(blank=True, null=True, upload_to='reports/')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderReportResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_orders', models.IntegerField()),
                ('total_revenue', models.DecimalField(decimal_places=2, max_digits=10)),
                ('average_order_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('orders_per_service_provider', models.JSONField(blank=True, help_text='Distribution of orders across service providers', null=True)),
                ('orders_per_account_manager', models.JSONField(blank=True, help_text='Distribution of orders across account managers', null=True)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stat_analysis.report')),
            ],
        ),
        migrations.CreateModel(
            name='JobReportResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_jobs', models.IntegerField()),
                ('avg_completion_time_regular', models.FloatField(blank=True, null=True)),
                ('avg_completion_time_wafer_run', models.FloatField(blank=True, null=True)),
                ('num_created', models.IntegerField(default=0)),
                ('num_active', models.IntegerField(default=0)),
                ('num_completed', models.IntegerField(default=0)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stat_analysis.report')),
            ],
        ),
        migrations.CreateModel(
            name='UserReportResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_customers', models.IntegerField(default=0)),
                ('new_customers', models.IntegerField(default=0, help_text='New customers in the reporting period')),
                ('total_account_managers', models.IntegerField(default=0)),
                ('top_performing_managers', models.JSONField(blank=True, help_text='Top account managers by order value', null=True)),
                ('customers_with_orders', models.IntegerField(default=0, help_text='Customers who placed at least one order')),
                ('avg_orders_per_customer', models.FloatField(default=0.0)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stat_analysis.report')),
            ],
        ),
    ]
