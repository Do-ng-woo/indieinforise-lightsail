# Generated by Django 3.2.23 on 2024-09-04 15:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('articleapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audience_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='audiences/')),
            ],
        ),
        migrations.CreateModel(
            name='Background_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='backgrounds/')),
            ],
        ),
        migrations.CreateModel(
            name='Bassist_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='bassists/')),
            ],
        ),
        migrations.CreateModel(
            name='Drummer_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='drummers/')),
            ],
        ),
        migrations.CreateModel(
            name='Guitarist_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='guitarists/')),
            ],
        ),
        migrations.CreateModel(
            name='Keyboardist_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='keyboardists/')),
            ],
        ),
        migrations.CreateModel(
            name='Lighting_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='lightings/')),
            ],
        ),
        migrations.CreateModel(
            name='Singer_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='singers/')),
            ],
        ),
        migrations.CreateModel(
            name='Stamp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_text', models.TextField()),
                ('first_line', models.TextField()),
                ('second_line', models.TextField(blank=True, null=True)),
                ('third_line', models.TextField(blank=True, null=True)),
                ('date', models.DateField()),
                ('font_choice', models.IntegerField(choices=[(1, 'Font 1'), (2, 'Font 2'), (3, 'Font 3'), (4, 'Font 4'), (5, 'Font 5'), (6, 'Font 6')])),
                ('background_choice', models.IntegerField(choices=[(1, 'Background 1'), (2, 'Background 2'), (3, 'Background 3')])),
                ('center_image_choice', models.IntegerField(choices=[(1, 'Center Image 1'), (2, 'Center Image 2'), (3, 'Center Image 3'), (4, 'Center Image 4')])),
                ('color_choice', models.CharField(choices=[('blue', 'Blue'), ('yellow', 'Yellow'), ('red', 'Red'), ('black', 'Black')], max_length=10)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stamps', to='articleapp.article')),
            ],
        ),
        migrations.CreateModel(
            name='UserPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('W', 'Will Watch'), ('S', 'Saw'), ('L', 'Like')], max_length=1)),
                ('rating', models.PositiveIntegerField()),
                ('memo', models.TextField(blank=True, null=True)),
                ('running_time', models.IntegerField(blank=True, null=True)),
                ('stamp_image', models.ImageField(blank=True, null=True, upload_to='stamps/')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_performances', to='articleapp.article')),
                ('stamp', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myshowapp.stamp')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MyShow_illust',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('positions', models.TextField(blank=True, null=True)),
                ('sizes', models.TextField(blank=True, null=True)),
                ('z_indices', models.TextField(blank=True, null=True)),
                ('audience', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshowapp.audience_illust')),
                ('background', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshowapp.background_illust')),
                ('bassist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshowapp.bassist_illust')),
                ('drummer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshowapp.drummer_illust')),
                ('guitarist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshowapp.guitarist_illust')),
                ('keyboardist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshowapp.keyboardist_illust')),
                ('lighting', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshowapp.lighting_illust')),
                ('singer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshowapp.singer_illust')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='myshows', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
