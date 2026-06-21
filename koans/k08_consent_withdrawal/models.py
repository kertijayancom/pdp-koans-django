from django.db import models

class RevokedToken(models.Model):
    user_email = models.EmailField()
    token_jti = models.CharField(max_length=255, unique=True)
    revoked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pdp_revoked_tokens'
