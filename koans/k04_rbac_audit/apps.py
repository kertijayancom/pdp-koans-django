from django.apps import AppConfig


class RbacAuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'koans.k04_rbac_audit'
    label = 'rbac_audit'
