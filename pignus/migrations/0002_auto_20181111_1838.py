# Generated by Django 2.1.3 on 2018-11-11 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pignus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='xgboostmodel',
            name='file_path',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='login',
            field=models.CharField(max_length=100),
        ),
    ]
