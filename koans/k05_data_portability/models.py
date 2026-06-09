from django.db import models

class UserTransaction(models.Model):
    user_email = models.EmailField()
    item_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pdp_user_transactions'
