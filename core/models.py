from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from execution.models import Job


class Customer(models.Model):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        'AccountManager',
        on_delete=models.SET_NULL,
        null=True,
        related_name='customers'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class AccountManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    service_providers = models.ManyToManyField('ServiceProvider', related_name='account_managers')

    def __str__(self):
        name = self.user.get_full_name()
        if name:
            return f"{name} ({self.user.username})"
        return self.user.username


class ServiceProvider(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.provider.name})"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_manager = models.ForeignKey(AccountManager, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    # Services in this order
    services = models.ManyToManyField(Service, related_name='orders')

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    def __str__(self):
        return f"Order #{self.id} by {self.customer.name}"

    def clean(self):
        # Custom validation: all services must be from providers managed by this order's account manager
        from django.core.exceptions import ValidationError

        if not self.pk or not self.account_manager_id:
            return  # Skip validation on unsaved instance

        allowed_providers = set(self.account_manager.service_providers.values_list('id', flat=True))
        for service in self.services.all():
            if service.provider_id not in allowed_providers:
                raise ValidationError(f"Service '{service.name}' from provider '{service.provider.name}' is not allowed.")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(account_manager=None),
                name="order_requires_account_manager"
            )
        ]
        permissions = [
            ("view_own_orders", "Can view orders managed by the account manager"),
        ]