from django.db import models

class GranularMarketingConsent(models.Model):
    user_email = models.EmailField()
    category = models.CharField(max_length=50)  # e.g., 'weekly_newsletter', 'product_promo'
    consent_given = models.BooleanField(default=False)

    class Meta:
        db_table = 'pdp_granular_marketing_consents'
        unique_together = ('user_email', 'category')
