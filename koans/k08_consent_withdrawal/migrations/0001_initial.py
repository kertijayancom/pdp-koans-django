from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RevokedToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email', models.EmailField(max_length=254)),
                ('token_jti', models.CharField(max_length=255, unique=True)),
                ('revoked_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'pdp_revoked_tokens',
            },
        ),
    ]
