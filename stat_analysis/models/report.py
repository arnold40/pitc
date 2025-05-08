"""stat_analysis.models.report.py

"""
from django.db import models
from django.contrib.auth.models import User


class Report(models.Model):
    # metadata
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Report settings 
    quarter_from = models.CharField(max_length=2)  # Q1, Q2, Q3, Q4
    year_from = models.IntegerField()
    quarter_to = models.CharField(max_length=2)  # Q1, Q2, Q3, Q4
    year_to = models.IntegerField()

    # PDF report attachment
    pdf_report = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.quarter_from}/{self.year_from} - {self.quarter_to}/{self.year_to})"

    def save(self, *args, **kwargs):
        """Override save to trigger statistics calculation on creation/update"""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Import here to avoid circular import
        from stat_analysis.stat_utils import calculate_job_stats, calculate_order_stats, calculate_user_stats

        # Calculate statistics for this report
        calculate_job_stats(self.quarter_from, self.year_from, self.quarter_to, self.year_to, self.created_by)
        calculate_order_stats(self.quarter_from, self.year_from, self.quarter_to, self.year_to, self.created_by)
        calculate_user_stats(self.quarter_from, self.year_from, self.quarter_to, self.year_to, self.created_by)