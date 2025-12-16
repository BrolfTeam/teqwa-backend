# Generated manually for changing image field from CharField to TextField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0002_alter_donation_currency_alter_donationcause_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationcause',
            name='image',
            field=models.TextField(blank=True, help_text='Image URL, file path, or base64 data URL', null=True),
        ),
    ]
