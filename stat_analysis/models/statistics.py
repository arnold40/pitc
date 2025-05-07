"""stat_analysis.models.statistics.py

"""
from django.db import models

from .report import Report


class JobReportResult(models.Model):
    """Model to store analysis results for the Jobs.

    `Job` model is defined in `execution` app.
    """
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    total_jobs = models.IntegerField()

    # New fields
    avg_completion_time_regular = models.FloatField(null=True, blank=True)
    avg_completion_time_wafer_run = models.FloatField(null=True, blank=True)
    num_created = models.IntegerField(default=0)
    num_active = models.IntegerField(default=0)
    num_completed = models.IntegerField(default=0)


class OrderReportResult(models.Model):
    """Model to store analysis results for the customer Orders.

    Note: `Order` model should be defined in Task 1.
    """
    report = models.OneToOneField(Report, on_delete=models.CASCADE)

    # Example data fields of what the order report may contain.
    total_orders = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
