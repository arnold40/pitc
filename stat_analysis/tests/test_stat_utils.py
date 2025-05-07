import datetime
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from execution.models import Job
from stat_analysis.models.statistics import JobReportResult
from stat_analysis.models.report import Report
from stat_analysis.stat_utils import calculate_job_stats, calculate_order_stats
from core.models import Order, Customer, AccountManager, ServiceProvider, Service


class CalculateJobStatsTest(TestCase):
    def setUp(self):
        # Create jobs in different states and types
        base_date = datetime.datetime(2024, 1, 15, tzinfo=datetime.timezone.utc)

        Job.objects.create(
            job_id="J1", job_name="Job 1", state="created", job_type="regular",
            starting_date=base_date, end_date=base_date + datetime.timedelta(days=2),
            completion_time=2
        )
        Job.objects.create(
            job_id="J2", job_name="Job 2", state="completed", job_type="regular",
            starting_date=base_date, end_date=base_date + datetime.timedelta(days=4),
            completion_time=4
        )
        Job.objects.create(
            job_id="J3", job_name="Job 3", state="active", job_type="wafer_run",
            starting_date=base_date, end_date=base_date + datetime.timedelta(days=6),
            completion_time=6
        )

    def test_job_statistics_are_calculated_correctly(self):
        result = calculate_job_stats("Q1", 2024, "Q1", 2024)

        self.assertEqual(result.total_jobs, 3)
        self.assertAlmostEqual(result.avg_completion_time_regular, 3.0)  # (2 + 4) / 2
        self.assertAlmostEqual(result.avg_completion_time_wafer_run, 6.0)
        self.assertEqual(result.num_created, 1)
        self.assertEqual(result.num_active, 1)
        self.assertEqual(result.num_completed, 1)

        # Report should exist and be linked
        self.assertIsInstance(result.report, Report)

class CalculateOrderStatsTest(TestCase):
    def setUp(self):
        # Create an Account Manager
        self.user = User.objects.create(username="manager1")
        self.manager = AccountManager.objects.create(user=self.user)

        # Create a Customer
        self.customer = Customer.objects.create(name="Test Customer", created_by=self.manager)

        # Create a Service Provider and Services
        provider = ServiceProvider.objects.create(name="Provider 1")
        self.manager.service_providers.add(provider)

        self.service1 = Service.objects.create(name="Service 1", price=Decimal('100.00'), provider=provider)
        self.service2 = Service.objects.create(name="Service 2", price=Decimal('200.00'), provider=provider)

        # Create Orders
        base_date = datetime.datetime(2024, 1, 15, tzinfo=datetime.timezone.utc)
        order1 = Order.objects.create(
            customer=self.customer,
            account_manager=self.manager,
            created_at=base_date
        )
        order1.services.add(self.service1)

        order2 = Order.objects.create(
            customer=self.customer,
            account_manager=self.manager,
            created_at=base_date
        )
        order2.services.add(self.service1, self.service2)

    def test_order_statistics_are_calculated_correctly(self):
        result = calculate_order_stats("Q1", 2024, "Q1", 2024)

        self.assertEqual(result.total_orders, 2)
        self.assertEqual(result.total_revenue, Decimal('400.00'))  # 100 + (100+200)
        self.assertEqual(result.average_order_value, Decimal('200.00'))  # 400 / 2

        # Report object should exist
        self.assertIsInstance(result.report, Report)