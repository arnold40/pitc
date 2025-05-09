from django.contrib import admin
from .models import Customer, AccountManager, ServiceProvider, Service, Order


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    list_filter = ('created_by',)
    search_fields = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'created_by':
            kwargs["queryset"] = AccountManager.objects.all().select_related('user')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AccountManager)
class AccountManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name')
    filter_horizontal = ('service_providers',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = 'Name'


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'price')
    list_filter = ('provider',)
    search_fields = ('name', 'description')


class ServiceInline(admin.TabularInline):
    model = Order.services.through
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'account_manager', 'created_at', 'get_total_price')
    list_filter = ('account_manager', 'created_at')
    search_fields = ('customer__name',)
    date_hierarchy = 'created_at'
    exclude = ('services',)
    inlines = [ServiceInline]

    def get_total_price(self, obj):
        return sum(service.price for service in obj.services.all())

    get_total_price.short_description = 'Total Price'