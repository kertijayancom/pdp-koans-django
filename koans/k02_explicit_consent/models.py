from django.db import models

class ConsentLog(models.Model):
    user_email = models.EmailField()
    consent_given = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    policy_version = models.CharField(max_length=10)

    class Meta:
        db_table = 'pdp_consent_logs'
