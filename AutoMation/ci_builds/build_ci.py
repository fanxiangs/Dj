import datetime
import json
import time

import requests

EXIT_CODE_ENUM = {
    0:'构建成功',
    99:'ant执行错误',
    101:'资源不存在',
    102:'依赖的job或task失败',
    103:'强制停止',
    104:'构建超时',
    105:'配置文件错误(包含工具触发策略配置错误及选择构建错误)',
    106:'路径不存在',
    107:'master与agent心跳失败',
    109:'申请资源失败',
    110:'ftp传输文件失败',
    111:'注册失败',
    112:'压缩文件失败',
    113:'解压文件失败',
    114:'拷贝报告文件失败',
    116:'ftp上传文件失败',
    117:'ftp下载文件失败',
    121:'rsync上传文件失败',
    122:'rsync下载文件失败',
    255:'未知异常',
    820:'任务失败转本地',
}

class ci_project:
    def __init__(self, ip, name):
        self.addr = 'http://'+ip
        self.name = name
        self.port = 3000
        self.url = self.addr + ":" + \
            str(self.port) + '/rest/projects/'
        self.rpm = "http://10.162.209.73:8000"

    def get_start_url(self):
        url = self.url + self.name+'/' + "start"
        print("start url:", url)
        return url

    def get_info_url(self):
        url = self.url + self.name+'/'  + "buildinfo"
        print("info url:", url)
        return url

    def get_stop_url(self):
        url =  self.url + self.name+'/'  + "stop"
        print("stop url:", url)
        return url

    # / rest / projects /: projectName / buildid /:buildid / buildinfo
    def get_info_url_with_build_id(self, build_id):
        url = self.url + self.name+'/'  + "buildid/" + build_id + "/buildinfo"
        # print("build id info url:", url)
        return url

    # / rest / projects /: buildId / stopBuild
    def get_stop_url_with_build_id(self, build_id):
        url = self.url + build_id + "/stopBuild"
        print("build id stop url:", url)
        return url

    def start(self):
        url = self.get_start_url()
        rsp = requests.post(url)
        if rsp.status_code == requests.codes.ok:
            ret = rsp.json()
            if 'message' in ret and 'data' in ret and ret['message'] == 'OK':
                data = ret['data']
                if 'No' in data and 'start_time' in data and 'build_id' in data:
                    print("工程:",data['build_id'],"启动成功，开始时间:",data['start_time'])
                    str = ''
                    if (data['exit_code'] in EXIT_CODE_ENUM):
                        str = EXIT_CODE_ENUM[data['exit_code']]
                    info = {
                        'No': data['No'],
                        'name': data['name'],
                        'start_time': data['start_time'],
                        'build_id': data['build_id'],
                        'exit_code': data['exit_code'],
                        'result': (True if data['exit_code'] == 0 else False),
                        'info': str
                    }
                    return info
            else:
                return {"result": False, 'info': ret['message']}
        return {"result": False, 'info': 'request响应异常'}

    def query_status(self, build_id = None):
        if build_id == None:
            url = self.get_info_url()
        else:
            url = self.get_info_url_with_build_id(build_id)
        rsp = requests.get(url)
        if rsp.status_code == requests.codes.ok:
            ret = rsp.json()
            if 'message' in ret and 'data' in ret and ret['message'] == 'OK':
                data = ret['data']
                if 'status' in data:
                    return data['status']

    def query(self):
        url = self.get_info_url()
        rsp = requests.get(url)
        if rsp.status_code == requests.codes.ok:
            ret = rsp.json()
            if 'message' in ret and 'data' in ret and ret['message'] == 'OK':
                data = ret['data']
                return data

    def wait_until_fin(self, build_id):
        url = self.get_info_url_with_build_id(build_id)
        while True:
            time.sleep(15)
            rsp = requests.get(url)
            if rsp.status_code == requests.codes.ok:
                ret = rsp.json()
                if 'message' in ret and 'data' in ret and ret['message'] == 'OK':
                    data = ret['data']
                    if 'status' in data:
                        if data['status'] == 'FINISH' or data['status'] == 'STOPPED':
                            if 'exit_code' in data and 'run_time' in data and 'No' in data and 'build_id' in data:
                                str = ''
                                if (data['exit_code'] in EXIT_CODE_ENUM):
                                    str = EXIT_CODE_ENUM[data['exit_code']]
                                smoke_ip = ''
                                if ('build_params' in data and 'properties' in data['build_params'] and 'Smokey_agent' in data['build_params']['properties']):
                                    smoke_ip = data['build_params']['properties']['Smokey_agent']
                                print("smoke_ip:",smoke_ip)
                                print("工程:",data['build_id'],"结束",str)
                                info = {
                                    'No': data['No'],
                                    'run_time': data['run_time'],
                                    'exit_code': data['exit_code'],
                                    'build_id': data['build_id'],
                                    'info': str,
                                    'smoke_ip': smoke_ip
                                }
                                if len(data['error_msgs']['error']) > 0:
                                    print("错误原因:",data['error_msgs']['error'][0])
                                    info['error'] = data['error_msgs']['error'][0]
                                elif len(data['error_msgs']['warning']) > 0:
                                    print("告警原因:",data['error_msgs']['warning'][0])
                                    info['error'] = data['error_msgs']['warning'][0]
                                return info
                        elif data['status'] == 'RUNNING':
                            continue

    def stop_with_build_id(self, build_id):
        url = self.get_stop_url_with_build_id(build_id)
        rsp = requests.get(url)
        if rsp.status_code == requests.codes.ok:
            ret = rsp.json()
            if 'message' in ret and ret['message'] == 'OK':
                return True
        return False

    def stop(self):
        url = self.get_stop_url()
        rsp = requests.post(url)
        if rsp.status_code == requests.codes.ok:
            ret = rsp.json()
            if 'message' in ret and ret['message'] == 'OK':
                return True
        return False

    def check_status(self):
        if self.query_status() == 'RUNNING':
            print("当前工程正在运行")
            return False
        return True

    def check_rpm(self):
        ret = self.query()
        jobs = ret['jobs']
        print(jobs)
        print('当前工程:',ret['name'],'下项目: ',jobs.keys())
        for key in jobs.keys():
            resource = jobs[key]['resource']
            rpm_query = self.rpm + "/status?ip=" + resource
            rsp = requests.get(rpm_query)
            if rsp.status_code == requests.codes.ok:
                ret = rsp.json()
                if len(ret) > 0:
                    info = ret[0]
                    status = info['status']
                    if status == 'IDLE':
                        print("工程:", key, "IP:", resource, "空闲")
                    elif status == 'BUSY':
                        print("工程: ",key,",IP: ",resource,"已占用")
                        print("上次触发时间:",info['last_job_time'],"上次触发人:",info['last_trigger'])
                        return [False,"工程: "+key+", IP: "+resource+"已占用\n上次触发时间: "+info['last_job_time']+",上次触发人: "+info['last_trigger']]
        return [True, None]


if __name__ == "__main__":
    proj = ci_project('10.162.127.200', 'rsync_build')
    proj.start()
