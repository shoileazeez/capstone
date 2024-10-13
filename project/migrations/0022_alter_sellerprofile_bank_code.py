# Generated by Django 5.1.1 on 2024-10-12 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0021_transaction_buyer_email_transaction_platform_fee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sellerprofile',
            name='bank_code',
            field=models.CharField(blank=True, choices=[('011', 'First Bank of Nigeria'), ('404', 'Abbey Mortgage Bank'), ('044', 'Access Bank'), ('058', 'Guaranty Trust Bank'), ('215', 'Unity Bank'), ('221', 'Stanbic IBTC Bank'), ('232', 'Sterling Bank'), ('033', 'United Bank for Africa'), ('035', 'Wema Bank'), ('082', 'Keystone Bank'), ('101', 'Providus Bank'), ('102', 'Suntrust Bank'), ('103', 'Titan Trust Bank'), ('232', 'Sterling Bank'), ('999992', 'Opay'), ('50211', 'Kuda Bank'), ('100002', 'Paga'), ('076', 'Polaris Bank'), ('104', 'parallex Bank'), ('50515', 'Moniepoint MFB'), ('214', 'First City Monument Bank'), ('999991', 'PalmPay'), ('033', 'CitiBank Nigeria'), ('059', 'JPMorgan Chase Bank'), ('070', 'Fidelity Bank'), ('057', 'Zenith Bank'), ('068', 'Standard Chartered Bank'), ('301', 'Jaiz Bank')], max_length=10, null=True),
        ),
    ]
