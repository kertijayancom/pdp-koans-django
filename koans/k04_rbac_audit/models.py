from django.db import models

class AccessAuditLog(models.Model):
    operator_email = models.EmailField()
    action = models.CharField(max_length=100)
    accessed_user_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pdp_access_audit_logs'
