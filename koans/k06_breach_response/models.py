from django.db import models

class IncidentReport(models.Model):
    root_cause = models.CharField(max_length=255)
    impacted_subjects_count = models.IntegerField()
    remediation_actions = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reported_to_bppa = models.BooleanField(default=False)

    class Meta:
        db_table = 'pdp_incident_reports'
