from django.db import models

class ActionAuditLog(models.Model):
    operator_email = models.EmailField()
    action_details = models.TextField()
    timestamp = models.DateTimeField()  # Allows manual backdating in tests

    class Meta:
        db_table = 'pdp_action_audit_logs'
