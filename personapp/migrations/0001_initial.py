# Generated by Django 3.2.23 on 2024-09-04 15:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('instrumentapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('image', models.ImageField(upload_to='person/')),
                ('description', models.CharField(max_length=200, null=True)),
                ('like', models.IntegerField(default=0)),
                ('views', models.IntegerField(default=0)),
                ('comment_count', models.IntegerField(default=0)),
                ('created_at', models.DateField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('hide', models.BooleanField(default=True)),
                ('instruments', models.ManyToManyField(blank=True, related_name='persons', to='instrumentapp.Instrument')),
            ],
        ),
        migrations.CreateModel(
            name='Subtitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PersonUpdateLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('update_description', models.TextField(blank=True, null=True)),
                ('hide', models.BooleanField(default=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='update_logs', to='personapp.person')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='sub_titles',
            field=models.ManyToManyField(blank=True, related_name='persons', to='personapp.Subtitle'),
        ),
        migrations.AddField(
            model_name='person',
            name='writer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='정보', max_length=100)),
                ('text', models.TextField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detailed_descriptions', to='personapp.person')),
            ],
        ),
    ]
