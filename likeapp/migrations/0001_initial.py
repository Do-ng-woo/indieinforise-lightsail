# Generated by Django 3.2.23 on 2024-09-04 15:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('singapp', '0001_initial'),
        ('instrumentapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('artistapp', '0001_initial'),
        ('genreapp', '0001_initial'),
        ('articleapp', '0001_initial'),
        ('projectapp', '0001_initial'),
        ('albumapp', '0001_initial'),
        ('communityapp', '0001_initial'),
        ('personapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingLikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sing_like_recode', to='singapp.sing')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sing_like_recode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'sing')},
            },
        ),
        migrations.CreateModel(
            name='ProjectLikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_like_recode', to='projectapp.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_like_recode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'project')},
            },
        ),
        migrations.CreateModel(
            name='PersonLikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person_like_recode', to='personapp.person')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person_like_recode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'person')},
            },
        ),
        migrations.CreateModel(
            name='LikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_recode', to='articleapp.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_recode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'article')},
            },
        ),
        migrations.CreateModel(
            name='InstrumentLikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instrument_like_recode', to='instrumentapp.instrument')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instrument_like_recode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'instrument')},
            },
        ),
        migrations.CreateModel(
            name='GenreLikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre_like_recode', to='genreapp.genre')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre_like_recode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'genre')},
            },
        ),
        migrations.CreateModel(
            name='CommunityLikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_record', to='communityapp.community')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_like_record', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'community')},
            },
        ),
        migrations.CreateModel(
            name='ArtistLikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artist_like_recode', to='artistapp.artist')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artist_like_recode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'artist')},
            },
        ),
        migrations.CreateModel(
            name='AlbumLikeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_like_recode', to='albumapp.album')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_like_recode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'album')},
            },
        ),
    ]
