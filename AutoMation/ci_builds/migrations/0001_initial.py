# Generated by Django 2.2.4 on 2020-04-01 13:03

import ckeditor.fields
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hitcount.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoProblemList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DiscoveryDate', models.DateField(default=datetime.date.today, verbose_name='问题提出日期')),
                ('Describe', ckeditor.fields.RichTextField(default='', max_length=1000, verbose_name='问题描述')),
                ('NE', models.CharField(choices=[('升级', '升级'), ('MDC', 'MDC'), ('UDC', 'UDC'), ('DC', 'DC')], default='MDC', max_length=10, verbose_name='网元')),
                ('SeverityLevel', models.CharField(choices=[('1', '一般'), ('2', '严重'), ('3', '致命')], default='1', max_length=1, verbose_name='严重程度')),
                ('Influence', models.CharField(default='', max_length=50, verbose_name='问题影响')),
                ('Responsible', models.CharField(default='', max_length=20, verbose_name='跟踪人员')),
                ('PositioningPerson', models.CharField(default='', max_length=20, verbose_name='定位人员/责任人')),
                ('Status', models.CharField(choices=[('1', '未定位'), ('2', '定位中'), ('3', '已定位'), ('4', '已解决')], default='1', max_length=20, verbose_name='当前状态')),
            ],
            options={
                'verbose_name': '自动化验证问题列表管理',
                'verbose_name_plural': '自动化验证问题列表管理',
            },
        ),
        migrations.CreateModel(
            name='AutoRes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField(default=datetime.date.today, verbose_name='日期')),
                ('VersionNum', models.CharField(default='', max_length=100, verbose_name='版本号')),
                ('VersionPath', models.CharField(max_length=100, unique=True, verbose_name='版本路径')),
                ('res', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1, verbose_name='验证结果')),
                ('options', models.CharField(choices=[('T', '是'), ('F', '否')], default='F', max_length=10, verbose_name='是否发送espace通知')),
            ],
            options={
                'verbose_name': '自动化验证日期及路径管理',
                'verbose_name_plural': '自动化验证日期及路径管理',
            },
        ),
        migrations.CreateModel(
            name='Bulletin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('body', ckeditor.fields.RichTextField(max_length=2000)),
                ('time', models.DateTimeField()),
            ],
            options={
                'verbose_name': '公告管理',
                'verbose_name_plural': '公告管理',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('svn', models.CharField(max_length=1000)),
                ('generating_path', models.CharField(max_length=1000)),
                ('sync_serv_ip', models.CharField(blank=True, max_length=100, null=True)),
                ('sync_proj_name', models.CharField(blank=True, max_length=100, null=True)),
                ('build_serv_ip', models.CharField(max_length=100)),
                ('build_proj_name', models.CharField(max_length=100)),
                ('witen_smoke_serv_ip', models.CharField(blank=True, max_length=100, null=True)),
                ('witen_smoke_proj_name', models.CharField(blank=True, max_length=100, null=True)),
                ('witen_smoke_agent_ip', models.CharField(blank=True, max_length=100, null=True)),
                ('btrunc_smoke_serv_ip', models.CharField(blank=True, max_length=100, null=True)),
                ('btrunc_smoke_proj_name', models.CharField(blank=True, max_length=100, null=True)),
                ('btrunc_smoke_agent_ip', models.CharField(blank=True, max_length=100, null=True)),
                ('tgpp_smoke_serv_ip', models.CharField(blank=True, max_length=100, null=True)),
                ('tgpp_smoke_proj_name', models.CharField(blank=True, max_length=100, null=True)),
                ('tgpp_smoke_agent_ip', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': '编译工程管理',
                'verbose_name_plural': '编译工程管理',
            },
            bases=(models.Model, hitcount.models.HitCountMixin),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=20)),
                ('version', models.CharField(max_length=50)),
                ('versionpath', models.CharField(max_length=100)),
                ('data1', models.CharField(max_length=20, null=True)),
                ('data2', models.CharField(max_length=20, null=True)),
                ('data3', models.CharField(max_length=20, null=True)),
                ('data4', models.CharField(max_length=20, null=True)),
                ('data5', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SmokeyResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='日期')),
                ('time', models.TimeField(auto_now_add=True, verbose_name='时间')),
                ('VersionNum', models.CharField(default='', max_length=100, verbose_name='版本号')),
                ('res', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1, verbose_name='冒烟结果')),
                ('describe', ckeditor.fields.RichTextField(blank=True, max_length=2000, null=True, verbose_name='问题现象及责任人')),
                ('MDC_Btrunc', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('MDC_Witen', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('MDC_3GPP', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('MDC_IM', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('MDC_UP', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('UDC_EBS', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('UDC_OTA', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('UDC_UTS', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('ISP', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('SDK', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('CID', models.CharField(choices=[('T', '通过'), ('F', '未通过')], default='T', max_length=1)),
                ('version_path', models.CharField(default='', max_length=200, verbose_name='版本路径')),
            ],
            options={
                'verbose_name': '冒烟结果管理',
                'verbose_name_plural': '冒烟结果管理',
            },
        ),
        migrations.CreateModel(
            name='SubRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('build_id', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='start time')),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('result', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='start time')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='end time')),
                ('duration', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('result', models.CharField(blank=True, choices=[('S', '成功'), ('F', '失败'), ('M', '强制停止')], default='F', max_length=1, null=True)),
                ('url', models.CharField(blank=True, default='', max_length=1000, null=True)),
                ('btrunc_smoke', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='btrunc', to='ci_builds.SubRecord')),
                ('build', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='build', to='ci_builds.SubRecord')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ci_builds.Project')),
                ('sync', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sync', to='ci_builds.SubRecord')),
                ('tgpp_smoke', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tgpp', to='ci_builds.SubRecord')),
                ('trigger', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('witen_smoke', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='witen', to='ci_builds.SubRecord')),
            ],
        ),
        migrations.CreateModel(
            name='AutoResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Time', models.TimeField(auto_now_add=True, verbose_name='时间')),
                ('VersionModel', models.CharField(choices=[('Witen', 'Witen'), ('Btrunc', 'Btrunc'), ('3GPP', '3GPP'), ('Witen-Btrunc-3GPP', 'Witen-Btrunc-3GPP')], default='Witen', max_length=20, verbose_name='版本制式')),
                ('NE', models.CharField(choices=[('升级', '升级'), ('MDC', 'MDC'), ('UDC', 'UDC'), ('DC', 'DC')], default='MDC', max_length=10, verbose_name='网元')),
                ('Responsible', models.CharField(default='', max_length=20, verbose_name='自动化测试线负责人')),
                ('Result', models.CharField(choices=[('G', '▲'), ('Y', '●'), ('R', '■')], default='G', max_length=1, verbose_name='验证结果')),
                ('Describe', ckeditor.fields.RichTextField(blank=True, max_length=2000, null=True, verbose_name='故障原因分析')),
                ('VersionPath', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ci_builds.AutoRes', to_field='VersionPath', verbose_name='版本路径')),
            ],
            options={
                'verbose_name': '自动化验证结果',
                'verbose_name_plural': '自动化验证结果',
            },
        ),
    ]
