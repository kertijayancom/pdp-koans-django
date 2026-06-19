from django.db import models

class DeletionRequest(models.Model):
    user_email = models.EmailField()
    status = models.CharField(max_length=20, default='PENDING')  # PENDING, COMPLETED
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pdp_deletion_requests'
