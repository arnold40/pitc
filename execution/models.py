"""execution.models.py

This script defines the Job model which is used to track
the execution progress of customer orders.
"""
from django.db import models


class Job(models.Model):

    JOB_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('wafer_run', 'Wafer Run'),
    ]
    STATE_CHOICES = [
        ('created', 'Created'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    job_id = models.CharField(max_length=10, unique=True)
    job_name = models.CharField(max_length=200)

    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)

    starting_date = models.DateTimeField()
    end_date = models.DateTimeField()
    completion_time = models.FloatField(help_text="Time in days which were spent to complete the job.")

    def __str__(self):
        return self.job_name
