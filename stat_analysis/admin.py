from django.contrib import admin
from .models import Report, JobReportResult, OrderReportResult, UserReportResult


class JobReportResultInline(admin.StackedInline):
    model = JobReportResult
    can_delete = False
    verbose_name_plural = 'Job Statistics'


class OrderReportResultInline(admin.StackedInline):
    model = OrderReportResult
    can_delete = False
    verbose_name_plural = 'Order Statistics'


class UserReportResultInline(admin.StackedInline):
    model = UserReportResult
    can_delete = False
    verbose_name_plural = 'User Statistics'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'created_by', 'date_range', 'has_pdf')
    list_filter = ('quarter_from', 'year_from', 'created_by')
    search_fields = ('title',)
    date_hierarchy = 'created_at'
    inlines = [JobReportResultInline, OrderReportResultInline, UserReportResultInline]

    def date_range(self, obj):
        return f"{obj.quarter_from}/{obj.year_from} - {obj.quarter_to}/{obj.year_to}"

    date_range.short_description = 'Period'

    def has_pdf(self, obj):
        return bool(obj.pdf_report)

    has_pdf.boolean = True
    has_pdf.short_description = 'PDF Attached'


@admin.register(JobReportResult)
class JobReportResultAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_jobs', 'num_created', 'num_active', 'num_completed')
    list_filter = ('report__quarter_from', 'report__year_from')
    search_fields = ('report__title',)


@admin.register(OrderReportResult)
class OrderReportResultAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_orders', 'total_revenue', 'average_order_value')
    list_filter = ('report__quarter_from', 'report__year_from')
    search_fields = ('report__title',)


@admin.register(UserReportResult)
class UserReportResultAdmin(admin.ModelAdmin):
    list_display = ('report', 'total_customers', 'new_customers', 'total_account_managers', 'customers_with_orders')
    list_filter = ('report__quarter_from', 'report__year_from')
    search_fields = ('report__title',)