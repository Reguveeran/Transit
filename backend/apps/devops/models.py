from django.db import models
from django.utils import timezone


class Incident(models.Model):
    SEVERITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]
    STATUS_CHOICES = [
        ("INVESTIGATING", "Investigating"),
        ("IDENTIFIED", "Identified"),
        ("MITIGATING", "Mitigating"),
        ("RESOLVED", "Resolved"),
    ]

    incident_id = models.CharField(max_length=32, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES, default="HIGH")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="INVESTIGATING")
    affected_service = models.CharField(max_length=128)
    timeline = models.JSONField(default=list, help_text="List of timestamped incident events")
    postmortem = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "devops_incidents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.incident_id}: {self.title} [{self.status}]"


class ChaosExperiment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("RECOVERED", "Recovered"),
        ("FAILED", "Failed"),
    ]

    name = models.CharField(max_length=128)
    target_service = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PENDING")
    expected_behavior = models.CharField(max_length=255)
    actual_behavior = models.CharField(max_length=255, blank=True)
    recovery_time_seconds = models.FloatField(null=True, blank=True)
    logs = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "devops_chaos_experiments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} on {self.target_service} ({self.status})"


class FeatureFlag(models.Model):
    key = models.CharField(max_length=64, unique=True, db_index=True)
    display_name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True)
    is_enabled = models.BooleanField(default=True)
    category = models.CharField(max_length=64, default="general")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "devops_feature_flags"
        ordering = ["key"]

    def __str__(self):
        return f"{self.key}: {'ON' if self.is_enabled else 'OFF'}"
