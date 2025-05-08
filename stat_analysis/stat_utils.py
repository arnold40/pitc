import datetime

from django.apps import apps
from execution.models import Job
from django.db.models import Avg, Count
from decimal import Decimal
from core.models import Order, Customer, AccountManager


# Correct way to get a model dynamically
job_stats_model = apps.get_model("stat_analysis", "JobReportResult")
report_model = apps.get_model("stat_analysis", "Report")
order_stats_model = apps.get_model("stat_analysis", "OrderReportResult")
user_stats_model = apps.get_model("stat_analysis", "UserReportResult")


def calculate_job_stats(quarter_from, year_from, quarter_to, year_to, user=None):
    """Calculate statistics for Job model for a given period."""
    start_date_from, end_date_from = get_quarter_dates(quarter_from, year_from)
    start_date_to, end_date_to = get_quarter_dates(quarter_to, year_to)

    start_date = min(start_date_from, start_date_to)
    end_date = max(end_date_from, end_date_to)

    jobs_in_range = Job.objects.filter(starting_date__gte=start_date, end_date__lte=end_date)

    total_jobs = jobs_in_range.count()

    # Averages by job type
    avg_times = jobs_in_range.values('job_type').annotate(avg_time=Avg('completion_time'))
    avg_regular = next((item['avg_time'] for item in avg_times if item['job_type'] == 'regular'), None)
    avg_wafer_run = next((item['avg_time'] for item in avg_times if item['job_type'] == 'wafer_run'), None)

    # Status breakdown
    status_counts = jobs_in_range.values('state').annotate(count=Count('id'))
    state_map = {item['state']: item['count'] for item in status_counts}

    report, created = report_model.objects.get_or_create(
        quarter_from=quarter_from,
        year_from=year_from,
        quarter_to=quarter_to,
        year_to=year_to,
        defaults={
            'title': 'Job Report',
            'created_by': user,  # Replace with actual user in production
        }
    )

    job_stats, created = job_stats_model.objects.get_or_create(
        report=report,
        defaults={
            'total_jobs': total_jobs,
            'avg_completion_time_regular': avg_regular,
            'avg_completion_time_wafer_run': avg_wafer_run,
            'num_created': state_map.get('created', 0),
            'num_active': state_map.get('active', 0),
            'num_completed': state_map.get('completed', 0),
        }
    )

    if not created:
        job_stats.total_jobs = total_jobs
        job_stats.avg_completion_time_regular = avg_regular
        job_stats.avg_completion_time_wafer_run = avg_wafer_run
        job_stats.num_created = state_map.get('created', 0)
        job_stats.num_active = state_map.get('active', 0)
        job_stats.num_completed = state_map.get('completed', 0)
        job_stats.save()

    return job_stats


def calculate_order_stats(quarter_from, year_from, quarter_to, year_to, user=None):
    """Calculate statistics for Order model for a given period."""
    report_model = apps.get_model("stat_analysis", "Report")

    start_date_from, end_date_from = get_quarter_dates(quarter_from, year_from)
    start_date_to, end_date_to = get_quarter_dates(quarter_to, year_to)

    start_date = min(start_date_from, start_date_to)
    end_date = max(end_date_from, end_date_to)

    orders_in_range = Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).prefetch_related('services')

    total_orders = orders_in_range.count()

    # Calculate total revenue
    total_revenue = Decimal('0.00')
    for order in orders_in_range:
        total_revenue += sum(service.price for service in order.services.all())

    # Calculate average order value
    if total_orders > 0:
        average_order_value = total_revenue / total_orders
    else:
        average_order_value = Decimal('0.00')

    # Calculate orders per service provider
    provider_stats = {}
    for order in orders_in_range:
        providers = set(service.provider.name for service in order.services.all())
        for provider in providers:
            provider_stats[provider] = provider_stats.get(provider, 0) + 1

    # Calculate orders per account manager
    manager_stats = {}
    for order in orders_in_range:
        manager_name = order.account_manager.user.get_full_name() or order.account_manager.user.username
        manager_stats[manager_name] = manager_stats.get(manager_name, 0) + 1

    # Get or create the Report
    report, created = report_model.objects.get_or_create(
        quarter_from=quarter_from,
        year_from=year_from,
        quarter_to=quarter_to,
        year_to=year_to,
        defaults={
            'title': 'Order Report',
            'created_by': user,
        }
    )

    # Save stats
    order_stats, created = order_stats_model.objects.get_or_create(
        report=report,
        defaults={
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': average_order_value,
            'orders_per_service_provider': provider_stats,
            'orders_per_account_manager': manager_stats,
        }
    )

    if not created:
        order_stats.total_orders = total_orders
        order_stats.total_revenue = total_revenue
        order_stats.average_order_value = average_order_value
        order_stats.orders_per_service_provider = provider_stats
        order_stats.orders_per_account_manager = manager_stats
        order_stats.save()

    return order_stats


def calculate_user_stats(quarter_from, year_from, quarter_to, year_to, user=None):
    """Calculate statistics for Users (Customers and Account Managers) for a given period."""
    start_date_from, end_date_from = get_quarter_dates(quarter_from, year_from)
    start_date_to, end_date_to = get_quarter_dates(quarter_to, year_to)

    start_date = min(start_date_from, start_date_to)
    end_date = max(end_date_from, end_date_to)

    # Customer statistics
    total_customers = Customer.objects.count()
    new_customers = Customer.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).count() if hasattr(Customer, 'created_at') else 0

    # Orders in range
    orders_in_range = Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    )

    # Customers with orders
    customers_with_orders = orders_in_range.values('customer').distinct().count()

    # Avg orders per customer
    avg_orders = 0.0
    if customers_with_orders > 0:
        total_orders = orders_in_range.count()
        avg_orders = total_orders / customers_with_orders

    # Account manager statistics
    total_managers = AccountManager.objects.count()

    # Top performing managers by order value
    manager_performance = {}
    for order in orders_in_range.prefetch_related('services'):
        manager_name = order.account_manager.user.get_full_name() or order.account_manager.user.username
        order_value = sum(service.price for service in order.services.all())
        if manager_name in manager_performance:
            manager_performance[manager_name] += float(order_value)
        else:
            manager_performance[manager_name] = float(order_value)

    # Sort by value and get top 5
    top_managers = dict(sorted(manager_performance.items(), key=lambda x: x[1], reverse=True)[:5])

    # Get or create the Report
    report, created = report_model.objects.get_or_create(
        quarter_from=quarter_from,
        year_from=year_from,
        quarter_to=quarter_to,
        year_to=year_to,
        defaults={
            'title': 'Report',
            'created_by': user,
        }
    )

    # Save user stats
    user_stats, created = user_stats_model.objects.get_or_create(
        report=report,
        defaults={
            'total_customers': total_customers,
            'new_customers': new_customers,
            'total_account_managers': total_managers,
            'customers_with_orders': customers_with_orders,
            'avg_orders_per_customer': avg_orders,
            'top_performing_managers': top_managers,
        }
    )

    if not created:
        user_stats.total_customers = total_customers
        user_stats.new_customers = new_customers
        user_stats.total_account_managers = total_managers
        user_stats.customers_with_orders = customers_with_orders
        user_stats.avg_orders_per_customer = avg_orders
        user_stats.top_performing_managers = top_managers
        user_stats.save()

    return user_stats


def get_quarter_dates(quarter, year):
    if quarter == 'Q1':
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 3, 31)
    elif quarter == 'Q2':
        start_date = datetime.date(year, 4, 1)
        end_date = datetime.date(year, 6, 30)
    elif quarter == 'Q3':
        start_date = datetime.date(year, 7, 1)
        end_date = datetime.date(year, 9, 30)
    elif quarter == 'Q4':
        start_date = datetime.date(year, 10, 1)
        end_date = datetime.date(year, 12, 31)
    else:
        raise ValueError("Invalid quarter. Please use 'Q1', 'Q2', 'Q3', or 'Q4'.")
    return start_date, end_date
