import datetime
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from execution.models import Job
from stat_analysis.models.report import Report
from stat_analysis.stat_utils import calculate_job_stats, calculate_order_stats, calculate_user_stats
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

        self.assertIn('Provider 1', result.orders_per_service_provider)
        self.assertEqual(result.orders_per_service_provider['Provider 1'], 2)

        manager_name = self.user.get_full_name() or self.user.username
        self.assertIn(manager_name, result.orders_per_account_manager)
        self.assertEqual(result.orders_per_account_manager[manager_name], 2)

        # Report object should exist
        self.assertIsInstance(result.report, Report)


class CalculateUserStatsTest(TestCase):
    def setUp(self):
        # Create account managers
        self.user1 = User.objects.create(username="manager1", first_name="John", last_name="Doe")
        self.manager1 = AccountManager.objects.create(user=self.user1)

        self.user2 = User.objects.create(username="manager2", first_name="Jane", last_name="Smith")
        self.manager2 = AccountManager.objects.create(user=self.user2)

        # Create customers
        self.customer1 = Customer.objects.create(name="Customer 1", created_by=self.manager1)
        self.customer2 = Customer.objects.create(name="Customer 2", created_by=self.manager1)

        # Create service providers and services
        provider1 = ServiceProvider.objects.create(name="Provider 1")
        provider2 = ServiceProvider.objects.create(name="Provider 2")

        self.manager1.service_providers.add(provider1)
        self.manager2.service_providers.add(provider2)

        self.service1 = Service.objects.create(name="Service 1", price=Decimal('100.00'), provider=provider1)
        self.service2 = Service.objects.create(name="Service 2", price=Decimal('200.00'), provider=provider2)

        # Create orders
        base_date = datetime.datetime(2024, 1, 15, tzinfo=datetime.timezone.utc)

        # Orders for customer 1 with manager 1
        order1 = Order.objects.create(
            customer=self.customer1,
            account_manager=self.manager1,
            created_at=base_date
        )
        order1.services.add(self.service1)

        # Orders for customer 2 with manager 2
        order2 = Order.objects.create(
            customer=self.customer2,
            account_manager=self.manager2,
            created_at=base_date
        )
        order2.services.add(self.service2)

    def test_user_statistics_are_calculated_correctly(self):
        result = calculate_user_stats("Q1", 2024, "Q1", 2024)

        self.assertEqual(result.total_customers, 2)
        self.assertEqual(result.total_account_managers, 2)
        self.assertEqual(result.customers_with_orders, 2)
        self.assertEqual(result.avg_orders_per_customer, 1.0)  # 2 orders / 2 customers

        # Test top performing managers
        top_managers = result.top_performing_managers
        self.assertIn('Jane Smith', top_managers)
        self.assertIn('John Doe', top_managers)

        # Jane should be top (200) vs John (100)
        top_manager = list(top_managers.keys())[0]
        self.assertEqual(top_manager, 'Jane Smith')

        # Report should exist
        self.assertIsInstance(result.report, Report)


class ReportPDFTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(username="testuser")

        # Create a sample PDF file
        self.pdf_content = b'%PDF-1.4 test pdf content'
        self.pdf_file = SimpleUploadedFile('report.pdf', self.pdf_content, content_type='application/pdf')

    def test_report_pdf_attachment(self):
        """Test that a PDF can be attached to a report"""
        report = Report.objects.create(
            title="Test Report with PDF",
            quarter_from="Q1",
            year_from=2024,
            quarter_to="Q1",
            year_to=2024,
            created_by=self.user,
            pdf_report=self.pdf_file
        )

        # Refresh from DB
        report.refresh_from_db()

        # Check the file is attached
        self.assertTrue(report.pdf_report)
        self.assertTrue(report.pdf_report.name.endswith('.pdf'))