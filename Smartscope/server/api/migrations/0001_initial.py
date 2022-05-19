# Generated by Django 3.1.7 on 2022-05-19 14:31

import Smartscope.core.models.session
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    replaces = [('API', '0001_initial'), ('API', '0002_microscope_scope_path'), ('API', '0003_detector_c2_perc')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='GridCollectionParams',
            fields=[
                ('params_id', models.CharField(editable=False, max_length=30, primary_key=True, serialize=False)),
                ('atlas_x', models.IntegerField(default=3)),
                ('atlas_y', models.IntegerField(default=3)),
                ('square_x', models.IntegerField(default=1)),
                ('square_y', models.IntegerField(default=1)),
                ('squares_num', models.IntegerField(default=3)),
                ('holes_per_square', models.IntegerField(default=3)),
                ('bis_max_distance', models.FloatField(default=0)),
                ('min_bis_group_size', models.IntegerField(default=1)),
                ('target_defocus_min', models.FloatField(default=-2)),
                ('target_defocus_max', models.FloatField(default=-2)),
                ('step_defocus', models.FloatField(default=0)),
                ('drift_crit', models.FloatField(default=-1)),
                ('tilt_angle', models.FloatField(default=0)),
                ('save_frames', models.BooleanField(default=True)),
                ('zeroloss_delay', models.IntegerField(default=-1)),
            ],
            options={
                'db_table': 'gridcollectionparams',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HoleType',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('hole_size', models.FloatField(blank=True, default=None, null=True)),
                ('hole_spacing', models.FloatField(blank=True, default=None, null=True)),
            ],
            options={
                'db_table': 'holetype',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MeshMaterial',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'meshmaterial',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MeshSize',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('square_size', models.IntegerField()),
                ('bar_width', models.IntegerField()),
                ('pitch', models.IntegerField()),
            ],
            options={
                'db_table': 'meshsize',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SquareModel',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('number', models.IntegerField()),
                ('pixel_size', models.FloatField(null=True)),
                ('shape_x', models.IntegerField(null=True)),
                ('shape_y', models.IntegerField(null=True)),
                ('selected', models.BooleanField(default=False)),
                ('status', models.CharField(default=None, max_length=20, null=True)),
                ('completion_time', models.DateTimeField(null=True)),
                ('square_id', models.CharField(editable=False, max_length=30, primary_key=True, serialize=False)),
                ('area', models.FloatField(null=True)),
                ('atlas_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.atlasmodel')),
                ('grid_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.autoloadergrid')),
            ],
            options={
                'db_table': 'squaremodel',
                'abstract': False,
                'unique_together': {('name', 'atlas_id')},
            },
            bases=(models.Model, Smartscope.core.models.session.ExtraPropertyMixin),
            managers=[
                ('withholes', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Selector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=30)),
                ('method_name', models.CharField(max_length=50, null=True)),
                ('label', models.CharField(max_length=30, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'db_table': 'selector',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScreeningSession',
            fields=[
                ('session', models.CharField(max_length=30)),
                ('date', models.CharField(editable=False, max_length=8)),
                ('version', models.CharField(editable=False, max_length=8)),
                ('working_dir', models.CharField(editable=False, max_length=300)),
                ('session_id', models.CharField(editable=False, max_length=30, primary_key=True, serialize=False)),
                ('detector_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.detector')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.group', to_field='name')),
                ('microscope_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.microscope')),
            ],
            options={
                'db_table': 'screeningsession',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PID', models.IntegerField()),
                ('start_time', models.DateTimeField(auto_now=True)),
                ('end_time', models.DateTimeField(default=None, null=True)),
                ('status', models.CharField(max_length=10)),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.screeningsession')),
            ],
            options={
                'db_table': 'process',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HoleModel',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('number', models.IntegerField()),
                ('pixel_size', models.FloatField(null=True)),
                ('shape_x', models.IntegerField(null=True)),
                ('shape_y', models.IntegerField(null=True)),
                ('selected', models.BooleanField(default=False)),
                ('status', models.CharField(default=None, max_length=20, null=True)),
                ('completion_time', models.DateTimeField(null=True)),
                ('hole_id', models.CharField(editable=False, max_length=30, primary_key=True, serialize=False)),
                ('dist_from_center', models.FloatField(null=True)),
                ('radius', models.IntegerField()),
                ('area', models.FloatField()),
                ('bis_group', models.CharField(max_length=30, null=True)),
                ('bis_type', models.CharField(max_length=30, null=True)),
                ('grid_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.autoloadergrid')),
                ('square_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.squaremodel')),
            ],
            options={
                'db_table': 'holemodel',
                'abstract': False,
                'unique_together': {('name', 'square_id')},
            },
            bases=(models.Model, Smartscope.core.models.session.ExtraPropertyMixin),
        ),
        migrations.CreateModel(
            name='HighMagModel',
            fields=[
                ('hm_id', models.CharField(editable=False, max_length=30, primary_key=True, serialize=False)),
                ('number', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('pixel_size', models.FloatField(null=True)),
                ('status', models.CharField(default=None, max_length=20, null=True)),
                ('is_x', models.FloatField(null=True)),
                ('is_y', models.FloatField(null=True)),
                ('frames', models.CharField(default=None, max_length=120, null=True)),
                ('defocus', models.FloatField(null=True)),
                ('astig', models.FloatField(null=True)),
                ('angast', models.FloatField(null=True)),
                ('ctffit', models.FloatField(null=True)),
                ('grid_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.autoloadergrid')),
                ('hole_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.holemodel')),
            ],
            options={
                'db_table': 'highmagmodel',
                'abstract': False,
            },
            bases=(models.Model, Smartscope.core.models.session.ExtraPropertyMixin),
        ),
        migrations.CreateModel(
            name='Finder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=30)),
                ('method_name', models.CharField(max_length=50, null=True)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('stage_x', models.FloatField()),
                ('stage_y', models.FloatField()),
                ('stage_z', models.FloatField(null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'db_table': 'finder',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Classifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=30)),
                ('method_name', models.CharField(max_length=50, null=True)),
                ('label', models.CharField(max_length=30, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'db_table': 'classifier',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.CharField(max_length=60)),
                ('line_id', models.CharField(max_length=30)),
                ('column_name', models.CharField(max_length=20)),
                ('initial_value', models.BinaryField()),
                ('new_value', models.BinaryField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('grid_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.autoloadergrid')),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'db_table': 'changelog',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AutoloaderGrid',
            fields=[
                ('position', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('grid_id', models.CharField(editable=False, max_length=30, primary_key=True, serialize=False)),
                ('hole_angle', models.FloatField(null=True)),
                ('mesh_angle', models.FloatField(null=True)),
                ('quality', models.CharField(default=None, max_length=10, null=True)),
                ('notes', models.CharField(default=None, max_length=10000, null=True)),
                ('status', models.CharField(default=None, max_length=10, null=True)),
                ('start_time', models.DateTimeField(default=None, null=True)),
                ('last_update', models.DateTimeField(default=None, null=True)),
                ('holeType', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.holetype')),
                ('meshMaterial', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.meshmaterial')),
                ('meshSize', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.meshsize')),
                ('params_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.gridcollectionparams')),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.screeningsession')),
            ],
            options={
                'db_table': 'autoloadergrid',
                'abstract': False,
                'unique_together': {('position', 'name', 'session_id')},
            },
        ),
        migrations.CreateModel(
            name='AtlasModel',
            fields=[
                ('atlas_id', models.CharField(editable=False, max_length=30, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('pixel_size', models.FloatField(null=True)),
                ('binning_factor', models.FloatField(null=True)),
                ('shape_x', models.IntegerField(null=True)),
                ('shape_y', models.IntegerField(null=True)),
                ('stage_z', models.FloatField(null=True)),
                ('status', models.CharField(default=None, max_length=20, null=True)),
                ('completion_time', models.DateTimeField(null=True)),
                ('grid_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.autoloadergrid')),
            ],
            options={
                'db_table': 'atlasmodel',
                'abstract': False,
                'unique_together': {('grid_id', 'name')},
            },
            bases=(models.Model, Smartscope.core.models.session.ExtraPropertyMixin),
        ),
        migrations.CreateModel(
            name='Microscope',
            fields=[
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=30)),
                ('voltage', models.IntegerField(default=200)),
                ('spherical_abberation', models.FloatField(default=2.7)),
                ('microscope_id', models.CharField(editable=False, max_length=30, primary_key=True, serialize=False)),
                ('loader_size', models.CharField(max_length=30)),
                ('worker_hostname', models.CharField(default='localhost', max_length=30)),
                ('executable', models.CharField(default='smartscope.py', max_length=30)),
                ('serialem_IP', models.CharField(default='xxx.xxx.xxx.xxx', max_length=30)),
                ('serialem_PORT', models.IntegerField(default=48888)),
                ('windows_path', models.CharField(default='X:\\\\auto_screening\\', max_length=200)),
                ('scope_path', models.CharField(default='/mnt/scope', max_length=200)),
            ],
            options={
                'db_table': 'microscope',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Detector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('detector_model', models.CharField(choices=[('K2', 'Gatan K2'), ('K3', 'Gatan K3'), ('Ceta', 'FEI Ceta'), ('Falcon3', 'TFS Falcon 3'), ('Falcon4', 'TFS Falcon 4')], max_length=30)),
                ('atlas_mag', models.IntegerField(default=210)),
                ('atlas_max_tiles_X', models.IntegerField(default=6)),
                ('atlas_max_tiles_Y', models.IntegerField(default=6)),
                ('spot_size', models.IntegerField(default=None, null=True)),
                ('frame_align_cmd', models.CharField(default='alignframes', max_length=30)),
                ('gain_rot', models.IntegerField(default=0, null=True)),
                ('gain_flip', models.BooleanField(default=True)),
                ('energy_filter', models.BooleanField(default=False)),
                ('microscope_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.microscope')),
                ('c2_perc', models.FloatField(default=100)),
            ],
            options={
                'db_table': 'detector',
                'abstract': False,
            },
        ),
    ]
