# Generated manually for adding donation_cause field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0001_initial'),
        ('donations', '0002_alter_donation_currency_alter_donationcause_currency'),  # Latest donations migration
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='donation_cause',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional: Link this announcement to a donation cause for fundraising',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='announcements',
                to='donations.donationcause'
            ),
        ),
    ]
