from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('breach_response', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompromisedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email', models.EmailField(max_length=254, unique=True)),
                ('is_compromised', models.BooleanField(default=True)),
                ('detected_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'pdp_compromised_users',
            },
        ),
    ]
