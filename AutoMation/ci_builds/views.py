import time
from datetime import datetime
from datetime import timedelta

# import pythoncom
# import wmi
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from tracking.models import Visitor
from tracking.settings import TRACK_PAGEVIEWS

from .models import Project, Record, SubRecord, Bulletin, AutoRes, SmokeyResult, Result, AutoProblemList
from django.http import Http404
from .build_ci import ci_project, EXIT_CODE_ENUM
from django.core.cache import cache


# Create your views here.
# @login_required(login_url='/ci_projects/login_page/')
def index(request):
    bulletin_list = Bulletin.objects.all().order_by('-id')
    if bulletin_list.count() > 3:
        bulletin_list = bulletin_list[:3]
    try:
        end_time = datetime.now()
        # 今日0点
        start_time_zero = datetime.now() - timedelta(hours=end_time.hour, minutes=end_time.minute,
                                                     seconds=end_time.second,
                                                     microseconds=end_time.microsecond)

        obj = Visitor.objects.order_by('start_time')[0]

        start_time = obj.start_time
        visitor = Visitor.objects.stats(start_time, end_time)['total']
        visitor_today = Visitor.objects.stats(start_time_zero, end_time)['total']
    except (IndexError, Visitor.DoesNotExist):
        visitor = 0
        visitor_today = 0

    # queries take `date` objects (for now)
    # user_stats = Visitor.objects.user_stats(start_time, now)

    # 获取当日冒烟结果中的版本问题生成公告
    date = time.strftime("%Y-%m-%d")
    notice_list = []
    smoke_res = ""
    try:
        smoke_result_list = SmokeyResult.objects.filter(date=date)
    except:
        smoke_result_list = []
    if smoke_result_list:
        if list(smoke_result_list)[-1].res == "T":
            smoke_res = "T"
            notice_list.append(list(smoke_result_list)[-1])
        else:
            smoke_res = "F"
            for smoke_result in smoke_result_list:
                if smoke_result.describe:
                    notice_list.append(smoke_result)

    return render(request, 'ci_projects/index.html', {
        'bulletin_list': bulletin_list,
        'visitor': visitor,
        'visitor_today': visitor_today,
        'notice_list': notice_list,
        "smoke_res": smoke_res
    })


def login_page(request):
    return render(request, 'ci_projects/login.html')


def register_page(request):
    return render(request, 'ci_projects/register.html')


def register(request):
    username = request.POST['name'].lower()
    password = request.POST['pass']
    email = request.POST['email']
    if User.objects.filter(username=username).exists():
        return render(request, 'ci_projects/register.html', {
            'error': '用户已注册',
        })
    User.objects.create_user(username=username, email=email, password=password)
    return HttpResponseRedirect(reverse('login_page'))


def user_login(request):
    username = request.POST['name']
    password = request.POST['pass']
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return HttpResponseRedirect(reverse('maker'))
    else:
        return render(request, 'ci_projects/login.html', {
            'error': '用户名或密码错误',
        })


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def bulletins(request):
    bulletin_list = Bulletin.objects.all().order_by('-id')

    return render(request, 'ci_projects/bulletins.html', {
        'bulletin_list': bulletin_list,
    })


def bulletin(request, id):
    try:
        bulletin = Bulletin.objects.get(id=id)
    except Bulletin.DoesNotExist:
        raise Http404("查询的公告不存在，id=" + str(id))

    return render(request, 'ci_projects/bulletin.html', {
        'bulletin': bulletin,
    })


def about(request):
    return render(request, 'ci_projects/about.html')


def contact(request):
    return render(request, 'ci_projects/contact.html')


def faq(request):
    return render(request, 'ci_projects/faq.html')


def static(request):
    return render(request, 'ci_projects/static.html')


# @login_required
# def mail(request):
#
#     send_mail(request, result['smoke_ip'])
#     print(request.user.id, request.user.username)


@login_required
def maker(request):
    project_list = Project.objects.order_by('id')

    return render(request, 'ci_projects/maker.html', {
        'project_list': project_list,
    })


@login_required
def detail(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("查询的工程不存在，id=" + str(project_id))

    record_list = Record.objects.filter(project=project).order_by('-id')
    if record_list.count() > 8:
        record_list = record_list[:8]
    hit_count = HitCount.objects.get_for_object(project)

    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    context = {
        'project': project,
        'record_list': record_list,
    }
    context.update(hit_count_response._asdict())
    return render(request, 'ci_projects/detail.html', context)


@login_required
def mail(request, project_id):
    project = Project.objects.get(id=project_id)
    send_mail(request, project.witen_smoke_agent_ip)
    return HttpResponse()


@login_required
def send_mail(request, ip):
    user_name = request.user.username
    print("evn: ", ip, ", name: ", user_name)
    try:
        pythoncom.CoInitialize()
        wmiobj = wmi.WMI(computer=ip, user="twx10656", password="Tdtech@@@@@123")
        filename = r"D:\WN_TEST_CODE_VOB\CI\AutoEmail_smoke\specified_mail.bat"
        cmd_callbat = "cmd /c {0} {1}".format(filename, user_name)
        wmiobj.Win32_Process.Create(CommandLine=cmd_callbat)
        print("邮件发送成功")
        pythoncom.CoUninitialize()
        return True
    except Exception as e:
        print("邮件发送失败, ", str(e))
        return False


@login_required
def update(request, project_id, para):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))
    time.sleep(15)
    print(request.user.id, request.user.username)
    (sync_id, build_id, witen_id, btrunc_id, tgpp_id) = para.split('&')
    total_time = 0
    result = 'S'
    if sync_id != '':
        sync = SubRecord.objects.get(build_id=sync_id)
        print(sync)
        total_time += sync.duration
        if sync.result == 0:
            result = 'S'
        elif sync.result == 103:
            result = 'M'
        else:
            result = 'F'
    else:
        sync = None

    if build_id != '':
        build = SubRecord.objects.get(build_id=build_id)
        print(build)
        total_time += build.duration

        if result == 'S' and build.result == 0:
            result = 'S'
        elif build.result == 103:
            result = 'M'
        else:
            result = 'F'
    else:
        build = None

    if witen_id != '':
        witen = SubRecord.objects.get(build_id=witen_id)
        print(witen)

        if result == 'S' and witen.result == 0:
            result = 'S'
        elif witen.result == 103:
            result = 'M'
        else:
            result = 'F'
    else:
        witen = None

    if btrunc_id != '':
        btrunc = SubRecord.objects.get(build_id=btrunc_id)
        print(btrunc)

        if result == 'S' and btrunc.result == 0:
            result = 'S'
        elif btrunc.result == 103:
            result = 'M'
        else:
            result = 'F'
    else:
        btrunc = None

    if tgpp_id != '':
        tgpp = SubRecord.objects.get(build_id=tgpp_id)
        print(tgpp)

        if result == 'S' and tgpp.result == 0:
            result = 'S'
        elif tgpp.result == 103:
            result = 'M'
        else:
            result = 'F'
    else:
        tgpp = None

    record = Record.objects.create(project=project, sync=sync, build=build, witen_smoke=witen, btrunc_smoke=btrunc,
                                   tgpp_smoke=tgpp)
    try:
        if sync_id != '':
            record.start_time = sync.start_time
        else:
            lst_start = []
            lst_time = []
            if witen_id != '':
                lst_start.append(time.mktime(witen.start_time.timetuple()))
                lst_time.append(witen.duration)
            if btrunc_id != '':
                lst_start.append(time.mktime(btrunc.start_time.timetuple()))
                lst_time.append(btrunc.duration)
            if tgpp_id != '':
                lst_start.append(time.mktime(tgpp.start_time.timetuple()))
                lst_time.append(tgpp.duration)

            record.start_time = datetime.fromtimestamp(min(lst_start))
            total_time += max(lst_time)
        record.duration = str(timedelta(seconds=total_time))
        record.end_time = datetime.now()
        record.result = result
        now = datetime.now().strftime('%Y-%m-%d')
        if result == 'S' and build_id != '':
            record.url = project.generating_path + '\\' + now + '\\version'
        else:
            record.url = "---"
        record.trigger = request.user
        record.save()
    except:
        record.delete()

    record_list = Record.objects.filter(project=project).order_by('-id')
    if record_list.count() > 8:
        record_list = record_list[:8]

    rendering = render_to_string("ci_projects/record.html", {'record_list': record_list})
    return HttpResponse(rendering)


@login_required
def stop(request, project_id, para):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    (sync_id, build_id, witen_id, btrunc_id, tgpp_id) = para.split('&')
    if sync_id != '':
        stop_sync(request, project_id, sync_id)
    if build_id != '':
        stop_build(request, project_id, build_id)
    if witen_id != '':
        stop_witen(request, project_id, witen_id)
    if btrunc_id != '':
        stop_btrunc(request, project_id, btrunc_id)
    if tgpp_id != '':
        stop_tgpp(request, project_id, tgpp_id)

    return HttpResponse(True)


@login_required
def start_sync(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.sync_serv_ip
    name = project.sync_proj_name
    ci = ci_project(ip, name)

    result = ci.start()
    ret = {}
    if result['result']:
        id = result['No']
        name = result['name']
        start_time = result['start_time']
        build_id = result['build_id']

        obj = SubRecord.objects.create(no=id, name=name)

        obj.start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        obj.build_id = build_id
        obj.no = id
        obj.save()

        ret['no'] = id
        ret['build_id'] = build_id
        if result['exit_code'] == 0:
            ret['result'] = True
        else:
            ret['result'] = False
    else:
        ret['result'] = False
    ret['info'] = result['info']
    return JsonResponse(ret)


@login_required
def check_sync_status(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.sync_serv_ip
    name = project.sync_proj_name
    ci = ci_project(ip, name)

    if not ci.check_status():
        return JsonResponse({'result': False, 'info': '工程' + name + '已启动'})
    else:
        return JsonResponse({'result': True})


@login_required
def check_sync_rpm(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))
    ip = project.sync_serv_ip
    name = project.sync_proj_name
    ci = ci_project(ip, name)

    (result, info) = ci.check_rpm()
    if not result:
        ret = {'info': info, 'result': False}
        return JsonResponse(ret)
    else:
        return JsonResponse({'result': True})


@login_required
def wait_sync_end(request, project_id, build_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.sync_serv_ip
    name = project.sync_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.wait_until_fin(build_id)
    if result != None:
        run_time = result['run_time']
        exit_code = result['exit_code']
        # build_id = result['build_id']

        sub = SubRecord.objects.get(build_id=build_id)
        sub.duration = run_time
        sub.result = exit_code
        sub.save()

        if exit_code == 0:
            ret['result'] = True
        else:
            if 'error' in result:
                ret['info'] = result['error']
            else:
                ret['info'] = result['info']

    else:
        ret['result'] = False
        ret['info'] = 'rest执行异常'
    return JsonResponse(ret)


@login_required
def stop_sync(request, project_id, build_id):
    project = Project.objects.get(id=project_id)
    ip = project.sync_serv_ip
    name = project.sync_proj_name
    if ip != "" and name != "":
        ci = ci_project(ip, name)
        ci.stop_with_build_id(build_id)


def start_build(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.build_serv_ip
    name = project.build_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.start()
    if result != None:
        id = result['No']
        start_time = result['start_time']
        build_id = result['build_id']
        name = result['name']

        obj = SubRecord.objects.create(no=id, name=name)
        obj.start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        obj.build_id = build_id
        obj.no = id
        obj.save()

        ret['no'] = id
        ret['build_id'] = build_id
        if result['exit_code'] == 0:
            ret['result'] = True
        else:
            ret['result'] = False
    else:
        ret['result'] = False
    ret['info'] = result['info']
    return JsonResponse(ret)


@login_required
def check_build_status(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.build_serv_ip
    name = project.build_proj_name
    ci = ci_project(ip, name)

    if not ci.check_status():
        return JsonResponse({'result': False, 'info': '工程' + name + '已启动'})
    else:
        return JsonResponse({'result': True})


@login_required
def check_build_rpm(request, project_id, ):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))
    ip = project.build_serv_ip
    name = project.build_proj_name
    ci = ci_project(ip, name)

    (result, info) = ci.check_rpm()
    if not result:
        ret = {'info': info, 'result': False}
        return JsonResponse(ret)
    else:
        return JsonResponse({'result': True})


@login_required
def wait_build_end(request, project_id, build_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.build_serv_ip
    name = project.build_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.wait_until_fin(build_id)
    if result != None:
        run_time = result['run_time']
        exit_code = result['exit_code']
        # build_id = result['build_id']

        sub = SubRecord.objects.get(build_id=build_id)
        sub.duration = run_time
        sub.result = exit_code
        sub.save()

        if exit_code == 0:
            ret['result'] = True
        else:
            if 'error' in result:
                ret['info'] = result['error']
            else:
                ret['info'] = result['info']

    else:
        ret['result'] = False
        ret['info'] = 'rest执行异常'
    return JsonResponse(ret)


@login_required
def stop_build(request, project_id, build_id):
    project = Project.objects.get(id=project_id)
    ip = project.build_serv_ip
    name = project.build_proj_name
    if ip != "" and name != "":
        ci = ci_project(ip, name)
        ci.stop_with_build_id(build_id)


def check_smoke_status(request, project_id, para):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    (witen, btrunc, tgpp) = para.split('&')
    ret = {}
    if witen != '':
        witen_ip = project.witen_smoke_serv_ip
        witen_name = project.witen_smoke_proj_name
        witen_ci = ci_project(witen_ip, witen_name)

        if not witen_ci.check_status():
            ret['witen'] = {'result': False, 'info': '工程' + witen_name + '已启动'}
        else:
            ret['witen'] = {'result': True}
    if btrunc != '':
        btrunc_ip = project.btrunc_smoke_serv_ip
        btrunc_name = project.btrunc_smoke_proj_name
        btrunc_ci = ci_project(btrunc_ip, btrunc_name)

        if not btrunc_ci.check_status():
            ret['btrunc'] = {'result': False, 'info': '工程' + btrunc_name + '已启动'}
        else:
            ret['btrunc'] = {'result': True}
    if tgpp != '':
        tgpp_ip = project.tgpp_smoke_serv_ip
        tgpp_name = project.tgpp_smoke_proj_name
        tgpp_ci = ci_project(tgpp_ip, tgpp_name)

        if not tgpp_ci.check_status():
            ret['tgpp'] = {'result': False, 'info': '工程' + tgpp_name + '已启动'}
        else:
            ret['tgpp'] = {'result': True}
    return JsonResponse(ret)


@login_required
def check_smoke_rpm(request, project_id, para):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    (witen, btrunc, tgpp) = para.split('&')
    ret = {}
    if witen != '':
        witen_ip = project.witen_smoke_serv_ip
        witen_name = project.witen_smoke_proj_name
        witen_ci = ci_project(witen_ip, witen_name)

        (result, info) = witen_ci.check_rpm()
        if not result:
            ret['witen'] = {'info': info, 'result': False}
        else:
            ret['witen'] = {'result': True}
    if btrunc != '':
        btrunc_ip = project.btrunc_smoke_serv_ip
        btrunc_name = project.btrunc_smoke_proj_name
        btrunc_ci = ci_project(btrunc_ip, btrunc_name)

        (result, info) = btrunc_ci.check_rpm()
        if not result:
            ret['btrunc'] = {'info': info, 'result': False}
        else:
            ret['btrunc'] = {'result': True}
    if tgpp != '':
        tgpp_ip = project.tgpp_smoke_serv_ip
        tgpp_name = project.tgpp_smoke_proj_name
        tgpp_ci = ci_project(tgpp_ip, tgpp_name)

        (result, info) = tgpp_ci.check_rpm()
        if not result:
            ret['tgpp'] = {'info': info, 'result': False}
        else:
            ret['tgpp'] = {'result': True}
    return JsonResponse(ret)


@login_required
def start_witen(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.witen_smoke_serv_ip
    name = project.witen_smoke_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.start()
    if result != None:
        id = result['No']
        name = result['name']
        start_time = result['start_time']
        build_id = result['build_id']

        obj = SubRecord.objects.create(no=id, name=name)
        obj.start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        print('witen start time:', obj.start_time, obj.start_time.tzinfo)
        obj.build_id = build_id
        obj.no = id
        obj.save()
        print(SubRecord.objects.get(build_id=build_id).start_time)
        ret['no'] = id
        ret['build_id'] = build_id
        if result['exit_code'] == 0:
            ret['result'] = True
        else:
            ret['result'] = False
    else:
        ret['result'] = False
    ret['info'] = result['info']
    return JsonResponse(ret)


@login_required
def wait_witen_end(request, project_id, build_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.witen_smoke_serv_ip
    name = project.witen_smoke_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.wait_until_fin(build_id)
    if result != None:
        run_time = result['run_time']
        exit_code = result['exit_code']
        # build_id = result['build_id']

        sub = SubRecord.objects.get(build_id=build_id)
        sub.duration = run_time
        sub.result = exit_code
        print(sub.duration)
        sub.save()

        if exit_code == 0:
            ret['result'] = True
            if 'smoke_ip' in result and result['smoke_ip'] != '':
                smoke_ip = result['smoke_ip']
            else:
                smoke_ip = project.witen_smoke_agent_ip
            send_mail(request, smoke_ip)
        else:
            if 'error' in result:
                ret['info'] = result['error']
            else:
                ret['info'] = result['info']
    else:
        ret['result'] = False
        ret['info'] = 'rest执行异常'
    return JsonResponse(ret)


@login_required
def stop_witen(request, project_id, build_id):
    project = Project.objects.get(id=project_id)
    ip = project.witen_smoke_serv_ip
    name = project.witen_smoke_proj_name
    if ip != "" and name != "":
        ci = ci_project(ip, name)
        ci.stop_with_build_id(build_id)


@login_required
def start_btrunc(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.btrunc_smoke_serv_ip
    name = project.btrunc_smoke_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.start()
    if result != None:
        id = result['No']
        name = result['name']
        start_time = result['start_time']
        build_id = result['build_id']

        obj = SubRecord.objects.create(no=id, name=name)
        obj.start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        obj.build_id = build_id
        obj.no = id
        obj.save()

        ret['no'] = id
        ret['build_id'] = build_id
        if result['exit_code'] == 0:
            ret['result'] = True
        else:
            ret['result'] = False
    else:
        ret['result'] = False
    ret['info'] = result['info']
    return JsonResponse(ret)


@login_required
def wait_btrunc_end(request, project_id, build_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.btrunc_smoke_serv_ip
    name = project.btrunc_smoke_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.wait_until_fin(build_id)
    if result != None:
        run_time = result['run_time']
        exit_code = result['exit_code']
        # build_id = result['build_id']

        sub = SubRecord.objects.get(build_id=build_id)
        sub.duration = run_time
        sub.result = exit_code
        sub.save()

        if exit_code == 0:
            ret['result'] = True
            if 'smoke_ip' in result and result['smoke_ip'] != '':
                smoke_ip = result['smoke_ip']
            else:
                smoke_ip = project.btrunc_smoke_agent_ip
            send_mail(request, smoke_ip)
        else:
            if 'error' in result:
                ret['info'] = result['error']
            else:
                ret['info'] = result['info']

    else:
        ret['result'] = False
        ret['info'] = 'rest执行异常'
    return JsonResponse(ret)


@login_required
def stop_btrunc(request, project_id, build_id):
    project = Project.objects.get(id=project_id)
    ip = project.btrunc_smoke_serv_ip
    name = project.btrunc_smoke_proj_name
    if ip != "" and name != "":
        ci = ci_project(ip, name)
        ci.stop_with_build_id(build_id)


@login_required
def start_tgpp(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.tgpp_smoke_serv_ip
    name = project.tgpp_smoke_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.start()
    if result != None:
        id = result['No']
        name = result['name']
        start_time = result['start_time']
        build_id = result['build_id']

        obj = SubRecord.objects.create(no=id, name=name)
        obj.start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        obj.build_id = build_id
        obj.no = id
        obj.save()

        ret['no'] = id
        ret['build_id'] = build_id
        if result['exit_code'] == 0:
            ret['result'] = True
        else:
            ret['result'] = False
    else:
        ret['result'] = False
    ret['info'] = result['info']
    return JsonResponse(ret)


@login_required
def wait_tgpp_end(request, project_id, build_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    ip = project.tgpp_smoke_serv_ip
    name = project.tgpp_smoke_proj_name
    ci = ci_project(ip, name)

    ret = {}
    result = ci.wait_until_fin(build_id)
    if result != None:
        run_time = result['run_time']
        exit_code = result['exit_code']
        # build_id = result['build_id']

        sub = SubRecord.objects.get(build_id=build_id)
        sub.duration = run_time
        sub.result = exit_code
        sub.save()

        if exit_code == 0:
            ret['result'] = True
            if 'smoke_ip' in result and result['smoke_ip'] != '':
                smoke_ip = result['smoke_ip']
            else:
                smoke_ip = project.tgpp_smoke_agent_ip
            send_mail(request, smoke_ip)
        else:
            if 'error' in result:
                ret['info'] = result['error']
            else:
                ret['info'] = result['info']

    else:
        ret['result'] = False
        ret['info'] = 'rest执行异常'
    return JsonResponse(ret)


@login_required
def stop_tgpp(request, project_id, build_id):
    project = Project.objects.get(id=project_id)
    ip = project.tgpp_smoke_serv_ip
    name = project.tgpp_smoke_proj_name
    if ip != "" and name != "":
        ci = ci_project(ip, name)
        ci.stop_with_build_id(build_id)


@login_required
def query_smoke(request, project_id, para):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise Http404("操作的工程不存在，id=" + str(project_id))

    (witen, btrunc, tgpp) = para.split('&')
    if witen != '':
        witen_ip = project.witen_smoke_serv_ip
        witen_name = project.witen_smoke_proj_name
        witen_ci = ci_project(witen_ip, witen_name)

        if witen_ci.query_status(witen) == 'RUNNING':
            return JsonResponse({'result': False})

    if btrunc != '':
        btrunc_ip = project.btrunc_smoke_serv_ip
        btrunc_name = project.btrunc_smoke_proj_name
        btrunc_ci = ci_project(btrunc_ip, btrunc_name)

        if btrunc_ci.query_status(btrunc) == 'RUNNING':
            return JsonResponse({'result': False})
    if tgpp != '':
        tgpp_ip = project.tgpp_smoke_serv_ip
        tgpp_name = project.tgpp_smoke_proj_name
        tgpp_ci = ci_project(tgpp_ip, tgpp_name)

        if tgpp_ci.query_status(tgpp) == 'RUNNING':
            return JsonResponse({'result': False})
    return JsonResponse({'result': True})


def daily(request):
    return render(request, 'ci_projects/daily.html')


# 自动化记录add

def add_data(request):
    data_list = []
    if request.method == "POST":
        date = request.POST.get("date", None)
        version = request.POST.get("version", None)
        versionpath = request.POST.get("versionpath", None)
        data1 = request.POST.getlist("data1", [])
        data2 = request.POST.getlist("data2", [])
        data3 = request.POST.getlist("data3", [])
        data4 = request.POST.getlist("data4", [])
        data5 = request.POST.getlist("data5", [])
        for i in range(len(data1)):
            Result.objects.create(date=date, version=version, versionpath=versionpath, data1=data1[i], data2=data2[i],
                                  data3=data3[i], data4=data4[i], data5=data5[i])
        if date != None:
            data_list = Result.objects.filter(date=date)
        else:
            data_list = Result.objects.all()
    return render(request, "ci_projects/add_data.html", {"data_list": data_list})


# 冒烟结果和自动化验证结果查询filter表示=，exclude表示!=BookInfo.objects.filter(heroinfo__id = 1)

def search(request):
    if request.method == "GET":
        date = time.strftime("%Y-%m-%d")
        print(date)
        try:  # 查冒烟结果
            smoke_result_list = SmokeyResult.objects.filter(date=date)
        except:
            smoke_result_list = []

        try:  # 查自动化结果
            auto_res_list = AutoRes.objects.filter(Date=date)
        except:
            auto_res_list = []

        try:  # 查版本问题
            auto_problem_list = AutoProblemList.objects.exclude(Status="4")
        except:
            auto_problem_list = []
        return render(request, "ci_projects/search.html", {"smoke_result_list": smoke_result_list,
                                                           "auto_res_list": auto_res_list,
                                                           "auto_problem_list": auto_problem_list})

    if request.method == "POST":
        date = request.POST.get("date", None)
        print(date)
        if date:
            try:  # 查冒烟结果
                smoke_result_list = SmokeyResult.objects.filter(date=date)
            except:
                smoke_result_list = []

            try:  # 查自动化结果
                auto_res_list = AutoRes.objects.filter(Date=date)
            except:
                auto_res_list = []

            try:  # 查版本问题
                auto_problem_list = AutoProblemList.objects.exclude(Status="4")
            except:
                auto_problem_list = []
        else:
            smoke_result_list = []
            auto_res_list = []
            auto_problem_list = []
        return render(request, "ci_projects/search.html", {"smoke_result_list": smoke_result_list,
                                                           "auto_res_list": auto_res_list,
                                                           "auto_problem_list": auto_problem_list})

