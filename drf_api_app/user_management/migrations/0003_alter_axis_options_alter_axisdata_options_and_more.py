# Generated by Django 5.1.1 on 2024-09-28 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_alter_axis_table_alter_axisdata_table_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='axis',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='axisdata',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='machine',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='tool',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='toolusage',
            options={'managed': False},
        ),
    ]
