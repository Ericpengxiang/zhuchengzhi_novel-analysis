# Generated migration: add missing fields to novel_detail table
# Fields: continuous_days, urge_tickets, reward, monthly_tickets, share_count

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='noveldetail',
            name='continuous_days',
            field=models.IntegerField(default=0, verbose_name='连更天数'),
        ),
        migrations.AddField(
            model_name='noveldetail',
            name='urge_tickets',
            field=models.IntegerField(default=0, verbose_name='催更票'),
        ),
        migrations.AddField(
            model_name='noveldetail',
            name='reward',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='打赏（元）'),
        ),
        migrations.AddField(
            model_name='noveldetail',
            name='monthly_tickets',
            field=models.IntegerField(default=0, verbose_name='月票'),
        ),
        migrations.AddField(
            model_name='noveldetail',
            name='share_count',
            field=models.IntegerField(default=0, verbose_name='分享人数'),
        ),
    ]
