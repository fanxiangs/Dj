from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from hitcount.models import HitCountMixin
from ckeditor.fields import RichTextField
from datetime import date

# from config import smoke_receiver,auto_receiver
# from eSpaceAPI.send_eSpace import send_espace


class Bulletin(models.Model):
    title = models.CharField(max_length=200)
    body = RichTextField(max_length=2000)
    time = models.DateTimeField()

    class Meta:
        verbose_name = "公告管理"
        verbose_name_plural = "公告管理"

    def __str__(self):
        return self.title


class Project(models.Model, HitCountMixin):
    name = models.CharField(max_length=200)
    svn = models.CharField(max_length=1000)
    generating_path = models.CharField(max_length=1000)
    sync_serv_ip = models.CharField(max_length=100, null=True, blank=True)
    sync_proj_name = models.CharField(max_length=100, null=True, blank=True)
    build_serv_ip = models.CharField(max_length=100)
    build_proj_name = models.CharField(max_length=100)
    witen_smoke_serv_ip = models.CharField(max_length=100, null=True, blank=True)
    witen_smoke_proj_name = models.CharField(max_length=100, null=True, blank=True)
    witen_smoke_agent_ip = models.CharField(max_length=100, null=True, blank=True)
    btrunc_smoke_serv_ip = models.CharField(max_length=100, null=True, blank=True)
    btrunc_smoke_proj_name = models.CharField(max_length=100, null=True, blank=True)
    btrunc_smoke_agent_ip = models.CharField(max_length=100, null=True, blank=True)
    tgpp_smoke_serv_ip = models.CharField(max_length=100, null=True, blank=True)
    tgpp_smoke_proj_name = models.CharField(max_length=100, null=True, blank=True)
    tgpp_smoke_agent_ip = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "编译工程管理"
        verbose_name_plural = "编译工程管理"

    def __str__(self):
        return self.name


BUILD_RESULT = (
    ('S', '成功'),
    ("F", '失败'),
    ("M", '强制停止'),
)


class SubRecord(models.Model):
    no = models.IntegerField()
    name = models.CharField(max_length=200)
    build_id = models.CharField(max_length=100)
    start_time = models.DateTimeField('start time', null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    result = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.build_id


class Record(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sync = models.ForeignKey(SubRecord, on_delete=models.CASCADE, null=True, blank=True, related_name="sync")
    build = models.ForeignKey(SubRecord, on_delete=models.CASCADE, null=True, blank=True, related_name="build")
    witen_smoke = models.ForeignKey(SubRecord, on_delete=models.CASCADE, null=True, blank=True, related_name='witen')
    btrunc_smoke = models.ForeignKey(SubRecord, on_delete=models.CASCADE, null=True, blank=True, related_name='btrunc')
    tgpp_smoke = models.ForeignKey(SubRecord, on_delete=models.CASCADE, null=True, blank=True, related_name='tgpp')
    start_time = models.DateTimeField('start time', null=True, blank=True)
    end_time = models.DateTimeField('end time', null=True, blank=True)
    duration = models.CharField(max_length=50, null=True, blank=True, default='')
    result = models.CharField(max_length=1, choices=BUILD_RESULT, default="F", null=True, blank=True)
    url = models.CharField(max_length=1000, null=True, blank=True, default='')
    trigger = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.project.name


# 自动化记录
class Result(models.Model):
    date = models.CharField(max_length=20, null=False)
    version = models.CharField(max_length=50, null=False)
    versionpath = models.CharField(max_length=100, null=False)
    data1 = models.CharField(max_length=20, null=True)
    data2 = models.CharField(max_length=20, null=True)
    data3 = models.CharField(max_length=20, null=True)
    data4 = models.CharField(max_length=20, null=True)
    data5 = models.CharField(max_length=500, null=True)


AUTO_RESULT = (
    ("T", "通过"),
    ("F", "未通过")
)

OPTIONS = (
    ("T", "是"),
    ("F", "否")
)


# 自动化验证结果表（1）----验证版本路径及结果
class AutoRes(models.Model):
    Date = models.DateField(default=date.today, null=False, blank=False, verbose_name="日期")
    VersionNum = models.CharField(max_length=100, default="", null=False, blank=False, verbose_name="版本号")
    VersionPath = models.CharField(max_length=100, unique=True, null=False, blank=False, verbose_name="版本路径")
    res = models.CharField(max_length=1, choices=AUTO_RESULT, default="T", null=False, blank=False,
                           verbose_name="验证结果")
    options = models.CharField(max_length=10, choices=OPTIONS, default="F", null=False, blank=False, verbose_name="是否发送espace通知")

    class Meta:
        verbose_name = "自动化验证日期及路径管理"
        verbose_name_plural = "自动化验证日期及路径管理"

    def save(self, *args, **kwargs):
        receiver = auto_receiver
        title = str(self.Date) + ' 自动化验证结果已更新，点击查看'
        content = '版本号：' + str(self.VersionNum)
        if self.options == 'T':
            try:
                send_espace(receiver, title, content)
            except:
                pass
        super(AutoRes, self).save(*args, **kwargs)

    def __str__(self):
        return self.VersionPath


# 版本制式
VERSION_MODEL = (
    ("Witen", "Witen"),
    ("Btrunc", "Btrunc"),
    ("3GPP", "3GPP"),
    ("Witen-Btrunc-3GPP", "Witen-Btrunc-3GPP"),
)
# 网元
NETWORK_ELEMENT = (
    ("升级", "升级"),
    ("MDC", "MDC"),
    ("UDC", "UDC"),
    ("DC", "DC"),

)
# 验证结果
VERIFICATION_RESULT = (
    ("G", "▲"),
    ("Y", "●"),
    ("R", "■")
)
# 问题严重程度
SEVERITY_LEVEL = (
    ("1", "一般"),
    ("2", "严重"),
    ("3", "致命")
)
# 当前状态
STATUS = (
    ("1", "未定位"),
    ("2", "定位中"),
    ("3", "已定位"),
    ("4", "已解决")
)


# 自动化验证结果表（2）----详细信息
class AutoResult(models.Model):
    Time = models.TimeField(auto_now_add=True, null=False, blank=False, verbose_name="时间")
    VersionPath = models.ForeignKey(AutoRes, to_field="VersionPath", on_delete=models.CASCADE,
                                    verbose_name="版本路径")
    VersionModel = models.CharField(max_length=20, choices=VERSION_MODEL, default="Witen", null=False, blank=False,
                                    verbose_name="版本制式")
    NE = models.CharField(max_length=10, choices=NETWORK_ELEMENT, default="MDC", null=False, blank=False,
                          verbose_name="网元")
    Responsible = models.CharField(max_length=20, default="", null=False, blank=False, verbose_name="自动化测试线负责人")
    Result = models.CharField(max_length=1, choices=VERIFICATION_RESULT, default="G", null=False, blank=False,
                              verbose_name="验证结果")
    Describe = RichTextField(max_length=2000, null=True, blank=True, verbose_name="故障原因分析")

    class Meta:
        verbose_name = "自动化验证结果"
        verbose_name_plural = "自动化验证结果"


# 自动化验证结果表（3）----问题列表
class AutoProblemList(models.Model):
    DiscoveryDate = models.DateField(default=date.today, null=False, blank=False, verbose_name="问题提出日期")
    Describe = RichTextField(max_length=1000, default="", null=False, blank=False, verbose_name="问题描述")
    NE = models.CharField(max_length=10, choices=NETWORK_ELEMENT, default="MDC", null=False, blank=False,
                          verbose_name="网元")
    SeverityLevel = models.CharField(max_length=1, choices=SEVERITY_LEVEL, default="1", null=False, blank=False,
                                     verbose_name="严重程度")
    Influence = models.CharField(max_length=50, default="", null=False, blank=False, verbose_name="问题影响")
    Responsible = models.CharField(max_length=20, default="", null=False, blank=False, verbose_name="跟踪人员")
    PositioningPerson = models.CharField(max_length=20, default="", null=False, blank=False, verbose_name="定位人员/责任人")
    Status = models.CharField(max_length=20, choices=STATUS, default="1", null=False, blank=False, verbose_name="当前状态")

    def __str__(self):
        return self.Describe

    class Meta:
        verbose_name = "自动化验证问题列表管理"
        verbose_name_plural = "自动化验证问题列表管理"

    def short_describe(self):  # 在admin管理中过滤问题描述中的<p>标签，且最多只显示80个字符
        describe = str(self.Describe).replace("<p>", "")
        if len(str(describe.replace("</p>", ""))) > 80:
            return '{}......'.format(describe.replace("</p>", "")[0:80])
        else:
            return describe.replace("</p>", "")

    short_describe.allow_tags = True


SMOKEY_RESULT = (
    ("T", "通过"),
    ("F", "未通过")
)


# 冒烟结果
class SmokeyResult(models.Model):
    date = models.DateField(default=date.today, null=False, blank=False, verbose_name="日期")
    time = models.TimeField(auto_now_add=True, null=False, blank=False, verbose_name="时间")
    VersionNum = models.CharField(max_length=100, default="", null=False, blank=False, verbose_name="版本号")
    res = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False,
                           verbose_name="冒烟结果")
    describe = RichTextField(max_length=2000, null=True, blank=True, verbose_name="问题现象及责任人")
    MDC_Btrunc = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    MDC_Witen = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    MDC_3GPP = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    MDC_IM = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    MDC_UP = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    UDC_EBS = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    UDC_OTA = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    UDC_UTS = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    ISP = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    SDK = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    CID = models.CharField(max_length=1, choices=SMOKEY_RESULT, default="T", null=False, blank=False)
    version_path = models.CharField(max_length=200, default="", null=False, blank=False, verbose_name="版本路径")

    class Meta:
        verbose_name = "冒烟结果管理"
        verbose_name_plural = "冒烟结果管理"

    # 新增冒烟结果时自动发送eSpace通知
    def save(self, *args, **kwargs):
        receiver = smoke_receiver
        title = str(self.date) + ' 冒烟结果已更新，点击查看'
        content = '版本号：' + str(self.VersionNum)
        if self.pk is None:
            try:
                send_espace(receiver, title, content)
            except:
                pass
        super(SmokeyResult, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.date.strftime('%Y-%m-%d'))
