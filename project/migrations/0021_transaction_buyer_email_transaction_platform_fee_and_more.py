# Generated by Django 5.1.1 on 2024-10-07 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0020_alter_sellerprofile_bank_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='buyer_email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='platform_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='transaction',
            name='seller_share',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
