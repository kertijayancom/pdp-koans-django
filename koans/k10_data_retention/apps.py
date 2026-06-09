from django.apps import AppConfig

class DataRetentionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'koans.k10_data_retention'
    label = 'data_retention'
