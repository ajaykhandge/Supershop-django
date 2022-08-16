# Generated by Django 3.0 on 2022-08-10 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20220208_1558'),
        ('orders', '0002_auto_20220810_0624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='variation',
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='variations',
            field=models.ManyToManyField(blank=True, to='store.Variation'),
        ),
    ]