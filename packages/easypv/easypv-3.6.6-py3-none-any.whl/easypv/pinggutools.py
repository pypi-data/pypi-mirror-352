#!/usr/bin/env python
# coding: utf-8
# 阅易评
# 开发人：蔡权周，张博涵


# 第一部分：导入基本模块及初始化 ########################################################################

# 导入一些基本模块
import warnings
import traceback
import re
import xlrd
import xlwt
import openpyxl
import pandas as pd
import numpy as np
import math
import tkinter as Tk
from tkinter import ttk
from tkinter import *
import tkinter.font as tkFont
from tkinter import filedialog, dialog, PhotoImage
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
import collections
from collections import Counter
import datetime
from datetime import datetime, timedelta
from tkinter import END
import xlsxwriter
import os
import time
import threading
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# 定义一些全局变量
global ori  # 源文件
global biaozhun  # 导入自定义的评分标准储存
global dishi  # 地市列表
biaozhun = ""  # 用于标准的判断，如果长度为0则使用内置标准
dishi = ""
ori = 0  # 源文件初始化
global modex
modex=""

import random
import requests
global version_now
global usergroup
global setting_cfg
global csdir
global peizhidir
version_now="1.0.1" 
usergroup="用户组=0"
setting_cfg=""
csdir =str (os .path .abspath (__file__ )).replace (str (__file__ ),"")
if csdir=="":
    csdir =str (os .path .dirname (__file__ ))#
    csdir =csdir +csdir.split ("easypv")[0 ][-1 ]#
    
    
def get_data_path(filename):
    """
    获取数据文件的绝对路径。
    """
    # 获取当前包的安装目录
    package_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建数据文件的路径
    data_path = os.path.join(package_dir, 'data', filename)
    
    # 检查文件是否存在
    #if not os.path.exists(data_path):
    #    raise FileNotFoundError(f"Data file '{filename}' not found at {data_path}")
    
    return data_path

# 示例：获取 sor.zip 的路径
try:
    def_path = get_data_path('def.zip')
    #print(f"sor.zip path: {sor_path}")
except FileNotFoundError as e:
    print(e)
    
#print(csdir)
# 第二部分：函数模块 ##################################################################

    
#序列号与用户组验证模块。

def EasyInf():
    inf={
    '软件名称':'报告表质量评估工具',
    '版本号':'1.0.1',
    '功能介绍':'快速启动一些小工具。',
    'PID':'MDRDSREGTLF006fg',
    '分组':'药物警戒',
    '依赖':'pandas,numpy,scipy,matplotlib,sqlalchemy'
        }
    return inf
    
def extract_zip_file(zip_file_path, extract_path):
    import zipfile
    import sys
    
    if not extract_path:
        return 0
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            try:
                # 尝试UTF-8解码（Python 3.11+默认使用UTF-8）
                filename = file_info.filename.encode('cp437').decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # 尝试GBK解码（常见于中文Windows创建的zip文件）
                    filename = file_info.filename.encode('cp437').decode('gbk')
                except UnicodeDecodeError:
                    # 如果都失败，使用原始文件名
                    filename = file_info.filename
            
            # 确保路径分隔符是当前系统的正确格式
            filename = filename.replace('/', '\\') if '\\' in sys.path[0] else filename.replace('\\', '/')
            
            # 更新文件名并解压
            file_info.filename = filename
            zip_ref.extract(file_info, extract_path)

def get_directory_path(directory_path):
    global csdir  # 假设 csdir 是之前定义好的包含 zip 文件的目录
    
    # 检查目录是否存在指定的文件
    file_path = os.path.join(directory_path, '！！！配置表版本（请勿删除本文件）.txt')
    if not os.path.isfile(file_path):
        # 创建一个 Tkinter 根窗口（隐藏主窗口）
        root = Toplevel()
        root.withdraw()  # 隐藏主窗口
        from tkinter import messagebox
        # 弹出确认框
        message = "程序将在该目录内生成相关配置文件。这个目录内的同名文件将会被取代，建议做好备份，请问是否继续？"
        user_response = messagebox.askyesno("确认解压", message)
        
        # 根据用户响应决定是否解压
        if user_response:
            # 假设 csdir + "def.zip" 是正确的 zip 文件路径
            #zip_file_path = os.path.join(csdir, "def.py")  # 修改为正确的 zip 文件名
            extract_zip_file(def_path, directory_path)
        else:
            # 用户选择否，退出程序
            root.destroy()  # 销毁隐藏的 Tkinter 窗口
            quit()
    
    # 检查目录路径是否为空，如果为空则退出程序
    if directory_path == "":
        quit()
    
    # 返回目录路径
    return directory_path
    


def convert_and_compare_dates(date_str):
    import datetime
    current_date = datetime.datetime.now()

    try:
       date_obj = datetime.datetime.strptime(str(int(int(date_str)/4)), "%Y%m%d") 
    except:
        print("fail")
        return  "已过期"
  
    if date_obj > current_date:
        
        return "未过期"
    else:
        return "已过期"
    
def read_setting_cfg():
    global csdir
    # 读取 setting.cfg 文件
    if os.path.exists(csdir+'setting.cfg'):
        text.insert(END,"已完成初始化\n")
        with open(csdir+'setting.cfg', 'r') as f:
            setting_cfg = eval(f.read())
    else:
        # 创建 setting.cfg 文件，如果文件已存在则覆盖
        setting_cfg_path =csdir+ 'setting.cfg'
        with open(setting_cfg_path, 'w') as f:
            f.write('{"settingdir": 0, "sidori": 0, "sidfinal": "11111180000808"}')
        text.insert(END,"未初始化，正在初始化...\n")
        setting_cfg = read_setting_cfg()
    return setting_cfg
    

def open_setting_cfg():
    global csdir
    # 打开 setting.cfg 文件
    with open(csdir+"setting.cfg", "r") as f:
        # 将文件内容转换为字典
        setting_cfg = eval(f.read())
    return setting_cfg

def update_setting_cfg(keys,values):
    global csdir
    # 打开 setting.cfg 文件
    with open(csdir+"setting.cfg", "r") as f:
        # 将文件内容转换为字典
        setting_cfg = eval(f.read())
    
    if setting_cfg[keys]==0 or setting_cfg[keys]=="11111180000808" :
        setting_cfg[keys]=values
        # 保存字典覆盖源文件
        with open(csdir+"setting.cfg", "w") as f:
            f.write(str(setting_cfg))


def generate_random_file():
    # 生成一个六位数的随机数
    random_number = random.randint(200000, 299999)
    # 将随机数保存到文本文件中
    update_setting_cfg("sidori",random_number)

def display_random_number():
    global csdir
    mroot = Toplevel()
    mroot.title("ID")
    
    sw = mroot.winfo_screenwidth()
    sh = mroot.winfo_screenheight()
    # 得到屏幕高度
    ww = 80
    wh = 70
    # 窗口宽高为100
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    mroot.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    
    # 打开 setting.cfg 文件
    with open(csdir+"setting.cfg", "r") as f:
        # 将文件内容转换为字典
        setting_cfg = eval(f.read())
    random_number=int(setting_cfg["sidori"])
    sid=random_number*2+183576

    print(sid)
    # 创建标签和输入框
    label = ttk.Label(mroot, text=f"机器码: {random_number}")
    entry = ttk.Entry(mroot)

    # 将标签和输入框添加到窗口中
    label.pack()
    entry.pack()

    # 监听输入框的回车键事件
    #entry.bind("<Return>", check_input)
    ttk.Button(mroot, text="验证", command=lambda:check_input(entry.get(),sid)).pack()
    
def check_input(input_numbers,sid):

    # 将输入的数字转换为整数'

    try:
        input_number = int(str(input_numbers)[0:6])
        day_end=convert_and_compare_dates(str(input_numbers)[6:14])
    except:
        showinfo(title="提示", message="不匹配，注册失败。")
        return 0
    # 核对输入的数字是否等于随机数字
    if input_number == sid and day_end=="未过期":
        update_setting_cfg("sidfinal",input_numbers)
        showinfo(title="提示", message="注册成功,请重新启动程序。")
        quit()
    else:
        showinfo(title="提示", message="不匹配，注册失败。")

###############################


def update_software(package_name):
    # 检查当前安装的版本
    global version_now   
    text.insert(END,"当前版本为："+version_now+",正在检查更新...(您可以同时执行分析任务)") 
    try: 
        latest_version = requests.get(f"https://pypi.org/pypi/{package_name}/json",timeout=2).json()["info"]["version"]
    except:
        return "...更新失败。"
    if latest_version > version_now:
        text.insert(END,"\n最新版本为："+latest_version+",正在尝试自动更新....")        
        # 如果 PyPI 中有更高版本的软件，则使用 `pip install --upgrade` 进行更新
        pip.main(['install', package_name, '--upgrade'])
        text.insert(END,"\n您可以开展工作。")
        return "...更新成功。"
#######################################################            
# 第二部分：函数模块 ##################################################################
def Topentable(methon):
    """导入表格，包括评分标准（methon=123）、原始数据（methon=1）、专家评分等三种情况"""
    global ori
    global biaozhun
    global dishi
    lista = []  # 用于导入专家评分文件路径的存储
    listb = []  # 用于导入被抽出所有数据文件路径储存
    mvpd = 1  # 用于判断被抽出所有数据文件是否被选择导入

    # 更改评分标准（含地市列表）专用
    if methon == 123:
        try:
            filenamebiaozhun = filedialog.askopenfilename(
                filetypes=[("XLS", ".xls"), ("XLSX", ".xlsx")]
            )
            biaozhun = pd.read_excel(
                filenamebiaozhun, sheet_name=0, header=0, index_col=0
            ).reset_index()
        except:
            showinfo(title="提示", message="配置表文件有误或您没有选择。")
            return 0
        try:
            dishi = pd.read_excel(
                filenamebiaozhun, sheet_name="地市清单", header=0, index_col=0
            ).reset_index()
        except:
            showinfo(title="提示", message="您选择的配置文件没有地市列表或您没有选择。")
            return 0
        if (
            "评分项" in biaozhun.columns
            and "打分标准" in biaozhun.columns
            and "专家序号" not in biaozhun.columns
        ):
            text.insert(END, "\n您使用自定义的配置表。")
            text.see(END)
            showinfo(title="提示", message="您将使用自定义的配置表。")
            return 0
        else:
            showinfo(title="提示", message="配置表文件有误，请正确选择。")
            biaozhun = ""
            return 0

    # 导入专家评分表和被抽出的所有样表模块
    try:
        if methon!=1:
            allfileName = filedialog.askopenfilenames(
                filetypes=[("Excel Files", "*.xls *.xlsx"), ("XLS", "*.xls"), ("XLSX", "*.xlsx")]
            )
        if methon == 1:
            allfileName = filedialog.askopenfilenames(
                filetypes=[("XLSX", ".xlsx"),("XLS", ".xls") ]
            )	#filetypes=[("XLS", ".xlsx"),("XLS", ".xls") ]		
            for qq in allfileName:
                if ("●专家评分表" in qq) and ("●(最终评分需导入)被抽出的所有数据.xls" not in qq):
                    lista.append(qq)
                elif "●(最终评分需导入)被抽出的所有数据.xls" in qq:
                    listb.append(qq)
                    namerrr=qq.replace("●(最终评分需导入)被抽出的所有数据", "分数错误信息")
                    mvpd = 0
            if mvpd == 1:

                showinfo(title="提示", message="请一并导入以下文件：●(最终评分需导入)被抽出的所有数据.xls")
                return 0
            allfileName = lista
        k = [
            pd.read_excel(x, header=0, sheet_name=0) for x in allfileName
        ]  # ,index_col=0
        ori = pd.concat(k, ignore_index=True).drop_duplicates().reset_index(drop=True)
        
        
        if "报告编码" in ori.columns or "报告表编码" in ori.columns:
            ori = ori.fillna("-未填写-") 
                   
        #兼容药品
        if "报告类型-新的" in ori.columns:
            biaozhun= pd.read_excel(
                    peizhidir+"pinggu_质量评估.xls", sheet_name="药品", header=0, index_col=0
                ).reset_index()
            ori["报告编码"]=ori["报告表编码"]
            text.insert(END,"检测到导入的文件为药品报告，正在进行兼容性数据规整，请稍后...")
            ori = ori.rename(columns={"医院名称": "单位名称"})
            ori = ori.rename(columns={"报告地区名称": "使用单位、经营企业所属监测机构"})
            ori = ori.rename(columns={"报告类型-严重程度": "伤害"})
            ori["伤害"]=ori["伤害"].str.replace("一般", "其他",regex=False)  #不良反应结果
            ori["伤害"]=ori["伤害"].str.replace("严重", "严重伤害",regex=False)  #不良反应结果
            ori.loc[(ori["不良反应结果"] =="死亡"), "伤害"] = "死亡"
            ori["上报单位所属地区"]=ori["使用单位、经营企业所属监测机构"]
            try:
                ori["报告编码"]=ori["唯一标识"]
            except:
                pass
           
    
           
            ori["药品信息"]=""           
            aaa2=0
            aaa=len(ori["报告编码"].drop_duplicates())                         							
            for myi in ori["报告编码"].drop_duplicates():  
                aaa2=aaa2+1
                nowx=round(aaa2/aaa,2)
                try:
                    change_schedule(aaa2,aaa) 
                except:
                    if nowx in [0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90,0.99]: 
                        text.insert(END,nowx)	
                        text.insert(END,"...")	
      
                ori_myi=ori[(ori["报告编码"]==myi)].sort_values(by=["药品序号"]).reset_index() 
                for ids, cols in ori_myi.iterrows():
                    ori.loc[(ori["报告编码"] ==cols["报告编码"]), "药品信息"] = ori["药品信息"]+"●药品序号："+str(cols["药品序号"])+" 性质："+str(cols["怀疑/并用"])+"\n批准文号:"+str(cols["批准文号"])+"\n商品名称："+str(cols["商品名称"])+"\n通用名称："+str(cols["通用名称"])+"\n剂型："+str(cols["剂型"])+"\n生产厂家："+str(cols["生产厂家"])+"\n生产批号："+str(cols["生产批号"])+"\n用量："+str(cols["用量"])+str(cols["用量单位"])+"，"+str(cols["用法-日"])+"日"+str(cols["用法-次"])+"次\n给药途径:"+str(cols["给药途径"])+"\n用药开始时间："+str(cols["用药开始时间"])+"\n用药终止时间："+str(cols["用药终止时间"])+"\n用药原因："+str(cols["用药原因"])+"\n"
            ori=ori.drop_duplicates("报告编码")

        #writererr = pd.ExcelWriter(r"test.xls")  # engin="xlsxwriter"
        #ori.to_excel(writererr, sheet_name="字典数据")
        #writererr.close()
        
        #兼容化妆品
        if "皮损部位" in ori.columns:
            biaozhun= pd.read_excel(
                    peizhidir+"pinggu_质量评估.xls", sheet_name="化妆品", header=0, index_col=0
                ).reset_index()
            ori["报告编码"]=ori["报告表编号"]
            text.insert(END,"检测到导入的文件为化妆品报告，正在进行兼容性数据规整，请稍后...")
            #ori = ori.rename(columns={"报告单位名称": "单位名称"})
            ori["报告地区名称"]=ori["报告单位名称"].astype(str)
            #ori = ori.rename(columns={"报告地区名称": "报告地区"})
            ori["单位名称"]= ori["报告单位名称"].astype(str)            
            ori["伤害"]= ori["报告类型"].astype(str)
            ori["伤害"]=ori["伤害"].str.replace("一般", "其他",regex=False)  #不良反应结果
            ori["伤害"]=ori["伤害"].str.replace("严重", "严重伤害",regex=False)  #不良反应结果
            #ori.loc[(ori["不良反应结果"] =="死亡"), "伤害"] = "死亡"
            ori["上报单位所属地区"]=ori["报告地区名称"]
            try:
                ori["报告编码"]=ori["唯一标识"]
            except:
                pass
            text.insert(END,"\n正在开展化妆品注册单位规整...")
            listxx2 = pd.read_excel(peizhidir+"0（范例）注册单位.xlsx",sheet_name="机构列表",header=0,index_col=0,).reset_index()

            for ids, cols in listxx2.iterrows():
                ori.loc[(ori["单位名称"] == cols["中文全称"]), "监测机构"] = cols["归属地区"]
                ori.loc[(ori["单位名称"] == cols["中文全称"]), "市级监测机构"] = cols["地市"]			
            ori["监测机构"]=ori["监测机构"].fillna("未规整")
            ori["市级监测机构"]=ori["市级监测机构"].fillna("未规整")		


        try:#使用上报单位表规整
                text.insert(END,"\n开展报告单位和监测机构名称规整...")
                listxx1 = pd.read_excel(peizhidir+"share_adrmdr_pinggu_上报单位.xls",sheet_name="报告单位",header=0,index_col=0,).fillna("没有定义好X").reset_index()
                listxx2 = pd.read_excel(peizhidir+"share_adrmdr_pinggu_上报单位.xls",sheet_name="监测机构",header=0,index_col=0,).fillna("没有定义好X").reset_index()
                listxx3 = pd.read_excel(peizhidir+"share_adrmdr_pinggu_上报单位.xls",sheet_name="地市清单",header=0,index_col=0,).fillna("没有定义好X").reset_index()                                
                for ids, cols in listxx1.iterrows():
                        ori.loc[(ori["单位名称"] == cols["曾用名1"]), "单位名称"] = cols["单位名称"]
                        ori.loc[(ori["单位名称"] == cols["曾用名2"]), "单位名称"] = cols["单位名称"]
                        ori.loc[(ori["单位名称"] == cols["曾用名3"]), "单位名称"] = cols["单位名称"]
                        ori.loc[(ori["单位名称"] == cols["曾用名4"]), "单位名称"] = cols["单位名称"]
                        ori.loc[(ori["单位名称"] == cols["曾用名5"]), "单位名称"] = cols["单位名称"]
                                               

                        ori.loc[(ori["单位名称"] == cols["单位名称"]), "使用单位、经营企业所属监测机构"] = cols["监测机构"]

                for ids, cols in listxx2.iterrows():
                        ori.loc[(ori["使用单位、经营企业所属监测机构"] == cols["曾用名1"]), "使用单位、经营企业所属监测机构"] = cols["监测机构"]
                        ori.loc[(ori["使用单位、经营企业所属监测机构"] == cols["曾用名2"]), "使用单位、经营企业所属监测机构"] = cols["监测机构"]
                        ori.loc[(ori["使用单位、经营企业所属监测机构"] == cols["曾用名3"]), "使用单位、经营企业所属监测机构"] = cols["监测机构"]
                
                for qwe in listxx3["地市列表"]:
                        ori.loc[(ori["上报单位所属地区"].str.contains(qwe, na=False)), "市级监测机构"] = qwe                    
                ori.loc[(ori["上报单位所属地区"].str.contains("顺德", na=False)), "市级监测机构"] = "佛山"  

        except:#使用上报单位表规整
                text.insert(END,"\n报告单位和监测机构名称规整失败.")   

    except:
        showinfo(title="提示", message="导入文件错误,请重试。")
        return 0

    # 去除无效列和对报告编码做一些格式处理
    try:
        ori = ori.loc[:, ~ori.columns.str.contains("Unnamed")]
    except:
        pass
    try:
        ori["报告编码"] = ori["报告编码"].astype(str)
    except:
        pass

    # 打乱顺序，之后再重新编号
    ori = ori.sample(frac=1).copy()
    ori.reset_index(inplace=True)
    text.insert(END, "\n数据读取成功，行数：" + str(len(ori)))
    text.see(END)

    # 如果是导入原始数据，进行一些校验
    if methon == 0:
        if "报告编码" not in ori.columns:
            showinfo(title="提示信息", message="\n在校验过程中，发现您导入的并非原始报告数据，请重新导入。")
        else:
            showinfo(title="提示信息", message="\n数据读取成功。")
        return 0

    # 如果导入的是专家文件，对专家的打分做一些校验，如果存在错误也return 0以免执行下一步（如果导入的是原始数据，上面一步已经return 0了）。
    data = ori.copy()
    errdict = {}
    ko = 0
    if "专家序号" not in data.columns:
        showinfo(title="提示信息", message="您导入的并非专家评分文件，请重新导入。")
        return 0
    for ids, cols in data.iterrows():
        lieming = "专家打分-" + str(cols["条目"])
        try:
            float(cols["评分"])
            float(cols["满分"])
        except:
            showinfo(
                title="错误提示",
                message="因专家评分或满分值输入的不是数字，导致了程序中止，请修正："
                + "专家序号："
                + str(int(cols["专家序号"]))
                + "，报告序号："
                + str(int(cols["序号"]))
                + cols["条目"],
            )
            ori = 0
        if float(cols["评分"]) > float(cols["满分"]) or float(cols["评分"]) < 0:
            errdict[str(ids)] = (
                "专家序号："
                + str(int(cols["专家序号"]))
                + "；  报告序号："
                + str(int(cols["序号"]))
                + cols["条目"]
            )
            ko = 1
            # print(errdict[str(ids)])
    if ko == 1:
        err = pd.DataFrame(list(errdict.items()), columns=["错误编号", "错误信息"])
        del err["错误编号"]
        name = namerrr
        err = err.sort_values(by=["错误信息"], ascending=True, na_position="last")
        writererr = pd.ExcelWriter(name)  # engin="xlsxwriter"
        err.to_excel(writererr, sheet_name="字典数据")
        writererr.close()
        showinfo(
            title="警告",
            message="经检查，部分专家的打分存在错误。请您修正错误的打分文件再重新导入全部的专家打分文件。详见:分数错误信息.xls",
        )
        text.insert(END, "\n经检查，部分专家的打分存在错误。详见:分数错误信息.xls。请您修正错误的打分文件再重新导入全部的专家打分文件。")
        text.insert(END, "\n以下是错误信息概况：\n")
        text.insert(END, err)
        text.see(END)
        return 0

    # 专家文件校验通过后，返回有效的值到下一步
    if methon == 1:
        return ori, listb


def Tchouyang(datam):
    """随机抽样及随机分组"""
    # 校验一下，如果没有导入原始数据或者导入了专家数据，不可以往下执行。
    try:
        if datam == 0:
            showinfo(title="提示", message="您尚未导入原始数据。")
            return 0
    except:
        pass
    if "详细描述" in datam.columns:
        showinfo(title="提示", message="目前工作文件为专家评分文件，请导入原始数据进行抽样。")
        return 0

    # 构建抽样界面
    se = Toplevel()
    se.title("随机抽样及随机分组")
    sw_se = se.winfo_screenwidth()
    # 得到屏幕宽度
    sh_se = se.winfo_screenheight()
    # 得到屏幕高度
    ww_se = 300
    wh_se = 220
    # 窗口宽高为100
    x_se = (sw_se - ww_se) / 1.7
    y_se = (sh_se - wh_se) / 2
    se.geometry("%dx%d+%d+%d" % (ww_se, wh_se, x_se, y_se))

    import_sey = Label(se, text="评估对象：")
    import_sey.grid(row=1, column=0, sticky="w")
    comvalue = StringVar()  # 窗体自带的文本，新建一个值
    comboxlist = ttk.Combobox(
        se, width=25, height=10, state="readonly", textvariable=comvalue
    )  # 初始化
    comboxlist["values"] = ["上报单位", "县区", "地市", "省级审核人", "上市许可持有人"]  # "市级监测机构","使用单位、经营企业所属监测机构"
    comboxlist.current(0)  # 默认选择最后一个
    comboxlist.grid(row=2, column=0)  # , sticky='w')

    import_seFGF = Label(se, text="-----------------------------------------")
    import_seFGF.grid(row=3, column=0, sticky="w")

    import_seSW = Label(se, text="死亡报告抽样数量（>1)或比例(<=1)：")
    import_seSW.grid(row=4, column=0, sticky="w")
    import_se_entrySW = Entry(se, width=10)
    import_se_entrySW.grid(row=4, column=1, sticky="w")

    import_seYZ = Label(se, text="严重报告抽样数量（>1)或比例(<=1)：")
    import_seYZ.grid(row=6, column=0, sticky="w")
    import_se_entryYZ = Entry(se, width=10)
    import_se_entryYZ.grid(row=6, column=1, sticky="w")

    import_seYB = Label(se, text="一般报告抽样数量（>1)或比例(<=1)：")
    import_seYB.grid(row=8, column=0, sticky="w")
    import_se_entryYB = Entry(se, width=10)
    import_se_entryYB.grid(row=8, column=1, sticky="w")

    import_seFGF = Label(se, text="-----------------------------------------")
    import_seFGF.grid(row=9, column=0, sticky="w")

    import_se2 = Label(se, text="抽样后随机分组数（专家数量）：")
    import_se2_entry = Entry(se, width=10)
    import_se2.grid(row=10, column=0, sticky="w")
    import_se2_entry.grid(row=10, column=1, sticky="w")

    btn_se2 = Button(
        se,
        text="最大覆盖",
        width=12,
        command=lambda: thread_it(
            Tdoing0,
            datam,
            import_se_entryYB.get(),
            import_se_entryYZ.get(),
            import_se_entrySW.get(),
            import_se2_entry.get(),
            comboxlist.get(),
            "最大覆盖",
            1,
        ),
    )  # comboxlistz.get()
    btn_se2.grid(row=13, column=1, sticky="w")
    btn_se3=Button(se,text="总体随机",width=12,command=lambda:thread_it(Tdoing0,datam,import_se_entryYB.get(),import_se_entryYZ.get(),import_se_entrySW.get(),import_se2_entry.get(),comboxlist.get(),"总体随机",1))#comboxlistz.get()
    btn_se3.grid(row=13, column=0, sticky='w')





def Tdoing0(datams0, fracn1, fracn2, fracn3, no, group_by, methon, yongtu):
    """随机抽样及随机分组-准备文件"""
    global dishi
    global biaozhun

    # 检验一些参数是否输入完整
    if (
        fracn1 == ""
        or fracn2 == ""
        or fracn3 == ""
        or no == ""
        or group_by == ""
        or methon == ""
    ):
        showinfo(title="提示信息", message="参数设置不完整。")
        return 0
    if group_by == "上报单位":
        group_by = "单位名称"
    if group_by == "县区":
        group_by = "使用单位、经营企业所属监测机构"  # "市级监测机构",""
    if group_by == "地市":
        group_by = "市级监测机构"
    if group_by == "省级审核人":
        group_by = "审核人.1"
        datams0["modex"]=1
        datams0["审核人.1"]=datams0["审核人.1"].fillna("未填写")
    if group_by == "上市许可持有人":
        group_by = "上市许可持有人名称"
        datams0["modex"]=1
        datams0["上市许可持有人名称"]=datams0["上市许可持有人名称"].fillna("未填写")
    # 校验是否存在配置表，使用顺序：导入的＞配置表文件夹中的＞内置的，其中内置的没有的地市列表。
    if yongtu == 1:
        if len(biaozhun) == 0:
            umeu = peizhidir+"pinggu_质量评估.xls"
            try:
                if "modex" in datams0.columns:
                    pdb = pd.read_excel(umeu, sheet_name="器械持有人", header=0, index_col=0).reset_index()
                else:
                    pdb = pd.read_excel(umeu, sheet_name=0, header=0, index_col=0).reset_index()   
                text.insert(END, "\n您使用配置表文件夹中的“pinggu_质量评估.xls“作为评分标准。")
                text.see(END)
                # r=pdb.to_dict()
                # text.insert(END,r)
            except:
                pdb = pd.DataFrame(
                    {
                        "评分项": {
                            0: "识别代码",
                            1: "报告人",
                            2: "联系人",
                            3: "联系电话",
                            4: "注册证编号/曾用注册证编号",
                            5: "产品名称",
                            6: "型号和规格",
                            7: "产品批号和产品编号",
                            8: "生产日期",
                            9: "有效期至",
                            10: "事件发生日期",
                            11: "发现或获知日期",
                            12: "伤害",
                            13: "伤害表现",
                            14: "器械故障表现",
                            15: "年龄和年龄类型",
                            16: "性别",
                            17: "预期治疗疾病或作用",
                            18: "器械使用日期",
                            19: "使用场所和场所名称",
                            20: "使用过程",
                            21: "合并用药/械情况说明",
                            22: "事件原因分析和事件原因分析描述",
                            23: "初步处置情况",
                        },
                        "打分标准": {
                            0: "",
                            1: "填写人名或XX科室，得1分",
                            2: "填写报告填报人员姓名或XX科X医生，得1分",
                            3: "填写报告填报人员移动电话或所在科室固定电话，得1分",
                            4: "可利用国家局数据库检索，注册证号与产品名称及事件描述相匹配的，得8分",
                            5: "可利用国家局数据库检索，注册证号与产品名称及事件描述相匹配的，得4分",
                            6: "规格和型号任填其一，且内容正确，得4分",
                            7: "产品批号和编号任填其一，且内容正确，,得4分。\n注意：（1）如果该器械使用年限久远，或在院外用械，批号或编号无法查询追溯的，报告表“使用过程”中给予说明的，得4分；（2）出现YZB格式、YY格式、GB格式等产品标准格式，或“XX生产许XX”等许可证号，得0分；（3）出现和注册证号一样的数字，得0分。",
                            8: "确保“生产日期”和“有效期至”逻辑正确，“有效期至”晚于“生产日期”，且两者时间间隔应为整月或整年，得2分。",
                            9: "确保生产日期和有效期逻辑正确。\n注意：如果该器械是使用年限久远的（2014年之前生产产品），或在院外用械，生产日期和有效期无法查询追溯的，并在报告表“使用过程”中给予说明的，该项得4分",
                            10: "指发生医疗器械不良事件的日期，应与使用过程描述一致，如仅知道事件发生年份，填写当年的1月1日；如仅知道年份和月份，填写当月的第1日；如年月日均未知，填写事件获知日期，并在“使用过程”给予说明。填写正确得2分。\n注意：“事件发生日期”早于“器械使用日期”的，得0分。",
                            11: "指报告单位发现或知悉该不良事件的日期，填写正确得5分。\n注意：“发现或获知日期”早于“事件发生日期”的，或者早于使用日期的，得0分。",
                            12: "分为“死亡”、“严重伤害”“其他”，判断正确，得8分。",
                            13: "描述准确且简明，或者勾选的术语贴切的，得6分；描述较为准确且简明，或选择术语较为贴切，或描述准确但不够简洁，得3分；描述冗长、填成器械故障表现的，得0分。\n注意：对于“严重伤害”事件，需写明实际导致的严重伤害，填写不恰当的或填写“无”的，得0分。伤害表现描述与使用过程中关于伤害的描述不一致的，得0分。对于“其他”未对患者造成伤害的，该项可填“无”或未填写，默认得6分。",
                            14: "描述准确而简明，或者勾选的术语贴切的，得6分；描述较为准确，或选择术语较为贴切，或描述准确但不够简洁，得3分；描述冗长、填成伤害表现的，得0分。故障表现与使用过程中关于器械故障的描述不一致的，得0分。\n注意：对于不存在器械故障但仍然对患者造成了伤害的，在伤害表现处填写了对应伤害，该项填“无”，默认得6分。",
                            15: "医疗器械若未用于患者或者未造成患者伤害的，患者信息非必填项，默认得1分。",
                            16: "医疗器械若未用于患者或者未造成患者伤害的，患者信息非必填项，默认得1分。",
                            17: "指涉及医疗器械的用途或适用范围，如治疗类医疗器械的预期治疗疾病，检验检查类、辅助治疗类医疗器械的预期作用等。填写完整准确，得4分；未填写、填写不完整或填写错误，得0分。",
                            18: "需与使用过程描述的日期一致，若器械使用日期和不良事件发生日期不是同一天，填成“不良事件发生日期”的，得0分；填成“有源设备启用日期”的，得0分。如仅知道事件使用年份，填写当年的1月1日；如仅知道年份和月份，填写当月的第1日；如年月日均未知，填写事件获知日期，并在“使用过程”给予说明。",
                            19: "使用场所为“医疗机构”的，场所名称可以为空，默认得2分；使用场所为“家庭”或“其他”，但勾选为医疗机构的，得0分；如使用场所为“其他”，没有填写实际使用场所或填写错误的，得0分。",
                            20: "按照以下四个要素进行评分：\n（1）具体操作使用情况（5分）\n详细描述具体操作人员资质、操作使用过程等信息，对于体外诊断医疗器械应填写患者诊疗信息（如疾病情况、用药情况）、样品检测过程与结果等信息。该要素描述准确完整的，得5分；较完整准确的，得2.5分；要素缺失的，得0分。\n（2）不良事件情况（5分）\n详细描述使用过程中出现的非预期结果等信息，对于体外诊断医疗器械应填写发现的异常检测情况，该要素描述完整准确的，得5分；较完整准确的，得2.5分；要素缺失的，得0分。\n（3）对受害者的影响（4分）\n详细描述该事件（可能）对患者造成的伤害，（可能）对临床诊疗造成的影响。有实际伤害的事件，需写明对受害者的伤害情况，包括必要的体征（如体温、脉搏、血压、皮损程度、失血情况等）和相关检查结果（如血小板检查结果）；对于可能造成严重伤害的事件，需写明可能对患者或其他人员造成的伤害。该要素描述完整准确的，得4分；较完整准确的，得2分；要素缺失的，得0分。\n（4）采取的治疗措施及结果（4分）\n有实际伤害的情况，须写明对伤者采取的治疗措施（包括用药、用械、或手术治疗等，及采取各个治疗的时间），以及采取治疗措施后的转归情况。该要素描述完整准确得4分，较完整准确得2分，描述过于笼统简单，如描述为“对症治疗”、“报告医生”、“转院”等，或者要素缺失的，得0分；无实际伤害的，该要素默认得4分。",
                            21: "有合并用药/械情况但没有填写此项的，得0分；填写不完整的，得2分；评估认为该不良事件过程中不存在合并用药/械情况的，该项不填写可得4分。\n如：输液泵泵速不准，合并用药/械情况应写明输注的药液、并用的输液器信息等。",
                            22: "原因分析不正确，如对于产品原因（包括说明书等）、操作原因 、患者自身原因 、无法确定的勾选与原因分析的描述的内容不匹配的，得0分，例如勾选了产品原因，但描述中说明该事件可能是未按照说明书要求进行操作导致（操作原因）；原因分析正确，但原因分析描述填成使用过程或者处置方式的，得2分。",
                            23: "包含产品的初步处置措施和对患者的救治措施等，填写完整得2分，部分完整得1分，填写过于简单得0分。",
                        },
                        "满分分值": {
                            0: 0,
                            1: 1,
                            2: 1,
                            3: 1,
                            4: 8,
                            5: 4,
                            6: 4,
                            7: 4,
                            8: 2,
                            9: 2,
                            10: 2,
                            11: 5,
                            12: 8,
                            13: 6,
                            14: 6,
                            15: 1,
                            16: 1,
                            17: 4,
                            18: 2,
                            19: 2,
                            20: 18,
                            21: 4,
                            22: 4,
                            23: 2,
                        },
                    }
                )
                text.insert(END, "\n您使用软件内置的评分标准。")
                text.see(END)

            try:
                dishi = pd.read_excel(
                    umeu, sheet_name="地市清单", header=0, index_col=0
                ).reset_index()
                text.insert(END, "\n找到地市清单，将规整地市名称。")
                for qwe in dishi["地市列表"]:
                    datams0.loc[
                        (datams0["上报单位所属地区"].str.contains(qwe, na=False)),
                        "市级监测机构",
                    ] = qwe
                    datams0.loc[
                        (datams0["上报单位所属地区"].str.contains("顺德", na=False)),
                        "市级监测机构",
                    ] = "佛山"
                    # data=data.loc[data["产品类别"].str.contains("无源|诊断", na=False)].copy()
                    
                    #为广西做一个兼容
                    datams0.loc[
                        (datams0["市级监测机构"].str.contains("北海", na=False)),
                        "市级监测机构",
                    ] = "北海"                    
                    datams0.loc[
                        (datams0["联系地址"].str.contains("北海市", na=False)),
                        "市级监测机构",
                    ] = "北海"                      
                text.see(END)
            except:
                text.insert(END, "\n未找到地市清单或清单有误，不对地市名称进行规整，未维护产品的报表的地市名称将以“未填写”的形式展现。")
                text.see(END)
        else:
            pdb = biaozhun.copy()
            if len(dishi) != 0:
                try:
                    text.insert(END, "\n找到自定义的地市清单，将规整地市名称。")
                    for qwe in dishi["地市列表"]:
                        datams0.loc[
                            (datams0["使用单位、经营企业所属监测机构"].str.contains(qwe, na=False)),
                            "市级监测机构",
                        ] = qwe
                    datams0.loc[
                        (datams0["上报单位所属地区"].str.contains("顺德", na=False)),
                        "市级监测机构",
                    ] = "佛山"
                    text.see(END)
                except TRD:
                    text.insert(
                        END,
                        "\n导入的自定义配置表中，未找到地市清单或清单有误，不对地市名称进行规整，未维护产品的报表的地市名称将以“未填写”的形式展现。",
                    )
                    text.see(END)
            text.insert(END, "\n您使用了自己导入的配置表作为评分标准。")
            text.see(END)
    text.insert(END, "\n正在抽样，请稍候...已完成30%")
    datams0 = datams0.reset_index(drop=True)

    # 对于报告时限及一些合并列的处理。
    datams0["质量评估模式"] = datams0[group_by]
    datams0["报告时限"] = ""
    datams0["报告时限情况"] = "超时报告"
    datams0["识别代码"] = range(0, len(datams0))
    try:
        datams0["报告时限"] = pd.to_datetime(datams0["报告日期"]) - pd.to_datetime(
            datams0["发现或获知日期"]
        )
        datams0["报告时限"] = datams0["报告时限"].dt.days
        datams0.loc[
            (datams0["伤害"] == "死亡") & (datams0["报告时限"] <= 7), "报告时限情况"
        ] = "死亡未超时，报告时限：" + datams0["报告时限"].astype(str)
        datams0.loc[
            (datams0["伤害"] == "严重伤害") & (datams0["报告时限"] <= 20), "报告时限情况"
        ] = "严重伤害未超时，报告时限：" + datams0["报告时限"].astype(str)
        datams0.loc[
            (datams0["伤害"] == "其他") & (datams0["报告时限"] <= 30), "报告时限情况"
        ] = "其他未超时，报告时限：" + datams0["报告时限"].astype(str)
        datams0.loc[
            (datams0["报告时限情况"] == "超时报告"), "报告时限情况"
        ] = "！疑似超时报告，报告时限：" + datams0["报告时限"].astype(str)
        datams0["型号和规格"] = (
            "型号：" + datams0["型号"].astype(str) + "   \n规格：" + datams0["规格"].astype(str)
        )
        datams0["产品批号和产品编号"] = (
            "产品批号："
            + datams0["产品批号"].astype(str)
            + "   \n产品编号："
            + datams0["产品编号"].astype(str)
        )
        datams0["使用场所和场所名称"] = (
            "使用场所："
            + datams0["使用场所"].astype(str)
            + "   \n场所名称："
            + datams0["场所名称"].astype(str)
        )
        datams0["年龄和年龄类型"] = (
            "年龄："
            + datams0["年龄"].astype(str)
            + "   \n年龄类型："
            + datams0["年龄类型"].astype(str)
        )
        datams0["事件原因分析和事件原因分析描述"] = (
            "事件原因分析："
            + datams0["事件原因分析"].astype(str)
            + "   \n事件原因分析描述："
            + datams0["事件原因分析描述"].astype(str)
        )
        
        #print("dddddddddddddddddddddddddddddddddddddddddddddddddddd")
        #兼容下持有人
        datams0["是否开展了调查及调查情况"] = (
            "是否开展了调查："
            + datams0["是否开展了调查"].astype(str)
            + "   \n调查情况："
            + datams0["调查情况"].astype(str)
        )
           
        datams0["控制措施情况"] = (
            "是否已采取控制措施："
            + datams0["是否已采取控制措施"].astype(str)
            + "   \n具体控制措施："
            + datams0["具体控制措施"].astype(str)
            + "   \n未采取控制措施原因："
            + datams0["未采取控制措施原因"].astype(str)    
        )
        
        datams0["是否为错报误报报告及错报误报说明"] = (
            "是否为错报误报报告："
            + datams0["是否为错报误报报告"].astype(str)
            + "   \n错报误报说明："
            + datams0["错报误报说明"].astype(str)
        )        

        datams0["是否合并报告及合并报告编码"] = (
            "是否合并报告："
            + datams0["是否合并报告"].astype(str)
            + "   \n合并报告编码："
            + datams0["合并报告编码"].astype(str)
        )           
    except:
        pass
    if "报告类型-新的" in datams0.columns:
        if '患者姓名' not in datams0.columns:
            datams0['患者姓名']='保密'        			
        #datams0["报告类型-新的"]=datams0["报告类型-新的"].str.replace("-未填写-","")
        datams0["报告时限"] = pd.to_datetime(datams0["报告日期"].astype(str)) - pd.to_datetime(datams0["不良反应发生时间"].astype(str))
        datams0["报告类型"] = datams0["报告类型-新的"].astype(str) +datams0["伤害"].astype(str) +"    "+datams0["严重药品不良反应"].astype(str)
        datams0["报告类型"] = datams0["报告类型"].str.replace("-未填写-","",regex=False)
        datams0["报告类型"] = datams0["报告类型"].str.replace("其他","一般",regex=False)
        datams0["报告类型"] = datams0["报告类型"].str.replace("严重伤害","严重",regex=False)                
        datams0["关联性评价和ADR分析"]= "停药减药后反应是否减轻或消失："+datams0["停药减药后反应是否减轻或消失"].astype(str)+"\n再次使用可疑药是否出现同样反应："+datams0["再次使用可疑药是否出现同样反应"].astype(str)+"\n报告人评价："+datams0["报告人评价"].astype(str)
        datams0["ADR过程描述以及处理情况"]= "不良反应发生时间："+datams0["不良反应发生时间"].astype(str)+"\n不良反应过程描述："+datams0["不良反应过程描述"].astype(str)+"\n不良反应结果:"+datams0["不良反应结果"].astype(str)+"\n对原患疾病影响:"+datams0["对原患疾病影响"].astype(str)+"\n后遗症表现："+datams0["后遗症表现"].astype(str)+"\n死亡时间:"+datams0["死亡时间"].astype(str)+"\n直接死因:"+datams0["直接死因"].astype(str)
        datams0["报告者及患者有关情况"]="患者姓名："+datams0["患者姓名"].astype(str)+"\n性别："+datams0["性别"].astype(str)+"\n出生日期:"+datams0["出生日期"].astype(str)+"\n年龄:"+datams0["年龄"].astype(str)+datams0["年龄单位"].astype(str)+"\n民族："+datams0["民族"].astype(str)+"\n体重:"+datams0["体重"].astype(str)+"\n原患疾病:"+datams0["原患疾病"].astype(str)+"\n病历号/门诊号:"+datams0["病历号/门诊号"].astype(str)+"\n既往药品不良反应/事件:"+datams0["既往药品不良反应/事件"].astype(str)+"\n家族药品不良反应/事件:"+datams0["家族药品不良反应/事件"].astype(str)


    # 选择保存的目录
    sourcePath = filedialog.askdirectory()  #!!!!!!!

    # 对于不同伤害程度，分别抽样的核心代码
    kcd = 1  # 如果是第一个
    for i in datams0["伤害"].drop_duplicates():
        if i == "其他":
            qt_j = 1
            dataqt = datams0[(datams0["伤害"] == "其他")]
            ori_qt = Tdoing(dataqt, fracn1, no, group_by, methon, yongtu)
            if kcd == 1:
                ori1 = ori_qt[0]
                kcd = kcd + 1
            else:
                ori1 = pd.concat([ori1, ori_qt[0]], axis=0)
                # print(len(ori1))
        if i == "严重伤害":
            yz_j = 1
            datayz = datams0[(datams0["伤害"] == "严重伤害")]
            ori_yz = Tdoing(datayz, fracn2, no, group_by, methon, yongtu)
            if kcd == 1:
                ori1 = ori_yz[0]
                kcd = kcd + 1
            else:
                ori1 = pd.concat([ori1, ori_yz[0]], axis=0)
                # print(len(ori1))
        if i == "死亡":
            sw_j = 1
            datasw = datams0[(datams0["伤害"] == "死亡")]
            ori_sw = Tdoing(datasw, fracn3, no, group_by, methon, yongtu)
            if kcd == 1:
                ori1 = ori_sw[0]
                kcd = kcd + 1
            else:
                ori1 = pd.concat([ori1, ori_sw[0]], axis=0)
                # print(len(ori1))

                # 对抽出来的数据进行保存。
    text.insert(END, "\n正在抽样，请稍候...已完成50%")
    writer_ori1 = pd.ExcelWriter(str(sourcePath) + "/●(最终评分需导入)被抽出的所有数据" + ".xlsx")
    ori1.to_excel(writer_ori1, sheet_name="被抽出的所有数据")
    writer_ori1.close()

    # 制作抽样情况统计表
    if yongtu == 1:
        ori_xx1 = datams0.copy()
        ori_xx1["原始数量"] = 1
        ori1_xx2 = ori1.copy()
        ori1_xx2["抽取数量"] = 1
        
        #ori_groupby = ori_xx1.groupby([group_by]).aggregate(
        #    {"原始数量": "count"}
        #)  # .reset_index()
        #ori_groupby = ori_groupby.sort_values(
        #    by=["原始数量"], ascending=False, na_position="last"
        #)
        #ori_groupby = ori_groupby.reset_index()        
        # 使用 pivot_table 进行透视，将“伤害”列的子项作为列
        ori_groupby = ori_xx1.pivot_table(
            index=group_by,  # 分组列作为索引
            columns='伤害',  # 将“伤害”列的子项作为列
            values='原始数量',  # 需要聚合的值
            aggfunc='count',  # 聚合函数为计数
            fill_value=0,  # 缺失值填充为0
            margins=True,
            dropna=False
        ).reset_index()

        ori_groupby = ori_groupby.rename(columns={"All": "原始数量"})
        # 计算总数量并排序
       # ori_groupby['原始数量'] = ori_groupby.sum(axis=1)  # 计算每一行的总数量
        ori_groupby = ori_groupby.sort_values(by='原始数量', ascending=False)  # 按总数量降序排序

        # 重置索引
        ori_groupby = ori_groupby.reset_index(drop=True)

        ori_groupby1 = pd.pivot_table(
            ori1_xx2,
            values=["抽取数量"],
            index=group_by,
            columns="伤害",
            aggfunc={"抽取数量": "count"},
            fill_value="0",
            margins=True,
            dropna=False,
        )  # .reset_index()
        ori_groupby1.columns = ori_groupby1.columns.droplevel(0)

        ori_groupby1 = ori_groupby1.sort_values(
            by=["All"], ascending=[False], na_position="last"
        )
        ori_groupby1 = ori_groupby1.reset_index()
        ori_groupby1 = ori_groupby1.rename(columns={"All": "抽取总数量"})
        try:
            ori_groupby1 = ori_groupby1.rename(columns={"其他": "抽取数量(其他)"})
        except:
            pass
        try:
            ori_groupby1 = ori_groupby1.rename(columns={"一般": "抽取数量(一般)"})
        except:
            pass
        try:
            ori_groupby1 = ori_groupby1.rename(columns={"严重伤害": "抽取数量(严重)"})
        except:
            pass
        try:
            ori_groupby1 = ori_groupby1.rename(columns={"死亡": "抽取数量-死亡"})
        except:
            pass
        df_empty = pd.merge(ori_groupby, ori_groupby1, on=[group_by], how="left")
        df_empty["抽取比例"] = round(df_empty["抽取总数量"] / df_empty["原始数量"], 2)
        writer_df_empty = pd.ExcelWriter(str(sourcePath) + "/抽样情况分布" + ".xlsx")
        df_empty.to_excel(writer_df_empty, sheet_name="抽样情况分布")
        writer_df_empty.close()

        # 对抽样结果进行专家分组
    #Ttree_Level_2(ori1, 1, ori1)
    #print(ori1["伤害"])
       
    ori1 = ori1[pdb["评分项"].tolist()]
    
    n = int(no)
    ###
    text.insert(END, "\n正在抽样，请稍候...已完成70%")
    for i in range(n):
        if i == 0:

            zhuanjia_qt = ori1[(ori1["伤害"] == "其他")].sample(
                frac=1 / (n - i), replace=False
            )
            zhuanjia_yz = ori1[(ori1["伤害"] == "严重伤害")].sample(
                frac=1 / (n - i), replace=False
            )
            zhuanjia_sw = ori1[(ori1["伤害"] == "死亡")].sample(
                frac=1 / (n - i), replace=False
            )

            zhuanjia = pd.concat([zhuanjia_qt, zhuanjia_yz, zhuanjia_sw], axis=0)

        else:
            ori1 = pd.concat([ori1, zhuanjia], axis=0)
            ori1.drop_duplicates(subset=["识别代码"], keep=False, inplace=True)
            zhuanjia_qt = ori1[(ori1["伤害"] == "其他")].sample(
                frac=1 / (n - i), replace=False
            )
            zhuanjia_yz = ori1[(ori1["伤害"] == "严重伤害")].sample(
                frac=1 / (n - i), replace=False
            )
            zhuanjia_sw = ori1[(ori1["伤害"] == "死亡")].sample(
                frac=1 / (n - i), replace=False
            )
            zhuanjia = pd.concat([zhuanjia_qt, zhuanjia_yz, zhuanjia_sw], axis=0)
        try:
            zhuanjia["报告编码"] = zhuanjia["报告编码"].astype(str)
        except:
            pass
        name = str(sourcePath) + "/" + str(i + 1) + ".xlsx"

        # 制作专家打分文件，并保存
        if yongtu == 1:
            zhuanjia2 = TeasyreadT(zhuanjia.copy())
            del zhuanjia2["逐条查看"]
            zhuanjia2["评分"] = ""
            if len(zhuanjia2) > 0:
                for ids, cols in pdb.iterrows():
                    zhuanjia2.loc[(zhuanjia2["条目"] == cols["评分项"]), "满分"] = cols["满分分值"]
                    zhuanjia2.loc[(zhuanjia2["条目"] == cols["评分项"]), "打分标准"] = cols[
                        "打分标准"
                    ]

            zhuanjia2["专家序号"] = i + 1
            name2 = str(sourcePath) + "/" + "●专家评分表" + str(i + 1) + ".xlsx"
            writer2 = pd.ExcelWriter(name2)
            zhuanjia2.to_excel(writer2, sheet_name="字典数据")
            writer2.close()

            # 工作结束，提示一些信息
    text.insert(END, "\n正在抽样，请稍候...已完成100%")
    showinfo(title="提示信息", message="抽样和分组成功，请查看以下文件夹：" + str(sourcePath))
    text.insert(END, "\n抽样和分组成功，请查看以下文件夹：" + str(sourcePath))
    text.insert(END, "\n抽样概况:\n")
    text.insert(END, df_empty[[group_by, "原始数量", "抽取总数量"]])
    text.see(END)


def Tdoing(datams, fracn, no, group_by, methon, yongtu):
    """随机抽样的核心代码，份最大覆盖和总体随机两种情况，实际上总体随机这种模式已被隐藏，但保留了代码"""

    def get_ori1(datax, fracn, methon):
        if float(fracn) > 1:
            try:
                datax1 = datax.sample(int(fracn), replace=False)
            # 添加最小保证
            except ValueError:
                # showinfo(title="提示信息", message="因为设置的抽样数量大于样本数量，所以全部抽样。")
                datax1 = datax
        else:
            datax1 = datax.sample(frac=float(fracn), replace=False)
            # 添加最小保证
            if len(datax) * float(fracn) > len(datax1) and methon == "最大覆盖":
                datax22 = pd.concat([datax, datax1], axis=0)
                datax22.drop_duplicates(subset=["识别代码"], keep=False, inplace=True)
                datax23 = datax22.sample(1, replace=False)
                datax1 = pd.concat([datax1, datax23], axis=0)
        return datax1

    # 实际上总体随机这种模式已被隐藏，但保留了代码
    if methon == "总体随机":
        ori1 = get_ori1(datams, fracn, methon)
        #print(len(ori1))
    else:
        kc = 1
        for k in datams[group_by].drop_duplicates():
            ori_temp = datams[(datams[group_by] == k)].copy()  # .reset_index(drop=True)
            if kc == 1:
                ori1 = get_ori1(ori_temp, fracn, methon)
                kc = kc + 1
            else:
                roi2 = get_ori1(ori_temp, fracn, methon)
                ori1 = pd.concat([ori1, roi2])  # , ignore_index=True)
    ori1 = ori1.drop_duplicates()
    return ori1, 1


def Tpinggu():
    """报告表质量评估合并及打分计算"""
    allfilex = Topentable(1)  # 导入专家评分表和抽样表

    data = allfilex[0]  # 合并后的专家评分表
    allfileName = allfilex[1]  # 抽样表的位置

    # 读取抽样表，实际只有一个文件
    try:
        # allfileName = filedialog.askopenfilenames( filetypes=[("XLS", ".xls"), ("XLSX", ".xlsx")]  )
        k = [
            pd.read_excel(x, header=0, sheet_name=0) for x in allfileName
        ]  # ,index_col=0
        alldata = pd.concat(k, ignore_index=True).drop_duplicates()
        try:
            alldata = alldata.loc[:, ~alldata.columns.str.contains("^Unnamed")]
        except:
            pass
    except:
        showinfo(title="提示信息", message="载入文件出错，任务终止。")
        return 0

    # 校验下专家评分表是否正确生成
    try:
        data = data.reset_index()
    except:
        showinfo(title="提示信息", message="专家评分文件存在错误，程序中止。")
        return 0

    alldata["质量评估专用表"] = ""

    # 在抽样表生成打分列，之后依次读取打分表各行，根据序号把分数添加上去。
    text.insert(END, "\n打分表导入成功，正在统计，请耐心等待...")
    text.insert(END, "\n正在计算总分，请稍候，已完成20%")
    text.see(END)
    
    #增加校验表
    datacheck=data[["序号","条目","详细描述","评分","满分","打分标准","专家序号"]].copy() #增加一个表格，声明评估对象的，方便核对打分。
    alldatacheck=alldata[["质量评估模式","识别代码"]].copy()
    datacheck.reset_index(inplace=True)
    alldatacheck.reset_index(inplace=True)    
    alldatacheck = alldatacheck.rename(columns={"识别代码": "序号"})
    datacheck=pd.merge(datacheck, alldatacheck, on=["序号"])
    datacheck=datacheck.sort_values(by=["序号","条目"], ascending=True, na_position="last")
    datacheck=datacheck[["质量评估模式","序号","条目","详细描述","评分","满分","打分标准","专家序号"]]
    
    for ids, cols in data.iterrows():
        lieming = "专家打分-" + str(cols["条目"])
        alldata.loc[(alldata["识别代码"] == cols["序号"]), lieming] = cols["评分"]
    del alldata["专家打分-识别代码"]
    del alldata["专家打分-#####分隔符#########"]
    try:
        alldata = alldata.loc[:, ~alldata.columns.str.contains("^Unnamed")]
    except:
        pass
    text.insert(END, "\n正在计算总分，请稍候，已完成60%")
    text.see(END)

    # 定义好工作目录
    sourcePath = allfileName[0]
    try:
        ddename = str(sourcePath).replace("●(最终评分需导入)被抽出的所有数据.xls", "")
    except:
        ddename = str(sourcePath)

    # 保存下抽样表+打分表的合并文件，但是这里不需要了。
    # writer_alldata = pd.ExcelWriter(str(ddename)+"汇总打分的原始文件"+".xlsx")
    # alldata.to_excel(writer_alldata, sheet_name="原始打分")
    # writer_alldata.close()

    # 保存下抽样表+打分表的合并文件，但是这里不需要了。
    writer_datacheck = pd.ExcelWriter(str(ddename)+"各评估对象打分核对文件"+".xlsx")
    datacheck.to_excel(writer_datacheck, sheet_name="原始打分")
    writer_datacheck.close()
    

    # 开展统计打分工作，并保存工作结果。
    dafen = Tpinggu2(alldata)

    text.insert(END, "\n正在计算总分，请稍候，已完成100%")
    text.see(END)
    showinfo(title="提示信息", message="打分计算成功，请查看文件：" + str(ddename) + "最终打分" + ".xlsx")
    text.insert(END, "\n打分计算成功，请查看文件：" + str(sourcePath) + "最终打分" + ".xls\n")
    dafen.reset_index(inplace=True)
    text.insert(END, "\n以下是结果概况：\n")
    text.insert(END, dafen[["评估对象", "总分"]])
    text.see(END)
    
 
    
    ms = ["评估对象", "总分"]
    for ii in dafen.columns:
        if "专家打分" in ii:
            ms.append(ii)
    dafen2 = dafen[ms]
    
    biaozhun = pd.read_excel(
        peizhidir+"pinggu_质量评估.xls", sheet_name=0, header=0, index_col=0
    ).reset_index()
    #print(ms)
    if "专家打分-不良反应名称" in ms:    
        biaozhun = pd.read_excel(peizhidir+"pinggu_质量评估.xls", sheet_name="药品", header=0, index_col=0).reset_index()    
        #print(biaozhun)
    if "专家打分-化妆品名称" in ms:    
        biaozhun = pd.read_excel(peizhidir+"pinggu_质量评估.xls", sheet_name="化妆品", header=0, index_col=0).reset_index()    
    if "专家打分-是否需要开展产品风险评价" in ms:    
        biaozhun = pd.read_excel(peizhidir+"pinggu_质量评估.xls", sheet_name="器械持有人", header=0, index_col=0).reset_index()          
    for ids, cols in biaozhun.iterrows():
        newname = "专家打分-" + str(cols["评分项"])
        try:
            warnings.filterwarnings('ignore')
            dafen2.loc[-1, newname] = cols["满分分值"]
        except:
            pass
    del dafen2["专家打分-识别代码"]
    dafen2.iloc[-1, 0] = "满分分值"
    dafen2.loc[-1, "总分"] = 100
    
    if "专家打分-事件原因分析.1" not in ms:
        dafen2.loc[-1, "专家打分-报告时限"] = 5
    #对持有人做一个兼容
    if "专家打分-事件原因分析.1" in ms:
        dafen2.loc[-1, "专家打分-报告时限"] = 10		
    
 
    dafen2.columns = dafen2.columns.str.replace("专家打分-", "",regex=False)
    #print(ms)
    if ("专家打分-器械故障表现" in ms)  and ("modex" not in alldata.columns): 
        dafen2.loc[-1, "姓名和既往病史"] = 2
        dafen2.loc[-1, "报告日期"] = 1        		
    else:
        del dafen2["伤害"]
        
    if "专家打分-化妆品名称" in ms:          
        del  dafen2["报告时限"]
        
    #内置几个排序
    try:
        dafen2=dafen2[["评估对象","总分","伤害.1","是否开展了调查及调查情况","关联性评价","事件原因分析.1","是否需要开展产品风险评价","控制措施情况","是否为错报误报报告及错报误报说明","是否合并报告及合并报告编码","报告时限"]]    
    except:
        pass 
    try:
        dafen2=dafen2[["评估对象","总分","报告日期","报告人","联系人","联系电话","注册证编号/曾用注册证编号","产品名称","型号和规格","产品批号和产品编号","生产日期","有效期至","事件发生日期","发现或获知日期","伤害","伤害表现","器械故障表现","姓名和既往病史","年龄和年龄类型","性别","预期治疗疾病或作用","器械使用日期","使用场所和场所名称","使用过程","合并用药/械情况说明","事件原因分析和事件原因分析描述","初步处置情况","报告时限"]]    
    except:
        pass         
    try:
        dafen2=dafen2[["评估对象","总分","报告类型","报告时限","报告者及患者有关情况","原患疾病","药品信息","不良反应名称","ADR过程描述以及处理情况","关联性评价和ADR分析"]]    
    except:
        pass 
    namesss=str(ddename) + "最终打分" + ".xlsx"           
    writer_dafen = pd.ExcelWriter(namesss)
    dafen2.to_excel(writer_dafen, sheet_name="最终打分")
    writer_dafen.close()

    try:
        pcsdd=pd.read_excel(namesss.replace('x最终打分.xlsx',"抽样情况分布.xlsx"),sheet_name=0,header=0,index_col=0,).reset_index(drop=True)
        dafen33=pd.merge(dafen2,pcsdd,left_on='评估对象',right_on=pcsdd.columns[0],how='left')
        writer_dafen33 = pd.ExcelWriter(str(ddename) + "抽样情况和最终打分" + ".xlsx" )

        dafen33.to_excel(writer_dafen33, sheet_name="抽样和最终打分")
        writer_dafen33.close()
    except www:
        pass

    Ttree_Level_2(dafen2, 0, dafen)  # .reset_index(drop=True)


def Tpinggu2(data):
    """报告表质打分计算核心文件"""
    data["报告数量小计"] = 1

    # 对报告时限、姓名、既往病史、报告日期等自动评分项进行处理
    if ("器械故障表现" in  data.columns) and ("modex" not in data.columns):
        data["专家打分-姓名和既往病史"] = 2
        data["专家打分-报告日期"] = 1
        if "专家打分-报告时限情况" not in data.columns:
            data["报告时限"] = data["报告时限"].astype(float)
            data["专家打分-报告时限"] = 0
            data.loc[(data["伤害"] == "死亡") & (data["报告时限"] <= 7), "专家打分-报告时限"] = 5
            data.loc[(data["伤害"] == "严重伤害") & (data["报告时限"] <= 20), "专家打分-报告时限"] = 5
            data.loc[(data["伤害"] == "其他") & (data["报告时限"] <= 30), "专家打分-报告时限"] = 5


    #对持有人做一个兼容
    if "专家打分-事件原因分析.1"  in data.columns:
       data["专家打分-报告时限"] = 10   
    
    # 构建要计算的列
    k = []
    for i in data.columns:
        if "专家打分-" in i:
            k.append(i)

    #print(k)
    # 对各计算列进行透视计算，最后通过评估对象列来进行拼接合并。
    x = 1
    for i in k:
        result = data.groupby(["质量评估模式"]).aggregate({i: "sum"}).reset_index()
        if x == 1:
            result_all = result
            x = x + 1
        else:
            result_all = pd.merge(result_all, result, on="质量评估模式", how="left")
            # print(result_all)
    result2 = data.groupby(["质量评估模式"]).aggregate({"报告数量小计": "sum"}).reset_index()
    result_all = pd.merge(result_all, result2, on="质量评估模式", how="left")

    # 计算总分和平均分
    for i in k:
        result_all[i] = round(result_all[i] / result_all["报告数量小计"], 2)
    result_all["总分"] = round(result_all[k].sum(axis=1), 2)
    result_all = result_all.sort_values(by=["总分"], ascending=False, na_position="last")
    print(result_all)
    warnings.filterwarnings('ignore')
    result_all.loc["平均分(非加权)"] = round(result_all.mean(axis=0,numeric_only=True), 2)
    result_all.loc["标准差(非加权)"] = round(result_all.std(axis=0,numeric_only=True), 2)
    result_all = result_all.rename(columns={"质量评估模式": "评估对象"})
    result_all.iloc[-2, 0] = "平均分(非加权)"
    result_all.iloc[-1, 0] = "标准差(非加权)"
    #print(result_all.columns)
    return result_all


def Ttree_Level_2(input_ori, methon, ori, *selection):  # methon=0表示原始报表那个层级，其他就使用传入文件。
    """-报表查看器"""
    ##########预处理模块：判断属于哪个层级和根据条件筛选报表#################
    columns_list_ori = input_ori.columns.values.tolist()
    methon = 0
    ori_owercount_easyread = input_ori.loc[:]

    ##########报表查看器模块#################
    treeQ = Toplevel()
    treeQ.title("报表查看器")
    sw_treeQ = treeQ.winfo_screenwidth()
    # 得到屏幕宽度
    sh_treeQ = treeQ.winfo_screenheight()
    # 得到屏幕高度
    ww_treeQ = 1300
    wh_treeQ = 600
    # 窗口宽高为100
    x_treeQ = (sw_treeQ - ww_treeQ) / 2
    y_treeQ = (sh_treeQ - wh_treeQ) / 2
    treeQ.geometry("%dx%d+%d+%d" % (ww_treeQ, wh_treeQ, x_treeQ, y_treeQ))
    frame = ttk.Frame(treeQ, width=1300, height=20)
    frame.pack(side=TOP)

    # 以下是在treeview上显示整个表格 ，并调节特定列的间距！！！！！！！！！！！！！！！！！！！！
    bookList = ori_owercount_easyread.values.tolist()
    columns_list = ori_owercount_easyread.columns.values.tolist()
    tree = ttk.Treeview(frame, columns=columns_list, show="headings", height=45)

    for i in columns_list:
        tree.heading(i, text=i)
    for item in bookList:
        tree.insert("", "end", values=item)
    for b in columns_list:
        tree.column(b, minwidth=0, width=120, stretch=NO)

    yscrollbar = Scrollbar(frame, orient="vertical")  # horizontal
    yscrollbar.pack(side=RIGHT, fill=Y)
    yscrollbar.config(command=tree.yview)
    tree.config(yscrollcommand=yscrollbar.set)

    xscrollbar = Scrollbar(frame, orient="horizontal")  # horizontal
    xscrollbar.pack(side=BOTTOM, fill=X)
    xscrollbar.config(command=tree.xview)
    tree.config(yscrollcommand=yscrollbar.set)

    def trefun_1(event, columns_list, ori_owercount_easyread):
        # del owercount_easyread["评估对象"]

        for item in tree.selection():
            selection = tree.item(item, "values")

        y = selection[2:]  # [x for x in selection][2:]
        y1 = ori_owercount_easyread.iloc[-1, :][
            2:
        ]  # [x for x in ori_owercount_easyread.iloc[-1, :]][2:]
        index = ori_owercount_easyread.columns  # .tolist()
        index = index[2:]

        Tpo(y1, y, index, "失分", "得分", selection[0])
        return 0

    # 以下是排序功能：
    tree.bind(
        "<Double-1>",
        lambda event: trefun_1(event, columns_list, ori_owercount_easyread),
    )

    def treeview_sort_column(tv, col, reverse):  # Treeview、列名、排列方式
        l = [(tv.set(k, col), k) for k in tv.get_children("")]
        l.sort(reverse=reverse)  # 排序方式
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):  # 根据排序后索引移动
            tv.move(k, "", index)
        tv.heading(
            col, command=lambda: treeview_sort_column(tv, col, not reverse)
        )  # 重写标题，使之成为再点倒序的标题

    for col in columns_list:  # 给所有标题加
        tree.heading(
            col,
            text=col,
            command=lambda _col=col: treeview_sort_column(tree, _col, False),
        )

    tree.pack()

def Txuanze():
    """-筛选数据专用"""
    global ori
    listx = pd.read_excel(peizhidir+"0（范例）批量筛选.xls",sheet_name=0,header=0,index_col=0,).reset_index()
    text.insert(END,"\n正在执行内部数据规整...\n")
    text.insert(END,listx)
    ori["temppr"]=""
    for x in listx.columns.tolist():
        ori["temppr"]=ori["temppr"]+"----"+ori[x]
    namex2 = "测试字段MMMMM"
    for x in listx.columns.tolist():		
        for i in listx[x].drop_duplicates():
            if i:
                namex2 = namex2 + "|" + str(i)
    ori = ori.loc[ori["temppr"].str.contains(namex2, na=False)].copy()
    del  ori["temppr"]     # 包括的
    
    ori=ori.reset_index(drop=True)
    text.insert(END,"\n内部数据规整完毕。\n")
    
    
def Tpo(y, y1, index, yL, y1L, title):  # y=大数，y1=小数，index=横坐标标签,yL y的图例标签
    """绘制堆叠柱状图通用文件"""
    y = y.astype(float)
    y1 = tuple(float(i) for i in y1)
    view_pic = Toplevel()
    view_pic.title(title)
    frame0 = ttk.Frame(view_pic, height=20)  # , width = 1200,
    frame0.pack(side=TOP)
    # 柱子的宽度
    width = 0.2
    drawPic_f = Figure(figsize=(12, 6), dpi=100)  # fast100
    drawPic_canvas = FigureCanvasTkAgg(drawPic_f, master=view_pic)
    drawPic_canvas.draw()
    drawPic_canvas.get_tk_widget().pack(expand=1)  # grid(row=0, column=0)
    drawPic_a = drawPic_f.add_subplot(111)
    # 解决汉字乱码问题
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 使用指定的汉字字体类型（此处为黑体）
    # 创建工具条
    toolbar = NavigationToolbar2Tk(drawPic_canvas, view_pic)
    toolbar.update()
    # 显示工具条
    drawPic_canvas.get_tk_widget().pack()
    x = range(0, len(index), 1)
    # x=np.arange(len(index))
    
    drawPic_a.set_xticklabels(index, rotation=-90, fontsize=8)
   

    # drawPic_a.set_yticklabels([0,1,2,3,4,5,6,7,8], fontsize=8)
    drawPic_a.bar(x, y, align="center", tick_label=index, label=yL)
    drawPic_a.bar(x, y1, align="center", label=y1L)
    drawPic_a.set_title(title)
    drawPic_a.set_xlabel("项")
    drawPic_a.set_ylabel("数量")

    # drawPic_a.set_yticklabels([0,1,2,3,4,5,6,7,8], fontsize=8)
    drawPic_f.tight_layout(pad=0.4, w_pad=3.0, h_pad=3.0)
    box1 = drawPic_a.get_position()
    drawPic_a.set_position([box1.x0, box1.y0, box1.width * 0.7, box1.height])
    drawPic_a.legend(loc=2, bbox_to_anchor=(1.05, 1.0), fontsize=10, borderaxespad=0.0)

    drawPic_canvas.draw()


def helper():
    """-程序使用帮助"""
    helper = Toplevel()
    helper.title("程序使用帮助")
    helper.geometry("700x500")

    yscrollbar = Scrollbar(helper)
    text_helper = Text(helper, height=80, width=150, bg="#FFFFFF", font="微软雅黑")
    yscrollbar.pack(side=RIGHT, fill=Y)
    text_helper.pack()
    yscrollbar.config(command=text_helper.yview)
    text_helper.config(yscrollcommand=yscrollbar.set)
    # text_helper.insert(END,"\n\n")
    text_helper.insert(
        END,
"\n                                             帮助文件\n\n\n为帮助用户快速熟悉“阅易评”使用方法，现以医疗器械不良事件报告表为例，对使用步骤作以下说明：\n\n第一步：原始数据准备\n用户登录国家医疗器械不良事件监测信息系统（https://maers.adrs.org.cn/），在“个例不良事件管理—报告浏览”页面，选择本次评估的报告范围（时间、报告状态、事发地监测机构等）后进行查询和导出。\n●注意：国家医疗器械不良事件监测信息系统设置每次导出数据上限为5000份报告，如查询发现需导出报告数量超限，需分次导出；如导出数据为压缩包，需先行解压。如原始数据在多个文件夹内，需先行整理到统一文件夹中，方便下一步操作。\n\n第二步：原始数据导入\n用户点击“导入原始数据”按钮，在弹出数据导入框中找到原始数据存储位置，本程序支持导入多个原始数据文件，可在长按键盘“Ctrl”按键的同时分别点击相关文件，选择完毕后点击“打开”按钮，程序会提示“数据读取成功”或“导入文件错误”。\n●注意：基于当前评估工作需要，仅针对使用单位报告进行评估，故导入数据时仅选择“使用单位、经营企业医疗器械不良事件报告”，不支持与“上市许可持有人医疗器械不良事件报告”混选。如提示“导入文件错误，请重试”，请重启程序并重新操作，如仍提示错误可与开发者联系（联系方式见文末）。\n\n第三步：报告抽样分组\n用户点击“随机抽样分组”按钮，在“随机抽样及随机分组”弹窗中：\n1、根据评估目的，在“评估对象”处勾选相应选项，可根据选项对上报单位（医疗机构）、县（区）、地市实施评估。注意：如果您是省级用户，被评估对象是各地市，您要关闭本软件，修改好配置表文件夹“pinggu_质量评估.xls”中的“地市列表”单元表，将本省地市参照范例填好再运行本软件。如果被评估对象不是选择“地市”，则无需该项操作。\n2、根据报告伤害类型依次输入需抽取的比例或报告数量。程序默认此处输入数值小于1（含1）为抽取比例，输入数值大于1为抽取报告数量，用户根据实际情况任选一种方式即可。本程序支持不同伤害类型报告选用不同抽样方式。\n3、根据参与评估专家数量，在“抽样后随机分组数”输入对应数字。\n4、抽样方法有2种，一种是最大覆盖，即对每个评估对象按抽样数量/比例进行单独抽样，如遇到不足则多抽（所以总体实际抽样数量可能会比设置的多一点），每个评估对象都会被抽到；另外一种是总体随机，即按照设定的参数从总体中随机抽取（有可能部分评估对象没有被抽到）。\n用户在确定抽样分组内容全部正确录入后，点击“最大覆盖”或者“总体随机”按钮，根据程序提示选择保存地址。程序将按照专家数量将抽取的报告进行随即分配，生成对应份数的“专家评分表”，专家评分表包含评分项、详细描述、评分、满分、打分标准等。专家评分表自动隐藏报告单位等信息，用户可随机将评分表派发给专家进行评分。\n●注意：为保护数据同时便于专家查看，需对专家评分表进行格式设置，具体操作如下（或者直接使用格式刷一键完成，模板详见配置表-专家模板）：全选表格，右键-设置单元格格式-对齐，勾选自动换行，之后设置好列间距。此外，请勿修改“专家评分表“和“（最终评分需导入）被抽出的所有数据”两类工作文件的文件名。\n\n第四步：评估得分统计\n用户在全部专家完成评分后，将所有专家评分表放置在同一文件夹中，点击“评估得分统计”按钮，全选所有专家评分表和“（最终评分需导入）被抽出的所有数据”这个文件，后点击“打开”，程序将首先进行评分内容校验，对于打分错误报告给与提示并生成错误定位文件，需根据提示修正错误再全部导入。如打分项无误，程序将提示“打分表导入成功，正在统计请耐心等待”，并生成最终的评分结果。\n\n本程序由广东省药品不良反应监测中心和佛山市药品不良反应监测中心共同制作，其他贡献单位包括广州市药品不良反应监测中心、深圳市药物警戒和风险管理研究院等。如有疑问，请联系我们：\n评估标准相关问题：广东省药品不良反应监测中心 张博涵 020-37886057\n程序运行相关问题：佛山市药品不良反应监测中心 蔡权周 0757-82580815 \n\n",    )

    text_helper.config(state=DISABLED)


def TeasyreadT(bos):  # 查看表格
    """行列互换查看表格"""
    bos[
        "#####分隔符#########"
    ] = "######################################################################"
    bos2 = bos.stack(dropna=False)
    bos2 = pd.DataFrame(bos2).reset_index()
    bos2.columns = ["序号", "条目", "详细描述"]
    bos2["逐条查看"] = "逐条查看"
    return bos2




def Tget_list(ori_list):
    """将字符串转化为列表，返回一个经过整理的列表，get_list0的精简版，这个函数实际没有使用，为后面升级功能做准备"""
    ori_list = str(ori_list)
    uselist_key = []
    uselist_key.append(ori_list)
    uselist_key = ",".join(uselist_key)
    uselist_key = uselist_key.split(",")
    uselist_key = ",".join(uselist_key)
    uselist_key = uselist_key.split("，")
    uselist_temp = uselist_key[:]
    uselist_key = list(set(uselist_key))
    uselist_key.sort(key=uselist_temp.index)
    return uselist_key
    
    
def thread_it(func, *args):
    """将函数打包进线程"""
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()


def showWelcome():  # 100100
    """欢迎屏幕"""
    sw = roox.winfo_screenwidth()
    # 得到屏幕宽度
    sh = roox.winfo_screenheight()
    # 得到屏幕高度
    roox.overrideredirect(True)
    roox.attributes("-alpha", 1)  # 窗口透明度（1为不透明，0为全透明）
    x = (sw - 475) / 2
    y = (sh - 200) / 2
    # 设置窗口位于屏幕中部
    roox.geometry("675x140+%d+%d" % (x, y))
    roox["bg"] = "royalblue"
    lb_welcometext = Label(
        roox, text="阅易评", fg="white", bg="royalblue", font=("微软雅黑", 35)
    )
    lb_welcometext.place(x=0, y=15, width=675, height=90)
    lb_welcometext2 = Label(
        roox,
        text="                         广东省药品不良反应监测中心                 V"+version_now,
        fg="white",
        bg="cornflowerblue",
        font=("微软雅黑", 15),
    )
    lb_welcometext2.place(x=0, y=90, width=675, height=50)


def closeWelcome():
    """欢迎屏幕:设置欢迎页停留时间"""
    for i in range(2):
        root.attributes("-alpha", 0)  # 窗口透明度
        time.sleep(1)
    root.attributes("-alpha", 1)  # 窗口透明度
    roox.destroy()


#####第三部分：主界面 ########################################################################
root = Tk()
root.title("阅易评 YYP_"+version_now)
try:
    root.iconphoto(True, PhotoImage(file=peizhidir+"0（范例）ico.png"))
except:
    pass
sw_root = root.winfo_screenwidth()
# 得到屏幕宽度
sh_root = root.winfo_screenheight()
# 得到屏幕高度
ww_root = 700
wh_root = 620
# 窗口宽高为100
x_root = (sw_root - ww_root) / 2
y_root = (sh_root - wh_root) / 2
root.geometry("%dx%d+%d+%d" % (ww_root, wh_root, x_root, y_root))
root.configure(bg="steelblue")  # royalblue

# 窗口按钮
try:
    frame0 = ttk.Frame(root, width=100, height=20)
    frame0.pack(side=LEFT)

    B_open_files1 = Button(
        frame0,
        text="导入原始数据",
        bg="steelblue",
        fg="snow",
        height=2,
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Topentable, 0),
    )
    B_open_files1.pack()  # floralwhite

    B_open_files3 = Button(
        frame0,
        text="随机抽样分组",
        bg="steelblue",
        height=2,
        fg="snow",
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Tchouyang, ori),
    )
    B_open_files3.pack()

    B_open_files3 = Button(
        frame0,
        text="评估得分统计",
        bg="steelblue",
        fg="snow",
        height=2,
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Tpinggu),
    )
    B_open_files3.pack()

    B_open_files3 = Button(
        frame0,
        text="查看帮助文件",
        bg="steelblue",
        fg="snow",
        height=2,
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(helper),
    )
    B_open_files3.pack()
    B_open_files1 = Button(
        frame0,
        text="更改评分标准",
        bg="steelblue",
        fg="snow",
        height=2,
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Topentable, 123),
    )
    #B_open_files1.pack()  # floralwhite
    
    B_open_files1 = Button(
        frame0,
        text="内置数据清洗",
        bg="steelblue",
        fg="snow",
        height=2,
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Txuanze),
    )
    if usergroup=="用户组=1":
        B_open_files1.pack()  # floralwhite

    B_open_files1 = Button(
        frame0,
        text="更改用户分组",
        bg="steelblue",
        fg="snow",
        height=2,
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(display_random_number))  
    #if usergroup=="用户组=0":
    #    B_open_files1.pack()  # floralwhite        
        
except:
    pass


# 文本框
text = ScrolledText(root, height=400, width=400, bg="#FFFFFF", font="微软雅黑")
text.pack()  # (padx=5, pady=5)

text.insert(
    END,
    "\n    欢迎使用“阅易评”，本程序由广东省药品不良反应监测中心联合佛山市药品不良反应监测中心开发，主要功能包括：\n    1、根据报告伤害类型和用户自定义抽样比例对报告表随机抽样；\n    2、根据评估专家数量对抽出报告表随机分组，生成专家评分表；\n    3、根据专家最终评分实现自动汇总统计。\n    本程序供各监测机构免费使用，使用前请先查看帮助文件。\n  \n版本功能更新日志：\n2022年6月1日  支持医疗器械不良事件报告表质量评估(上报部分)。\n2022年10月31日  支持药品不良反应报告表质量评估。  \n2023年4月6日  支持化妆品不良反应报告表质量评估。\n2023年6月9日  支持医疗器械不良事件报告表质量评估(调查评价部分)。\n\n缺陷修正：20230609 修正结果列排序（按评分项目排序）。\n\n缺陷修正：20240329 兼容药品国家系统的新格式。\n\n注：化妆品质量评估仅支持第一怀疑化妆品。",
)
text.insert(END, "\n\n")




#序列好验证、配置表生成与自动更新。
setting_cfg=read_setting_cfg()
generate_random_file()
setting_cfg=open_setting_cfg()
if setting_cfg["settingdir"]==0:
    showinfo(title="提示", message="未发现默认配置文件夹，请选择一个。如该配置文件夹中并无配置文件，将生成默认配置文件。")
    filepathu=filedialog.askdirectory()
    filepathu=os.path.normpath(filepathu)
    path=get_directory_path(filepathu)

    update_setting_cfg("settingdir",path)    	
setting_cfg=open_setting_cfg()
random_number=int(setting_cfg["sidori"])
input_number=int(str(setting_cfg["sidfinal"])[0:6])
day_end=convert_and_compare_dates(str(setting_cfg["sidfinal"])[6:14])
sid=random_number*2+183576
if input_number == sid  and day_end=="未过期":
    usergroup="用户组=1" 
    text.insert(END,usergroup+"   有效期至：")
    text.insert(END,datetime.strptime(str(int(int(str(setting_cfg["sidfinal"])[6:14])/4)), "%Y%m%d") )
else:
    text.insert(END,usergroup)	
text.insert(END,"\n配置文件路径："+setting_cfg["settingdir"]+"\n")
peizhidir=str(setting_cfg["settingdir"])
peizhidir=os.path.join(peizhidir, 'fspsssdfpy')
peizhidir=peizhidir.replace("fspsssdfpy",'')
# 启动界面
#roox = Toplevel()
#tMain = threading.Thread(target=showWelcome)
#tMain.start()
#t1 = threading.Thread(target=closeWelcome)
#t1.start()
#root.lift()
#root.attributes("-topmost", True)
#root.attributes("-topmost", False)
root.mainloop()
