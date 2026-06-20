from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GranularMarketingConsent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email', models.EmailField(max_length=254)),
                ('category', models.CharField(max_length=50)),
                ('consent_given', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'pdp_granular_marketing_consents',
                'unique_together': {('user_email', 'category')},
            },
        ),
    ]
