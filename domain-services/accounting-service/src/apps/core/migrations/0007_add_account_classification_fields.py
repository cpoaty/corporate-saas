# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_account_ohada_classification'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='ref_financial_statement',
            field=models.CharField(blank=True, help_text='Référence pour les états financiers (ex: AE, BJ, TA)', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='is_amortization_depreciation',
            field=models.BooleanField(default=False, help_text="Indique si le compte est un compte d'amortissement ou de dépréciation"),
        ),
        migrations.AddField(
            model_name='account',
            name='normal_balance',
            field=models.CharField(blank=True, help_text='Solde normal du compte (DEBIT ou CREDIT)', max_length=10, null=True),
        ),
    ]