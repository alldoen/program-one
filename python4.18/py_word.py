import base64
import hashlib
import hmac
import json
import os
import time
from tkinter import *
import tkinter.messagebox
import requests
import tkinter as tk
from tkinter import filedialog
from moviepy.editor import *
from tkinter import *
import tkinter.messagebox
import pyttsx3


lfasr_host = 'http://raasr.xfyun.cn/api'
# 请求的接口名
api_prepare = '/prepare'
api_upload = '/upload'
api_merge = '/merge'
api_get_progress = '/getProgress'
api_get_result = '/getResult'
# 文件分片大小10M
file_piece_sice = 10485760

# ——————————————————转写可配置参数————————————————
# 参数可在官网界面（https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html）查看，根据需求可自行在gene_params方法里添加修改
# 转写类型
lfasr_type = 0
# 是否开启分词
has_participle = 'false'
has_seperate = 'true'
# 多候选词个数
max_alternatives = 0
# 子用户标识
suid = ''


class SliceIdGenerator:
    """slice id生成器"""

    def __init__(self):
        self.__ch = 'aaaaaaaaa`'

    def getNextSliceId(self):
        ch = self.__ch
        j = len(ch) - 1
        while j >= 0:
            cj = ch[j]
            if cj != 'z':
                ch = ch[:j] + chr(ord(cj) + 1) + ch[j + 1:]
                break
            else:
                ch = ch[:j] + 'a' + ch[j + 1:]
                j = j - 1
        self.__ch = ch
        return self.__ch


class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path, to_file):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.to_file = to_file

    # 根据不同的apiname生成不同的参数,本示例中未使用全部参数您可在官网(https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html)查看后选择适合业务场景的进行更换
    def gene_params(self, apiname, taskid=None, slice_id=None):
        appid = self.appid
        secret_key = self.secret_key
        upload_file_path = self.upload_file_path
        ts = str(int(time.time()))
        m2 = hashlib.md5()
        m2.update((appid + ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)
        param_dict = {}

        if apiname == api_prepare:
            # slice_num是指分片数量，如果您使用的音频都是较短音频也可以不分片，直接将slice_num指定为1即可
            slice_num = int(file_len / file_piece_sice) + (0 if (file_len % file_piece_sice == 0) else 1)
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['file_len'] = str(file_len)
            param_dict['file_name'] = file_name
            param_dict['slice_num'] = str(slice_num)
        elif apiname == api_upload:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
            param_dict['slice_id'] = slice_id
        elif apiname == api_merge:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
            param_dict['file_name'] = file_name
        elif apiname == api_get_progress or apiname == api_get_result:
            param_dict['app_id'] = appid
            param_dict['signa'] = signa
            param_dict['ts'] = ts
            param_dict['task_id'] = taskid
        return param_dict

    # 请求和结果解析，结果中各个字段的含义可参考：https://doc.xfyun.cn/rest_api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%86%99.html
    def gene_request(self, apiname, data, files=None, headers=None):
        response = requests.post(lfasr_host + apiname, data=data, files=files, headers=headers)
        result = json.loads(response.text)
        if result["ok"] == 0:
            print("{} success:".format(apiname) + str(result))
            return result
        else:
            print("{} error:".format(apiname) + str(result))
            exit(0)
            return result

    # 预处理
    def prepare_request(self):
        return self.gene_request(apiname=api_prepare,
                                 data=self.gene_params(api_prepare))

    # 上传
    def upload_request(self, taskid, upload_file_path):
        file_object = open(upload_file_path, 'rb')
        try:
            index = 1
            sig = SliceIdGenerator()
            while True:
                content = file_object.read(file_piece_sice)
                if not content or len(content) == 0:
                    break
                files = {
                    "filename": self.gene_params(api_upload).get("slice_id"),
                    "content": content
                }
                response = self.gene_request(api_upload,
                                             data=self.gene_params(api_upload, taskid=taskid,
                                                                   slice_id=sig.getNextSliceId()),
                                             files=files)
                if response.get('ok') != 0:
                    # 上传分片失败
                    print('upload slice fail, response: ' + str(response))
                    return False
                print('upload slice ' + str(index) + ' success')
                index += 1
        finally:
            'file index:' + str(file_object.tell())
            file_object.close()
        return True

    # 合并
    def merge_request(self, taskid):
        return self.gene_request(api_merge, data=self.gene_params(api_merge, taskid=taskid))

    # 获取进度
    def get_progress_request(self, taskid):
        return self.gene_request(api_get_progress, data=self.gene_params(api_get_progress, taskid=taskid))

    # 获取结果
    def get_result_request(self, taskid):
        return self.gene_request(api_get_result, data=self.gene_params(api_get_result, taskid=taskid))

    def all_api_request(self):
        # 1. 预处理
        pre_result = self.prepare_request()
        taskid = pre_result["data"]
        # 2 . 分片上传
        self.upload_request(taskid=taskid, upload_file_path=self.upload_file_path)
        # 3 . 文件合并
        self.merge_request(taskid=taskid)
        # 4 . 获取任务进度
        while True:
            # 每隔20秒获取一次任务进度
            progress = self.get_progress_request(taskid)
            progress_dic = progress
            if progress_dic['err_no'] != 0 and progress_dic['err_no'] != 26605:
                print('task error: ' + progress_dic['failed'])
                return
            else:
                data = progress_dic['data']
                task_status = json.loads(data)
                if task_status['status'] == 9:
                    print('task ' + taskid + ' finished')
                    break
                print('The task ' + taskid + ' is in processing, task status: ' + str(data))

            # 每次获取进度间隔20S
            time.sleep(20)
        # 5 . 获取结果
        res = self.get_result_request(taskid=taskid)
        r = json.loads(res["data"])
        with open(self.to_file, 'w', encoding='utf-8') as file_obj:
            for iterating_var in r:
                file_obj.write(iterating_var["onebest"])
                file_obj.write("\n")





def create():
    def mp4_mp3():
        '''打开选择文件夹对话框'''
        note = e1.get()
        if note == '':
            tkinter.messagebox.showinfo('提示', '输入为空！')
            top.destroy()
            return 0
        root1 = tk.Tk()
        root1.withdraw()
        Filepath = filedialog.askopenfilename()  # 获得选择好的文件
        print('Filepath:', Filepath)
        print('e1:',e1.get())
        if ".mp4" or ".mov" or ".mav" or ".avi"in Filepath:#mp4、mov、mav、avi
            print(True)
        else:
            tkinter.messagebox.showinfo('提示', '错误！请选择正确的文件')
            top.destroy()
            return 0
        video = VideoFileClip(Filepath)
        print(str(video))
        audio = video.audio
        audio.write_audiofile(e1.get())
        tkinter.messagebox.showinfo('提示', '视频转化成功！')
        top.destroy()
    top = Toplevel()
    top.title('视频转音频')
    top.geometry("460x100+440+400")
    Label(top, text="转化后的文件名和后缀（建议使用wav）").grid(row=0, column=0)
    e1 = Entry(top)
    e1.grid(row=0, column=1, padx=15, pady=10)
    # Button(top, text='出现2级',comand=mp4_mp3()).grid(row=1, column=1, padx=1, pady=1)
    Button(top, text="获取MP4的文件", width=15, command=mp4_mp3) \
        .grid(row=1, column=0, sticky=W, padx=10, pady=5)



def create1():
    def mp3_txt():
        '''打开选择文件夹对话框'''
        note1 = e1.get()
        if note1 == '' or e2.get() == '' or e3.get()== '':
            tkinter.messagebox.showinfo('提示', '输入为空！')
            return 0
        else:
            tkinter.messagebox.showinfo('提示', '登录成功！')
        root2 = tk.Tk()
        root2.withdraw()
        Filepath = filedialog.askopenfilename()  # 获得选择好的文件
        print('Filepath:', Filepath)
        #wav / flac / opus / m4a / mp3
        #if ".mp3" or ".wav" or ".flac" or ".opus" or ".m4a" in Filepath:
        #    print(True)
        #else:
        #    tkinter.messagebox.showinfo('提示', '错误！请选择正确的文件')
        #    top.destroy()
        #    return 0
        tkinter.messagebox.showinfo('提示', '等待时间较长，请耐心等待！')
        api = RequestApi(
            appid=e2.get(),#2ce562b1
            secret_key=e3.get(),#5afceaaa2666343d9b12842755e4585a
            upload_file_path=Filepath,
            to_file=note1
        )
        api.all_api_request()
        tkinter.messagebox.showinfo('提示', '当前音频已成功转化为文本！')
        top.destroy()
    # 注意：如果出现requests模块报错："NoneType" object has no attribute 'read', 请尝试将requests模块更新到2.20.0或以上版本(本demo测试版本为2.20.0)
    # 输入讯飞开放平台的appid，secret_key和待转写的文件路径

    top = Toplevel()
    top.title('Python')
    top.geometry("460x200+1200+400")
    Label(top, text="转化后的文件名和后缀（txt，doc等）").grid(row=0, column=0)
    e1 = Entry(top)
    e1.grid(row=0, column=1, padx=15, pady=10)
    Label(top, text="app_id").grid(row=1, column=0)
    e2 = Entry(top)
    e2.grid(row=1, column=1, padx=15, pady=10)
    Label(top, text="key").grid(row=2, column=0)
    e3 = Entry(top)
    e3.grid(row=2, column=1, padx=15, pady=10)
    # Button(top, text='出现2级',comand=mp4_mp3()).grid(row=1, column=1, padx=1, pady=1)
    Button(top, text="获取音频文件", width=10, command=mp3_txt) \
        .grid(row=3, column=1, sticky=W, padx=10, pady=5)


if __name__ == '__main__':
    root = Tk()
    root.title('python')
    root.geometry("400x120+800+400")
    Button(root, text='MP4提取音频', command=create).grid(row=0, column=1, sticky=W, padx=10, pady=20)
    Button(root, text='MP3提取txt', command=create1).grid(row=0, column=2, sticky=W, padx=10, pady=20)
    Button(root, text="退出",       command=root.quit).grid(row=1, column=4, sticky=E, padx=100, pady=10)
    mainloop()