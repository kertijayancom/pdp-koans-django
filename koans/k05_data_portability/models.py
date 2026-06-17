from django.db import models

class UserTransaction(models.Model):
    user_email = models.EmailField()
    item_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pdp_user_transactions'


class DataExportJob(models.Model):
    user_email = models.EmailField()
    status = models.CharField(max_length=20, default='PENDING')  # PENDING, COMPLETED, FAILED
    download_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pdp_data_export_jobs'
