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

    orders_per_service_provider = models.JSONField(null=True, blank=True,
                                                   help_text="Distribution of orders across service providers")
    orders_per_account_manager = models.JSONField(null=True, blank=True,
                                                  help_text="Distribution of orders across account managers")


class UserReportResult(models.Model):
    """Model to store analysis results for Users (Customers and Account Managers).

    This provides insights into user activity and performance.
    """
    report = models.OneToOneField(Report, on_delete=models.CASCADE)

    # Customer statistics
    total_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0, help_text="New customers in the reporting period")

    # Account manager statistics
    total_account_managers = models.IntegerField(default=0)
    top_performing_managers = models.JSONField(null=True, blank=True,
                                               help_text="Top account managers by order value")

    # Activity metrics
    customers_with_orders = models.IntegerField(default=0,
                                                help_text="Customers who placed at least one order")
    avg_orders_per_customer = models.FloatField(default=0.0)