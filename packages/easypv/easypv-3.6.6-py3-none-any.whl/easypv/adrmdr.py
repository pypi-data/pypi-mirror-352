#!/usr/bin/env python
# coding: utf-8

# 第一部分：程序说明###################################################################################
# coding=utf-8
# 药械不良事件工作平台
# 开发人：蔡权周

# 第二部分：导入基本模块及初始化 ########################################################################
 
import tkinter as Tk
import os
import traceback
import ast
import re
import xlrd
import xlwt
import openpyxl
import pandas as pd
import numpy as np
import math
import scipy.stats as st
from tkinter import ttk,Menu,Frame,Canvas,StringVar,LEFT,RIGHT,TOP,BOTTOM,BOTH,Y,X,YES,NO,DISABLED,END,Button,LabelFrame,GROOVE, Toplevel,Label,Entry,Scrollbar,Text, filedialog, dialog, PhotoImage
import tkinter.font as tkFont
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import collections
from collections import Counter
import datetime
from datetime import datetime, timedelta
import xlsxwriter
import time
import threading
import warnings
from matplotlib.ticker import PercentFormatter
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy import text as sqltext
import random
import requests
import webbrowser
#from easypv import run_apps
# 定义一些全局变量




global ori
ori = 0
global auto_guize

#供质量评估用的全局变量
global biaozhun #导入自定义的评分标准储存
global dishi    #地市列表
biaozhun=""     #用于标准的判断，如果长度为0则使用内置标准
dishi=""


#定义一个专用字典
global ini
ini={}
ini["四个品种"]=1#=1则为课题服务



global version_now
global usergroup
global setting_cfg
global csdir
global peizhidir
version_now="1.0.2" 
usergroup="用户组=0"
setting_cfg=""
csdir =str (os .path .abspath (__file__ )).replace (str (__file__ ),"")
if csdir=="":
    csdir =str (os .path .dirname (__file__ ))#
    csdir =csdir +csdir.split ("easypv")[0 ][-1 ]#
#print(csdir)


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



title_all="EasyPV药械妆不良反应报表统计分析工具_"+version_now
title_all2="EasyPV药械妆不良反应报表统计分析工具_"+version_now
# 第二部分：函数模块 ##################################################################

    
#序列号与用户组验证模块。

def EasyInf():
    inf={
    '软件名称':'EasyPV药械妆不良反应报表统计分析工具_',
    '版本号':'1.0.1',
    '功能介绍':'快速启动一些小工具。',
    'PID':'QX00RET6',
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










############################################################
#绘图函数
############################################################
    
def TOOLS_ror_mode1(data_all,methon):
    all_list=[]
    for a in ("事件发生年份","性别","年龄段","报告类型-严重程度","停药减药后反应是否减轻或消失","再次使用可疑药是否出现同样反应","对原患疾病影响","不良反应结果","关联性评价"):#,"时隔"):
        data_all[a]=data_all[a].astype(str)
        data_all[a]=data_all[a].fillna("不详")
        
        countx=0
        for x in data_all[methon].drop_duplicates():    
            countx=countx+1
            data2=data_all[(data_all[methon]==x)].copy()
            
            mtk=str(x)+"计数"
            mtk2=str(x)+"构成比(%)"
            result= data2.groupby(a).agg(计数=("报告编码","nunique") ).sort_values(by=a, ascending=[True], na_position="last").reset_index()    
            result[mtk2]=round(100*result["计数"]/result["计数"].sum(),2)
            result = result.rename(    columns={a: "项目"})
            result = result.rename(    columns={"计数": mtk}) #
            if countx>1:
                result_bak=pd.merge(result_bak,result, on=["项目"], how="outer")
            else:
                result_bak=result.copy()

        result_bak["类别"]=a
        all_list.append(result_bak.copy().reset_index(drop=True))
    
    
    data = pd.concat(all_list, ignore_index=True).fillna(0)
    data["报表类型"]="KETI"
    TABLE_tree_Level_2(data,1,data)    
    
def TOOLS_ror_mode2(data_all,methon):
    result=Countall(data_all).df_ror(["产品类别",methon]).reset_index()
    result["四分表"]=result["四分表"].str.replace("(","")
    result["四分表"]=result["四分表"].str.replace(")","")
    result["ROR信号（0-否，1-是）"]=0
    result["PRR信号（0-否，1-是）"]=0    
    result["分母核验"]=0        
    for ids,cols in result.iterrows():
        mtss=tuple(cols["四分表"].split(","))
        result.loc[ids,"a"]=int(mtss[0])
        result.loc[ids,"b"]=int(mtss[1])
        result.loc[ids,"c"]=int(mtss[2])
        result.loc[ids,"d"]=int(mtss[3])
        if int(mtss[1])*int(mtss[2])*int(mtss[3])*int(mtss[0])==0:
            result.loc[ids,"分母核验"]=1        
        if     cols['ROR值的95%CI下限']>1 and cols['出现频次']>=3:
            result.loc[ids,"ROR信号（0-否，1-是）"]=1
        if     cols['PRR值的95%CI下限']>1 and cols['出现频次']>=3:
            result.loc[ids,"PRR信号（0-否，1-是）"]=1                            
        result.loc[ids,"事件分类"]=str(TOOLS_get_list(result.loc[ids,"特定关键字"])[0])
    #TABLE_tree_Level_2(result,1,result)    
    result=pd.pivot_table(result, values=["出现频次",'ROR值', "ROR值的95%CI下限","ROR信号（0-否，1-是）",'PRR值',"PRR值的95%CI下限","PRR信号（0-否，1-是）","a","b","c","d","分母核验","风险评分"], index='事件分类', columns=methon, aggfunc='sum').reset_index().fillna(0)

    #载入器官系统
    try:
        filename=peizhidir+"0（范例）比例失衡关键字库.xls"
        if "报告类型-新的" in data_all.columns:
            guize_num="药品"
        else:
            guize_num="器械"    
        guize = pd.read_excel(filename, header=0, sheet_name=guize_num).reset_index(drop=True)
    except:
        pass

    for ids,cols in guize.iterrows():
        result.loc[result["事件分类"].str.contains(cols["值"], na=False),"器官系统损害"]=TOOLS_get_list(cols["值"])[0]
    
    #载入标准术语
    try:    
        umeu = peizhidir+"" + "share_easy_adrmdr_药品规整-SOC-Meddra库" + ".xlsx"
        try:
            code_pud = pd.read_excel( umeu, sheet_name="onept", header=0, index_col=0  ).reset_index()
        except:
            showinfo(title="错误信息", message="标准术语集无法加载。")

        try:
            code_pud2 = pd.read_excel( umeu, sheet_name="my", header=0, index_col=0  ).reset_index()
        except:
            showinfo(title="错误信息", message="自定义术语集无法加载。")

        code_pud=pd.concat([code_pud2,code_pud], ignore_index=True).drop_duplicates("code")        
        code_pud["code"]=code_pud["code"].astype(str)
        result["事件分类"]=result["事件分类"].astype(str)
        code_pud["事件分类"] = code_pud["PT"]
        result2 = pd.merge(result, code_pud, on=["事件分类"], how="left")    
        for ids,cols in result2.iterrows():
            result.loc[result["事件分类"]==cols["事件分类"],"Chinese"]=cols["Chinese"]
            result.loc[result["事件分类"]==cols["事件分类"],"PT"]=cols["PT"]            
            result.loc[result["事件分类"]==cols["事件分类"],"HLT"]=cols["HLT"]            
            result.loc[result["事件分类"]==cols["事件分类"],"HLGT"]=cols["HLGT"]            
            result.loc[result["事件分类"]==cols["事件分类"],"SOC"]=cols["SOC"]            
    except:
        pass
        
        
    result["报表类型"]="KETI"        
    TABLE_tree_Level_2(result,1,result)    
    
def TOOLS_ror_mode3(data_all,methon):
    data_all["css"]=0
    TOOLS_ror_mode2(data_all,methon)
    
def TOOLS_ror_mode4(data_all,methon):
    aaaa=[]
    for ids,cols in data.drop_duplicates(methon).iterrows():
        datam= data[(data_all[methon] == cols[methon])]
        m1=Countall(datam).df_psur()
        m1[methon]=cols[methon]
        if len(m1)>0:
            aaaa.append(m1)
            #print(m1)
    result=pd.concat(aaaa, ignore_index=True).sort_values(by="关键字标记", ascending=[False], na_position="last").reset_index()
    result["报表类型"]="KETI"            
    TABLE_tree_Level_2(result,1,result)    
        
def STAT_pinzhong(data,methon,whx):
    #品种统计专门开发的模块
    a=[methon]
    if whx==-1:#时间专用
        data2=data.drop_duplicates("报告编码").copy()
        result= data2.groupby([methon]).agg(计数=("报告编码","nunique") ).sort_values(by=methon, ascending=[True], na_position="last").reset_index()    
        result["构成比(%)"]=round(100*result["计数"]/result["计数"].sum(),2)
        result[methon]=result[methon].astype(str)
        result["报表类型"]="dfx_deepview"+"_"+str(a)
        TABLE_tree_Level_2(result,1,data2)    

    if whx==1:#非时间专用
        data2=data.copy()
        result= data2.groupby([methon]).agg(计数=("报告编码","nunique") ).sort_values(by="计数", ascending=[False], na_position="last").reset_index()    
        result["构成比(%)"]=round(100*result["计数"]/result["计数"].sum(),2)
        result["报表类型"]="dfx_deepview"+"_"+str(a)
        TABLE_tree_Level_2(result,1,data2)

    if whx==4:#转归专用
        data2=data.copy()
        data2.loc[data2["不良反应结果"].str.contains("好转", na=False), "不良反应结果2"] = "好转"
        data2.loc[data2["不良反应结果"].str.contains("痊愈", na=False), "不良反应结果2"] = "痊愈"        
        data2.loc[data2["不良反应结果"].str.contains("无进展", na=False), "不良反应结果2"] = "无进展"
        data2.loc[data2["不良反应结果"].str.contains("死亡", na=False), "不良反应结果2"] = "死亡"
        data2.loc[data2["不良反应结果"].str.contains("不详", na=False), "不良反应结果2"] = "不详"    
        data2.loc[data2["不良反应结果"].str.contains("未好转", na=False), "不良反应结果2"] = "未好转"            
        result= data2.groupby(["不良反应结果2"]).agg(计数=("报告编码","nunique") ).sort_values(by="计数", ascending=[False], na_position="last").reset_index()    
        result["构成比(%)"]=round(100*result["计数"]/result["计数"].sum(),2)
        result["报表类型"]="dfx_deepview"+"_"+str(["不良反应结果2"])
        TABLE_tree_Level_2(result,1,data2)
        
    if whx==5:#关联性评价专用
        data2=data.copy()

        data2["关联性评价汇总"]="("+data2["评价状态"].astype(str)+"("+data2["县评价"].astype(str)+"("+data2["市评价"].astype(str)+"("+data2["省评价"].astype(str)+"("+data2["国家评价"].astype(str)+")"
        data2["关联性评价汇总"]=data2["关联性评价汇总"].str.replace("(nan","",regex=False)
        data2["关联性评价汇总"]=data2["关联性评价汇总"].str.replace("nan)","",regex=False)
        data2["关联性评价汇总"]=data2["关联性评价汇总"].str.replace("nan","",regex=False)
        data2['最终的关联性评价'] = data2["关联性评价汇总"].str.extract('.*\((.*)\).*', expand=False)
        result= data2.groupby('最终的关联性评价').agg(计数=("报告编码","nunique") ).sort_values(by="计数", ascending=[False], na_position="last").reset_index()    
        result["构成比(%)"]=round(100*result["计数"]/result["计数"].sum(),2)
        result["报表类型"]="dfx_deepview"+"_"+str(['最终的关联性评价'])
        TABLE_tree_Level_2(result,1,data2)

    if whx==0:#事件统计    
        data[methon]=data[methon].fillna("未填写")
        data[methon]=data[methon].str.replace("*","",regex=False)
        msdd="use("+str(methon)+").file"    
        rm=str(Counter(TOOLS_get_list_r0(msdd,data,1000))).replace("Counter({", "{")
        rm=rm.replace("})", "}")
        rm = ast.literal_eval(rm)
        result=pd.DataFrame.from_dict(rm, orient="index",columns=["计数"]).reset_index()
        
        result["构成比(%)"]=round(100*result["计数"]/result["计数"].sum(),2)
        result["报表类型"]="dfx_deepvie2"+"_"+str(a)
        TABLE_tree_Level_2(result,1,data)
        return result

        #aa=str({k:v for k, v in rm.items() if STAT_judge_x(str(k),TOOLS_get_list(keyword_value))==1 })

    if whx==2 or  whx==3:#由code来反过来统计    
        data[methon]=data[methon].astype(str)
        data[methon]=data[methon].fillna("未填写")
        
        msdd="use("+str(methon)+").file"    
        rm=str(Counter(TOOLS_get_list_r0(msdd,data,1000))).replace("Counter({", "{")
        rm=rm.replace("})", "}")
        rm = ast.literal_eval(rm)
        result=pd.DataFrame.from_dict(rm, orient="index",columns=["计数"]).reset_index()
        print("正在统计，请稍后...")
        umeu = peizhidir+"" + "share_easy_adrmdr_药品规整-SOC-Meddra库" + ".xlsx"
        try:
            code_pud = pd.read_excel( umeu, sheet_name="simple", header=0, index_col=0  ).reset_index()
        except:
            showinfo(title="错误信息", message="标准术语集无法加载。")
            return 0
        try:
            code_pud2 = pd.read_excel( umeu, sheet_name="my", header=0, index_col=0  ).reset_index()
        except:
            showinfo(title="错误信息", message="自定义术语集无法加载。")
            return 0
        code_pud=pd.concat([code_pud2,code_pud], ignore_index=True).drop_duplicates("code")        
        code_pud["code"]=code_pud["code"].astype(str)
        result["index"]=result["index"].astype(str)

        result = result.rename(    columns={"index": "code"})
        result = pd.merge(result, code_pud, on=["code"], how="left")    
        result["code构成比(%)"]=round(100*result["计数"]/result["计数"].sum(),2)        
        result2= result.groupby("SOC").agg(SOC计数=("计数","sum") ).sort_values(by="SOC计数", ascending=[False], na_position="last").reset_index()
        result2["soc构成比(%)"]=round(100*result2["SOC计数"]/result2["SOC计数"].sum(),2)
        result2["SOC计数"]=result2["SOC计数"].astype(int)
        result = pd.merge(result, result2, on=["SOC"], how="left")

        if whx==3:
            result2["具体名称"]=""
            for ids,cols in result2.iterrows():
                aaa=""
                result_temp=result.loc[result["SOC"].str.contains(cols["SOC"], na=False)].copy()
                for ids2,cols2 in result_temp.iterrows():
                    aaa=aaa+str(cols2["PT"])+"("+str(cols2["计数"])+")、"
                result2.loc[ids,"具体名称"]=aaa
            result2["报表类型"]="dfx_deepvie2"+"_"+str(["SOC"])
            TABLE_tree_Level_2(result2,1,result)
        
        if whx==2:
            result["报表类型"]="dfx_deepvie2"+"_"+str(a)
            TABLE_tree_Level_2(result,1,data)                    
            
        
    pass    

def DRAW_pre(data):
    """预制的几个图形"""
    #try:
    #    if len(data["注册证编号/曾用注册证编号"].drop_duplicates())>1:
    #        text.insert(END,"该类图表仅支持列表内仅有单个注册证号。\n")
    #        return 0
    #except:
    #    pass
        
    mvp=list(data["报表类型"])[0].replace("1","")

    if "dfx_org监测机构" in mvp:
        data=data[:-1]
        DRAW_make_one(data, "报告图", "监测机构", "报告数量","超级托帕斯图(严重伤害数)")
    elif "dfx_org市级监测机构"  in mvp:
        data=data[:-1]
        DRAW_make_one(data, "报告图", "市级监测机构", "报告数量","超级托帕斯图(严重伤害数)")    
    elif "dfx_user"  in mvp:
        data=data[:-1]
        DRAW_make_one(data, "报告单位图", "单位名称", "报告数量","超级托帕斯图(严重伤害数)")


    elif "dfx_deepview"  in mvp:
        DRAW_make_one(data, "柱状图", data.columns[0], "计数","柱状图")

    elif "dfx_chiyouren" in mvp:
        data=data[:-1]
        DRAW_make_one(data, "涉及持有人图", "上市许可持有人名称", "总报告数","超级托帕斯图(总待评价数量)")

    elif "dfx_zhenghao" in mvp:
        data["产品"]=data["产品名称"]+"("+data["注册证编号/曾用注册证编号"]+")"
        DRAW_make_one(data, "涉及产品图", "产品", "证号计数","超级托帕斯图(严重伤害数)")        

    elif "dfx_pihao" in mvp:
        if len(data["注册证编号/曾用注册证编号"].drop_duplicates())>1:
            data["产品"]=data["产品名称"]+"("+data["注册证编号/曾用注册证编号"]+"--"+data["产品批号"]+")"
            DRAW_make_one(data, "涉及批号图", "产品", "批号计数","超级托帕斯图(严重伤害数)")    
        else:    
            DRAW_make_one(data, "涉及批号图", "产品批号", "批号计数","超级托帕斯图(严重伤害数)")    

    elif "dfx_xinghao" in mvp:
        if len(data["注册证编号/曾用注册证编号"].drop_duplicates())>1:
            data["产品"]=data["产品名称"]+"("+data["注册证编号/曾用注册证编号"]+"--"+data["型号"]+")"
            DRAW_make_one(data, "涉及型号图", "产品", "型号计数","超级托帕斯图(严重伤害数)")    
        else:
            DRAW_make_one(data, "涉及型号图", "型号", "型号计数","超级托帕斯图(严重伤害数)")    

    elif "dfx_guige" in mvp:
        if len(data["注册证编号/曾用注册证编号"].drop_duplicates())>1:
            data["产品"]=data["产品名称"]+"("+data["注册证编号/曾用注册证编号"]+"--"+data["规格"]+")"
            DRAW_make_one(data, "涉及规格图", "产品", "规格计数","超级托帕斯图(严重伤害数)")    
        else:
            DRAW_make_one(data, "涉及规格图", "规格", "规格计数","超级托帕斯图(严重伤害数)")    

    elif "PSUR" in mvp:
        DRAW_make_mutibar(data, "总数量", "严重", "事件分类", "总数量", "严重", "表现分类统计图")

    elif "keyword_findrisk" in mvp:
        
        xx=data.columns.to_list()
        target=xx[xx.index("关键字")+1]

        result = pd.pivot_table(
                data,
                index=target,
                columns="关键字",
                values=["计数"],
                aggfunc={"计数": "sum"},
                fill_value="0",
                margins=True,
                dropna=False,
            )  # .reset_index()
        result.columns = result.columns.droplevel(0)
        result=result[:-1].reset_index()
        
        result=pd.merge(result,data[[target,"该元素总数量"]].drop_duplicates(target), on=[target], how="left")
        #result=result.rename(columns={"All":"总数量"}).reset_index() 
        del result["All"]
        #result[target]=result[target].fillna("未填写")
        #result=result.applymap(lambda x: 'int' if str(x).isdigit() else x)
        #TABLE_tree_Level_2(result,1,result)
        #DRAW_make_risk_plot(result[:-1],target,[x for x in result.columns if x!=target], "关键字趋势图", 100)
        DRAW_make_risk_plot(result,target,[x for x in result.columns if x!=target], "关键字趋势图", 100)
                


    
def DRAW_make_risk_plot(data, bar_x,bar_y, title, methon,*gn):
    """风险预警栏目的专用绘图函数"""
    #data 当前表(字典)  bar_x X轴的列，BAR_Y y轴的列。  
    # 创建窗体  
    view_pic = Toplevel()
    view_pic.title(title)
    frame0 = ttk.Frame(view_pic, height=20)  # , width = 1200,
    frame0.pack(side=TOP)

    drawPic_f = Figure(figsize=(12, 6), dpi=100)  # fast100
    drawPic_canvas = FigureCanvasTkAgg(drawPic_f, master=view_pic)
    drawPic_canvas.draw()
    drawPic_canvas.get_tk_widget().pack(expand=1)  # grid(row=0, column=0)
    # 解决汉字乱码问题
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 使用指定的汉字字体类型（此处为黑体）
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 创建和显示工具条
    toolbar = NavigationToolbar2Tk(drawPic_canvas, view_pic)
    toolbar.update()
    drawPic_canvas.get_tk_widget().pack()

    drawPic_a = drawPic_f.add_subplot(111)
   
    drawPic_a.set_title(title)
    x_label = data[bar_x] #X标签
    
    #from pandas.api.types import is_datetime64_any_dtype
    if methon!=999: #这个是时间的，不转格式   
        drawPic_a.set_xticklabels(x_label, rotation=-90, fontsize=8)


    x_value = range(0, len(x_label), 1) #X轴



    #第一个柱状图(关键字风险不用)
    try:
        drawPic_a.bar(x_label, data["报告总数"],color='skyblue',label="报告总数")
        drawPic_a.bar(x_label, height=data["严重伤害数"],color="orangered",label="严重伤害数")
    except:
        pass
            
    #其余的折线图
    for y_col in bar_y:
        y_values= data[y_col].astype(float)  #Y轴
        
        if y_col=="关注区域":
            drawPic_a.plot(list(x_label), list(y_values),label=str(y_col),color="red") # width, label="num",
        else:
            drawPic_a.plot(list(x_label), list(y_values),label=str(y_col))  # width, label="num",
  
        #添加关键字标记（关键字方法使用）        
        if methon==100:
            for x00,y00 in zip(x_label,y_values):   
                if y00==max(y_values) and y00>=3:
                     drawPic_a.text(x00,y00,(str(y_col)+":"+str(int(y00))), color = 'black', size=8) ##在图上写文本    
    #添加风险标记 
    #try:
    #    for x00,y00 in zip(x_label,data["风险评分"]):   
    #        if y00>0:
    #             drawPic_a.text(x00,y00,"!", color = 'r', size=8) ##在图上写文本
    #except:
    #    pass
        
    #增加UCL
    try:
        if gn[0]:
            modelxx=gn[0]
    except:
        modelxx="ucl"
        
    if len(bar_y)==1:
        
        if modelxx=="更多控制线分位数":
            dat=data[bar_y].astype(float).values
            filters=np.where(dat>0,1,0)
            idc=np.nonzero(filters)
            dat=dat[idc]
            midx=np.median(dat)
            x_25=np.percentile(dat,25)
            x_75=np.percentile(dat,75)    
            x_IQR=x_75-x_25
            UpLimit=x_75+1.5*x_IQR
            DownLimit=x_25-1.5*x_IQR  

            
            drawPic_a.axhline(DownLimit, color='c', linestyle='--', label='异常下限')                 
      
            drawPic_a.axhline(x_25, color='r', linestyle='--', label='第25百分位数')  
            drawPic_a.axhline(midx, color='g', linestyle='--', label='中位数')      
            drawPic_a.axhline(x_75, color='r', linestyle='--', label='第75百分位数')    
                
            drawPic_a.axhline(UpLimit, color='c', linestyle='--', label='异常上限')       
            label_2 = ttk.Label(view_pic, text="中位数="+str(midx)+"; 第25百分位数="+str(x_25)+"; 第75百分位数="+str(x_75)+"; 异常上限(第75百分位数+1.5IQR)="+str(UpLimit)+"; IQR="+str(x_IQR))
            label_2.pack()      
                          
        elif modelxx=="更多控制线STD":
            dat=data[bar_y].astype(float).values
            filters=np.where(dat>0,1,0)
            idc=np.nonzero(filters)
            dat=dat[idc]
            
            mean=dat.mean()
            std= dat.std(ddof=1)
            upper_ctrl = mean + 3 * std
            lower_ctrl = std - 3 * std  
            
            if len(dat)<30:
                ci=st.t.interval(0.95, df=len(dat)-1,loc=np.mean(dat),scale=st.sem(dat))
            else:
                ci=st.norm.interval(0.95,loc=np.mean(dat),scale=st.sem(dat))
            ci=ci[1]            
            drawPic_a.axhline(upper_ctrl, color='r', linestyle='--', label='UCL')#+str(round(upper_ctrl,2)))  
            drawPic_a.axhline(mean+2*std, color='m', linestyle='--', label='μ+2σ')       
            drawPic_a.axhline(mean+std, color='m', linestyle='--', label='μ+σ')                               
            drawPic_a.axhline(mean, color='g', linestyle='--', label='CL')#+str(round(mean,2))+";std:"+str(round(std,2)))
            drawPic_a.axhline(mean-std, color='m', linestyle='--', label='μ-σ')        
            drawPic_a.axhline(mean-2*std, color='m', linestyle='--', label='μ-2σ')            
            drawPic_a.axhline(lower_ctrl, color='r', linestyle='--', label='LCL')#+str(round(lower_ctrl,2)))
            drawPic_a.axhline(ci, color='g', linestyle='-', label='95CI')
            label_1 = ttk.Label(view_pic, text="mean="+str(mean)+"; std="+str(std)+"; 99.73%:UCL(μ+3σ)="+str(upper_ctrl)+"; LCL(μ-3σ)="+str(lower_ctrl)+"; 95%CI="+str(ci))
            label_1.pack()
            
            label_2 = ttk.Label(view_pic, text="68.26%:μ+σ="+str(mean+std)+"; 95.45%:μ+2σ="+str(mean+2*std))
            label_2.pack() 
            
        else:
            dat=data[bar_y].astype(float).values
            filters=np.where(dat>0,1,0)
            idc=np.nonzero(filters)
            dat=dat[idc]
            mean=dat.mean()
            std= dat.std(ddof=1)
            upper_ctrl = mean + 3 * std
            lower_ctrl = std - 3 * std  
            drawPic_a.axhline(upper_ctrl, color='r', linestyle='--', label='UCL')#+str(round(upper_ctrl,2)))
            drawPic_a.axhline(mean, color='g', linestyle='--', label='CL')#+str(round(mean,2))+";std:"+str(round(std,2)))            
            drawPic_a.axhline(lower_ctrl, color='r', linestyle='--', label='LCL')#+str(round(lower_ctrl,2)))
            label_1 = ttk.Label(view_pic, text="mean="+str(mean)+"; std="+str(std)+"; UCL(μ+3σ)="+str(upper_ctrl)+"; LCL(μ-3σ)="+str(lower_ctrl))
            label_1.pack()

                                                   
    drawPic_a.set_title("控制图")
    drawPic_a.set_xlabel("项")
    drawPic_f.tight_layout(pad=0.4, w_pad=3.0, h_pad=3.0)
    box1 = drawPic_a.get_position()
    drawPic_a.set_position([box1.x0, box1.y0, box1.width * 0.7, box1.height])
    drawPic_a.legend(loc=2, bbox_to_anchor=(1.05, 1.0), fontsize=10, borderaxespad=0.0)


    xt22 = StringVar()
    number_chosen = ttk.Combobox(frame0, width=15, textvariable=xt22, state='readonly')
    number_chosen['values'] = bar_y
    number_chosen.pack(side=LEFT)
    number_chosen.current(0)

    
    B_draw0 = Button(
        frame0,
        text="控制图（单项-UCL(μ+3σ)）",
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: DRAW_make_risk_plot(data,bar_x,[x for x in bar_y if xt22.get() in x], title, methon))       
    B_draw0.pack(side=LEFT,anchor="ne")    
    B_draw5 = Button(
        frame0,
        text="控制图（单项-UCL(标准差法)）",
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: DRAW_make_risk_plot(data,bar_x,[x for x in bar_y if xt22.get() in x], title, methon,"更多控制线STD"))       
    B_draw5.pack(side=LEFT,anchor="ne")  
    B_draw5 = Button(
        frame0,
        text="控制图（单项-分位数）",
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: DRAW_make_risk_plot(data,bar_x,[x for x in bar_y if xt22.get() in x], title, methon,"更多控制线分位数"))       
    B_draw5.pack(side=LEFT,anchor="ne")      
          
    B_draw2 = Button(
        frame0,
        text="去除标记",
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: DRAW_make_risk_plot(data,bar_x,bar_y, title, 0))

    B_draw2.pack(side=LEFT,anchor="ne")
    drawPic_canvas.draw()
    
    

def DRAW_make_one(data, title, bar_x, bar_y,methon):
    """绘制柱状图饼图折线图（单个值）通用文件"""
    warnings.filterwarnings("ignore")
    view_pic = Toplevel()
    view_pic.title(title)
    frame0 = ttk.Frame(view_pic, height=20)  # , width = 1200,
    frame0.pack(side=TOP)             
    # 创造画布
    drawPic_f = Figure(figsize=(12, 6), dpi=100)  # fast100
    drawPic_canvas = FigureCanvasTkAgg(drawPic_f, master=view_pic)
    drawPic_canvas.draw()
    drawPic_canvas.get_tk_widget().pack(expand=1)  # grid(row=0, column=0)
    drawPic_a = drawPic_f.add_subplot(111)
    # 解决汉字乱码问题
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 使用指定的汉字字体类型（此处为黑体）
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 创建工具条
    toolbar = NavigationToolbar2Tk(drawPic_canvas, view_pic)
    toolbar.update()
    # 显示工具条
    drawPic_canvas.get_tk_widget().pack()
    
    #为字典传入做一个兼容
    try:
        test_ini = data.columns
        #data=data.sort_values(by=bar_y, ascending=[False], na_position="last")
    except:
        dict_ori = eval(data)
        dict_ori = pd.DataFrame.from_dict(
            dict_ori, orient=bar_x, columns=[bar_y]
        ).reset_index()
        data = dict_ori.sort_values(by=bar_y, ascending=[False], na_position="last")    


    #如果是时间的显示，则做一些优化
    if ("日期" in title or  "时间" in title  or  "季度" in title) and "饼图" not in methon:
        data[bar_x] = pd.to_datetime(data[bar_x], format="%Y/%m/%d").dt.date
        data = data.sort_values(by=bar_x, ascending=[True], na_position="last")
    elif "批号" in title: 
        data[bar_x] = data[bar_x].astype(str)
        data = data.sort_values(by=bar_x, ascending=[True], na_position="last")
        drawPic_a.set_xticklabels(data[bar_x], rotation=-90, fontsize=8)                           
    else:
        data[bar_x] = data[bar_x].astype(str)
        drawPic_a.set_xticklabels(data[bar_x], rotation=-90, fontsize=8)
    #定义好X,Y等参数
    values= data[bar_y]  
    x_value = range(0, len(values), 1)

    drawPic_a.set_title(title)
    
    
    #绘图函数
    if methon=="柱状图":
        drawPic_a.bar(x=data[bar_x], height=values, width=0.2, color="#87CEFA")  # width, label="num",plt.bar(x='size',height = 'tip',data=df_bar)
    elif methon=="饼图":
        drawPic_a.pie(x=values, labels=data[bar_x], autopct="%0.2f%%")
    elif methon=="折线图":
        drawPic_a.plot(data[bar_x], values, lw=0.5, ls='-', c="r", alpha=0.5) 

    elif  "托帕斯图" in str(methon):
        data_tps = data[bar_y].fillna(0)##将目标数据导入
     
        ##数据处理
        #data_tps.sort_values(ascending = False,inplace = True )##对数组进行排序,ascending 升序,inplace代表行和列的排序
        p=data_tps.cumsum()/data_tps.sum()*100

        key = p[p>0.8].index[0]##返回累计占比大于0.8的第一个索引名称
        key_num = data_tps.index.tolist().index(key)

        ##开始画图及结果输出

        drawPic_a.bar(x=data[bar_x], height=data_tps,color="C0",label=bar_y)##画条形图
        ax2 = drawPic_a.twinx()
        ax2.plot(data[bar_x], p, color="C1",alpha = 0.6,label="累计比例")
        ax2.yaxis.set_major_formatter(PercentFormatter())
        #if "时间" not in title:
        #    ax2.axvline(key_num,color='r',linestyle="--",alpha=0.3)  ##画红色的虚线
        #    ax2.text(key_num+0.2,p[key]-0.05,'%.3f%%' % (p[key]*100), color = 'r') ##在图上写文本

        drawPic_a.tick_params(axis="y", colors="C0")
        ax2.tick_params(axis="y", colors="C1")

        #增加多一个柱状图
        if  "超级托帕斯图" in str(methon):
            p1 = re.compile(r'[(](.*?)[)]', re.S)
            bar_z=re.findall(p1, methon)[0]
            drawPic_a.bar(x=data[bar_x], height=data[bar_z],color="orangered",label=bar_z)##画条形图        
    #格式设置
    drawPic_f.tight_layout(pad=0.4, w_pad=3.0, h_pad=3.0)
    box1 = drawPic_a.get_position()
    drawPic_a.set_position([box1.x0, box1.y0, box1.width * 0.7, box1.height])
    drawPic_a.legend(loc=2, bbox_to_anchor=(1.05, 1.0), fontsize=10, borderaxespad=0.0)

    #开始绘制
    drawPic_canvas.draw()
    
    #柱状图增加数值
    if len(values)<=20 and methon!="饼图":
        for x,y in zip(x_value,values):
            text = str(y)
            xy=(x,y+0.3)
            drawPic_a.annotate(text,xy=xy,fontsize=8,color="black",ha="center",va="baseline")


    
    B1 = Button(
        frame0,
        relief=GROOVE,
        activebackground="green",
        text="保存原始数据",
        command=lambda: TOOLS_save_dict(data),
    )
    B1.pack(side=RIGHT)
    
    B333 = Button(
        frame0, relief=GROOVE, text="查看原始数据", command=lambda: TOOLS_view_dict(data, 0)
    )
    B333.pack(side=RIGHT)    
    

    B0 = Button(
        frame0,
        relief=GROOVE,
        text="饼图",
        command=lambda: DRAW_make_one(data, title, bar_x, bar_y,"饼图"),
    )
    B0.pack(side=LEFT)

    B0 = Button(
        frame0,
        relief=GROOVE,
        text="柱状图",
        command=lambda: DRAW_make_one(data,title, bar_x, bar_y,"柱状图"),
    )
    B0.pack(side=LEFT)
    B0 = Button(
        frame0,
        relief=GROOVE,
        text="折线图",
        command=lambda: DRAW_make_one(data, title, bar_x, bar_y,"折线图"),
    )
    B0.pack(side=LEFT)

    B0 = Button(
        frame0,
        relief=GROOVE,
        text="托帕斯图",
        command=lambda: DRAW_make_one(data, title, bar_x, bar_y,"托帕斯图"),
    )
    B0.pack(side=LEFT)
def DRAW_make_mutibar(data, y, y1, index, yL, y1L, title):  # y=大数，y1=小数，index=横坐标标签,yL y的图例标签
    """绘制堆叠柱状图通用文件"""
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
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 创建工具条
    toolbar = NavigationToolbar2Tk(drawPic_canvas, view_pic)
    toolbar.update()
    # 显示工具条
    drawPic_canvas.get_tk_widget().pack()
    y = data[y]
    y1 = data[y1]
    index = data[index]

    x = range(0, len(y), 1)
    drawPic_a.set_xticklabels(index, rotation=-90, fontsize=8)
    drawPic_a.bar(
        x, y, align="center", tick_label=index, label=yL
    )  # width, label="num", color="#66c2a5",
    drawPic_a.bar(
        x, y1, align="center", label=y1L
    )  # width, label="num",, color="#8da0cb"
    drawPic_a.set_title(title)
    drawPic_a.set_xlabel("项")
    drawPic_a.set_ylabel("数量")

    drawPic_f.tight_layout(pad=0.4, w_pad=3.0, h_pad=3.0)
    box1 = drawPic_a.get_position()
    drawPic_a.set_position([box1.x0, box1.y0, box1.width * 0.7, box1.height])
    drawPic_a.legend(loc=2, bbox_to_anchor=(1.05, 1.0), fontsize=10, borderaxespad=0.0)
    
    drawPic_canvas.draw()
    B1 = Button(
        frame0,
        relief=GROOVE,
        activebackground="green",
        text="保存原始数据",
        command=lambda: TOOLS_save_dict(data),
    )
    B1.pack(side=RIGHT)

############################################################
#数据处理业务函数
############################################################
def SMALL_last_non_null_value(df, columns_list, new_column_name):  
    """  
    在DataFrame df中创建一个新列，其值为columns_list中最后一个非空值。  
      
    参数:  
        df (pd.DataFrame): 输入的DataFrame。  
        columns_list (list of str): 要检查的列名列表，按顺序。  
        new_column_name (str): 新列的名称。  
          
    返回:  
        pd.DataFrame: 包含新列的原始DataFrame。  
    """  
      
    # 遍历每一行，找到最后一个非空值  
    def get_last_non_null(row):  
        for col in reversed(columns_list):  # 从后向前遍历列  
            if pd.notna(row[col]):  
                return row[col]  
        return np.nan  # 如果没有非空值，则返回NaN  
  
    # 应用函数并创建新列  
    df[new_column_name] = df.apply(get_last_non_null, axis=1)  
      
    return df  

def CLEAN_hzp(data):
    """数据清洗模块-化妆品"""
    if "报告编码" not in data.columns: #如果报告编码是存在的，则是规整过的，不需要重复规整。
            data["特殊化妆品注册证书编号/普通化妆品备案编号"]=data["特殊化妆品注册证书编号/普通化妆品备案编号"].fillna("-未填写-")         
            data["省级评价结果"]=data["省级评价结果"].fillna("-未填写-")     
            data["生产企业"]=data["生产企业"].fillna("-未填写-")                   
            data["提交人"]="不适用" 
            data["医疗机构类别"]="不适用" 
            data["经营企业或使用单位"]="不适用" 
            data["报告状态"]="报告单位评价"             
            data["所属地区"]="不适用"   
            data["医院名称"]="不适用" 
            data["报告地区名称"]="不适用"                         
            data["提交人"]="不适用"  
            data["型号"]=data["化妆品分类"]    
            data["关联性评价"]=data["上报单位评价结果"]   
            data["规格"]="不适用"  
            data["器械故障表现"]=data["初步判断"]
            data["伤害表现"]=data["自觉症状"]+ data["皮损部位"]+ data["皮损形态"]
            data["事件原因分析"]="不适用"             
            data["事件原因分析描述"]="不适用"  
            data["调查情况"]="不适用"              
            data["具体控制措施"]="不适用"     
            data["未采取控制措施原因"]="不适用"                        
            data["报告地区名称"]="不适用"                         
            data["上报单位所属地区"]="不适用"              
            data["持有人报告状态"]="不适用" 
            data["年龄类型"]="岁" 
            data["经营企业使用单位报告状态"]="不适用"             
            data["产品归属"]="化妆品"                                     
            data["管理类别"]="不适用"            
            data["超时标记"]="不适用"                                    
            #改名列                                
            data = data.rename(
                columns={
                    "报告表编号": "报告编码",
                    "报告类型": "伤害",
                    "报告地区": "监测机构",
                    "报告单位名称": "单位名称",
                    "患者/消费者姓名": "姓名",
                    "不良反应发生日期": "事件发生日期",
                    
                    "过程描述补充说明": "使用过程",
                    "化妆品名称": "产品名称",
                    "化妆品分类": "产品类别",
                    "生产企业": "上市许可持有人名称",
                    "生产批号": "产品批号",
                    "特殊化妆品注册证书编号/普通化妆品备案编号": "注册证编号/曾用注册证编号",              
                    
                }
            )          
            data["时隔"]=pd.to_datetime(data["事件发生日期"])-pd.to_datetime(data["开始使用日期"])
            data["时隔"]=data["时隔"].astype(str)
            data.loc[(data["省级评价结果"]!="-未填写-"), "有效报告"] = 1  
            data["伤害"] = data["伤害"].str.replace("严重", "严重伤害",regex=False)  
            try:
                data=TOOL_guizheng(data,4,True)
            except:
                pass
            return data
         
         
         
         
def CLEAN_yp(data):
    """数据清洗模块-药品"""
    if "报告编码" not in data.columns: #如果报告编码是存在的，则是规整过的，不需要重复规整。
        #增加药品持有人反馈报告兼容性
        if "反馈码" in data.columns and  "报告表编码"  not in data.columns:    
            #增加列
            data["提交人"]="不适用" 
            data["经营企业或使用单位"]="不适用" 
            data["报告状态"]="报告单位评价"             
            data["所属地区"]="不适用"   
            data["产品类别"]="无源"  
            data["医院名称"]="不适用" 
            data["报告地区名称"]="不适用"                         
            data["提交人"]="不适用"              

            
            #改名列                                
            data = data.rename(
                columns={
                    "反馈码": "报告表编码",
                    "序号": "药品序号",
                    "新的": "报告类型-新的",
                    "报告类型": "报告类型-严重程度",
                    "用药-日数": "用法-日",
                    "用药-次数": "用法-次",
                }
            )  

            
        #药品的通用兼容代码（省平台）       
        #特殊处理 
        if "医院名称" in data.columns:
            data = data.rename(columns={"医院名称": "单位名称"})
        if     "患者姓名" not in data.columns:
            data['患者姓名']=''  
        if '报告单位名称' in data.columns:
            data['单位名称']=data['报告单位名称']  
        if     "唯一标识" not in data.columns:
            data["报告编码"] = data["报告表编码"].astype(str) + data["患者姓名"].astype(str)    
                   
        if     "唯一标识" in data.columns:
            data["唯一标识"]=data["唯一标识"].astype(str)
            data = data.rename(columns={"唯一标识": "报告编码"})
        if "医疗机构类别" not in data.columns:
            data["医疗机构类别"] = "医疗机构"
            data["经营企业使用单位报告状态"] = "已提交"
        try:
            data["年龄和单位"] = data["年龄"].astype(str) + data["年龄单位"]                 
        except:
            data["年龄和单位"] = data["年龄"].astype(str) + data["年龄类型"]
        data.loc[(data["报告类型-新的"] == "新的"), "管理类别"] = "Ⅲ类"
        data.loc[(data["报告类型-严重程度"] == "严重"), "管理类别"] = "Ⅲ类"                
        text.insert(END,"剔除已删除报告和重复报告...")
        if "删除标识" in data.columns:  # 兼容药品
            data = data[(data["删除标识"] != "删除")] 
        if "重复报告" in data.columns:  # 兼容药品
            data = data[(data["重复报告"] != "重复报告")]    

        #增加列
        data["报告类型-新的"] = data["报告类型-新的"].fillna(" ")
        data.loc[(data["报告类型-严重程度"] == "严重"), "伤害"] = "严重伤害"
        data["伤害"] = data["伤害"].fillna("所有一般") 
        data["伤害PSUR"] = data["报告类型-新的"].astype(str)+data["报告类型-严重程度"].astype(str)               
        data["用量用量单位"] = data["用量"].astype(str) + data["用量单位"].astype(str)
        data["报告分数"] = 0
        data["规格"] = "不适用"   
        data["事件原因分析"] = "不适用" 
        data["事件原因分析描述"] = "不适用"         
        data["初步处置情况"] = "不适用" 
        data["伤害表现"] = data["不良反应名称"]       
        data["产品类别"] = "无源"
        data["调查情况"] = "不适用"
        data["具体控制措施"] = "不适用"
        data["上报单位所属地区"] =  data["报告地区名称"] 

        #data["持有人报告状态"] =  data["报告状态"] 
        data["注册证编号/曾用注册证编号"] =  data["批准文号"] 
        data["器械故障表现"] =  data["不良反应名称"] 
        data["型号"] =  data["剂型"] 
        #data["关联性评价"] =  data["报告人评价"]         
                
        data["未采取控制措施原因"] = "不适用"
        data["报告单位评价"] = data["报告类型-新的"].astype(str) + data["报告类型-严重程度"].astype(str)
        data.loc[(data["报告类型-新的"] == "新的"), "持有人报告状态"] = "待评价"                     
        data["用法temp日"] = "日"
        data["用法temp次"] = "次"
        data["用药频率"] = (
                data["用法-日"].astype(str)
                + data["用法temp日"]
                + data["用法-次"].astype(str)
                + data["用法temp次"]
            )
        try:        
            data["相关疾病信息[疾病名称]-术语"] =data["原患疾病"]
            data["治疗适应症-术语"] =data["用药原因"]   
        except:
            pass                       
        #改名列                                            
        try:
            data = data.rename(columns={"提交日期": "报告日期"}) 
            data = data.rename(columns={"提交人": "报告人"})  
            data = data.rename(columns={"报告状态": "持有人报告状态"}) 
            data = data.rename(columns={"所属地区": "使用单位、经营企业所属监测机构"})             

            #data = data.rename(columns={"批准文号": "注册证编号/曾用注册证编号"})
            data = data.rename(columns={"通用名称": "产品名称"})
            data = data.rename(columns={"生产厂家": "上市许可持有人名称"})
            data = data.rename(columns={"不良反应发生时间": "事件发生日期"})
            #data = data.rename(columns={"不良反应名称": "器械故障表现"})
            data = data.rename(columns={"不良反应过程描述": "使用过程"})
            data = data.rename(columns={"生产批号": "产品批号"})
            data = data.rename(columns={"报告地区名称": "使用单位、经营企业所属监测机构"})
            #data = data.rename(columns={"剂型": "型号"})
            data = data.rename(columns={"报告人评价": "关联性评价"})               
            data = data.rename(columns={"年龄单位": "年龄类型"})
        except:
            text.insert(END,"数据规整失败。")
            return 0
            

        data['报告日期']=data['报告日期'].str.strip()    
        data['事件发生日期']=data['事件发生日期'].str.strip()    
        data['用药开始时间']=data['用药开始时间'].str.strip()    
        
        return data
    if "报告编码" in data.columns: 
        return data        
        #########兼容药品的代码##########################################
def CLEAN_qx(data):
        """数据清洗模块-器械"""    
        # 增器械加持有人报表兼容性
        if "使用单位、经营企业所属监测机构" not in data.columns and "监测机构" not in data.columns:
            data["使用单位、经营企业所属监测机构"] = "本地"
        if "上市许可持有人名称" not in data.columns:
            data["上市许可持有人名称"] = data["单位名称"]
        if "注册证编号/曾用注册证编号" not in data.columns:
            data["注册证编号/曾用注册证编号"] = data["注册证编号"]
        if "事件原因分析描述" not in data.columns:
            data["事件原因分析描述"] = "  "
        if "初步处置情况" not in data.columns:
            data["初步处置情况"] = "  "
            
        # 基础规整
        text.insert(END,"\n正在执行格式规整和增加有关时间、年龄、性别等统计列...")
        data = data.rename(columns={"使用单位、经营企业所属监测机构": "监测机构"})
        data["报告编码"] = data["报告编码"].astype("str")
        data["产品批号"] = data["产品批号"].astype("str")
        data["型号"] = data["型号"].astype("str")
        data["规格"] = data["规格"].astype("str")
        data["注册证编号/曾用注册证编号"] = data["注册证编号/曾用注册证编号"].str.replace("(", "（",regex=False)  # 转义
        data["注册证编号/曾用注册证编号"] = data["注册证编号/曾用注册证编号"].str.replace(")", "）",regex=False)  # 转义
        data["注册证编号/曾用注册证编号"] = data["注册证编号/曾用注册证编号"].str.replace("*", "※",regex=False)  # 转义
        data["注册证编号/曾用注册证编号"] = data["注册证编号/曾用注册证编号"].fillna("-未填写-")
        data["产品名称"] = data["产品名称"].str.replace("*", "※",regex=False)  # 转义
        data["产品批号"] = data["产品批号"].str.replace("(", "（",regex=False)  # 转义
        data["产品批号"] = data["产品批号"].str.replace(")", "）",regex=False)  # 转义
        data["产品批号"] = data["产品批号"].str.replace("*", "※",regex=False)  # 转义
        if ini['模式']!='化妆品':
            data["报告分数"] = 0
        #空值处理
        data["上市许可持有人名称"] = data["上市许可持有人名称"].fillna("-未填写-")
        data["产品类别"] = data["产品类别"].fillna("-未填写-")
        data["产品名称"] = data["产品名称"].fillna("-未填写-")
        data["注册证编号/曾用注册证编号"] = data["注册证编号/曾用注册证编号"].fillna("-未填写-")        
        data["产品批号"] = data["产品批号"].fillna("-未填写-")
        data["型号"] = data["型号"].fillna("-未填写-")        
        data["规格"] = data["规格"].fillna("-未填写-")
        
        #增加几个列
        data["伤害与评价"]=data["伤害"]+data["持有人报告状态"]
        data["注册证备份"] = data["注册证编号/曾用注册证编号"]    


        data['报告日期'] = pd.to_datetime(data['报告日期'], format='%Y-%m-%d', errors='coerce')     
        data['事件发生日期'] = pd.to_datetime(data['事件发生日期'], format='%Y-%m-%d', errors='coerce')     
                        
        data["报告月份"] = data["报告日期"].dt.to_period("M").astype(str)    
        data["报告季度"] = data["报告日期"].dt.to_period("Q").astype(str)    
        data["报告年份"] = data["报告日期"].dt.to_period("Y").astype(str)    #    品种评价        
        data["事件发生月份"] = data["事件发生日期"].dt.to_period("M").astype(str)            
        data["事件发生季度"] = data["事件发生日期"].dt.to_period("Q").astype(str)                
        data["事件发生年份"] = data["事件发生日期"].dt.to_period("Y").astype(str)    
        #data["事件发生年份"]=data["报告月份"].str[0:4]    

                
        if ini["模式"]=="器械":
            data['发现或获知日期'] = pd.to_datetime(data['发现或获知日期'], format='%Y-%m-%d', errors='coerce') 
            data["时隔"]=pd.to_datetime(data["发现或获知日期"])-pd.to_datetime(data["事件发生日期"])
            data["时隔"]=data["时隔"].astype(str)
            data["报告时限"] = pd.to_datetime(data["报告日期"]) - pd.to_datetime(data["发现或获知日期"])
            data["报告时限"] = data["报告时限"].dt.days
            data.loc[(data["报告时限"]>20)&(data["伤害"]=="严重伤害"), "超时标记"] = 1
            data.loc[(data["报告时限"]>30)&(data["伤害"]=="其他"), "超时标记"] = 0    
            data.loc[(data["报告时限"]>7)&(data["伤害"]=="死亡"), "超时标记"] = 1   
            
            data.loc[(data["经营企业使用单位报告状态"]=="审核通过"), "有效报告"] = 1               
            
            
        if ini["模式"]=="药品":
            data['用药开始时间'] = pd.to_datetime(data['用药开始时间'], format='%Y-%m-%d', errors='coerce')             
            data["时隔"]=pd.to_datetime(data["事件发生日期"])-pd.to_datetime(data["用药开始时间"])
            data["时隔"]=data["时隔"].astype(str)
            #data["报告时限"] = pd.to_datetime(data["报告日期"]) - pd.to_datetime(data["事件发生日期"])
            data["报告时限"] = pd.to_datetime(data["国家中心接收时间"]) - pd.to_datetime(data["报告日期"])
            data["报告时限"] = data["报告时限"].dt.days
            data.loc[(data["报告时限"]>15)&(data["报告类型-严重程度"]=="严重"), "超时标记"] = 1
            data.loc[(data["报告时限"]>30)&(data["报告类型-严重程度"]=="一般"), "超时标记"] = 1
            data.loc[(data["报告时限"]>15)&(data["报告类型-新的"]=="新的"), "超时标记"] = 1
            data.loc[(data["报告时限"]>1)&(data["报告类型-严重程度"]=="死亡"), "超时标记"] = 1              

            data.loc[~data["市评价时间"].isnull(), "有效报告"] = 1
            
             
        data.loc[((data["年龄"].astype(str)=="未填写")|data["年龄"].isnull()), "年龄"] = -1 
        data["年龄"]=data["年龄"].astype(float)
        data["年龄"]=data["年龄"].fillna(-1)
        data["性别"]=data["性别"].fillna("未填写")    
        data["年龄段"]="未填写"
        try:
            data.loc[(data["年龄类型"]=="月"), "年龄"] = data["年龄"].values/12
            data.loc[(data["年龄类型"]=="月"), "年龄类型"] ="岁"  
        except:
            pass 
        try:          
            data.loc[(data["年龄类型"]=="天"), "年龄"] = data["年龄"].values/365
            data.loc[(data["年龄类型"]=="天"), "年龄类型"] ="岁"    
        except:
            pass                  
        data.loc[(data["年龄"].values<4), "年龄段"] = "0-婴幼儿（0-4）"   
        data.loc[(data["年龄"].values>=5), "年龄段"] = "1-少儿（5-14）"       
        data.loc[(data["年龄"].values>=15), "年龄段"] = "2-青壮年（15-44）"     
        data.loc[(data["年龄"].values>=45), "年龄段"] = "3-中年期（45-64）"       
        data.loc[(data["年龄"].values>=65), "年龄段"] = "4-老年期（≥65）"      
        data.loc[(data["年龄"].values==-1), "年龄段"] = "未填写" 
        #严重修正
        try:
            data=SMALL_last_non_null_value(data, ["伤害","伤害.1"], "综合伤害")
            data=data.rename(columns={"伤害":"伤害（医院上报）"})
            data=data.rename(columns={"综合伤害":"伤害"})            
        except:
            pass
        #单位名称规整
        data["规整后品类"]="N"
        data=TOOL_guizheng(data,2,True)
        
        #产品名称规整
        if ini['模式'] in ["器械"]:
            data=TOOL_guizheng(data,3,True)            

        #为课题服务的规整
        
        data=TOOL_guizheng(data,"课题",True)

        try:
            data["注册证编号/曾用注册证编号"]= data["注册证编号/曾用注册证编号"].fillna("未填写")
        except:
            pass 

        data["数据清洗完成标记"]="是" 
        data_backup = data.loc[:]        
        return data

#
############################################################
#程序功能函数
############################################################
def TOOLS_fileopen():
    """-导入多个文件"""
    warnings.filterwarnings('ignore')
    allfileName = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xls *.xlsx"), ("XLS", "*.xls"), ("XLSX", "*.xlsx")])
    ori = Useful_tools_openfiles(allfileName,0)
    try:
        ori=ori.loc[ : , ~ori.columns.str.contains("^Unnamed")]
    except:
        pass
 
    ini["模式"]="其他"
    data=ori
    TABLE_tree_Level_2(data,0,data)


def TOOLS_pinzhong(datax):
    """品种评价专用"""
    datax["患者姓名"]=datax["报告表编码"]
    datax["用量"]=datax["用法用量"] 
    datax["评价状态"]=datax["报告单位评价"]       
    datax["用量单位"]=""      
    datax["单位名称"]="不适用"     
    datax["报告地区名称"]="不适用"     
    datax["用法-日"]="不适用"         
    datax["用法-次"]="不适用"    #不良反应发生时间
    datax["不良反应发生时间"]=datax["不良反应发生时间"].str[0:10]
    #print(datax["不良反应发生时间"])
    datax["持有人报告状态"]="待评价"    
    datax = datax.rename( columns={
                    "是否非预期": "报告类型-新的",
                    "不良反应-术语": "不良反应名称",
                    "持有人/生产厂家": "上市许可持有人名称"
                } )  
    return datax #不良反应-术语报告单位评价
    



def Useful_tools_openfiles(files_list,sheetname):
    """导入清单中的xls文件,并合并成一个的小模块，参数：sheetname是单元表的名称"""    
    k = [pd.read_excel(x, header=0, sheet_name=sheetname) for x in files_list] 
    data = pd.concat(k, ignore_index=True).drop_duplicates()    
    return data
    
def TOOLS_allfileopen():
    """-导入多个文件"""
    global ori  #规整前
    global ini
    global data
    ini["原始模式"]="否"
    warnings.filterwarnings('ignore')
    
    allfileName = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xls *.xlsx"), ("XLS", "*.xls"), ("XLSX", "*.xlsx")])
    ori = Useful_tools_openfiles(allfileName,0)


    #药品品种评价数据做的一个兼容
    try:
        orid=Useful_tools_openfiles(allfileName,"报告信息")       
        if "是否非预期" in orid.columns:
            ori=TOOLS_pinzhong(orid)
    except:
        pass

    ini["模式"]="其他"
    #原始导入(试验性)   把表格名称改为字典数据，则为原始模式导入。
    try:
        ori = Useful_tools_openfiles(allfileName,"字典数据")
        ini["原始模式"]="是"
        if "UDI" in ori.columns:
            ini["模式"]="器械"
            data=ori
        if "报告类型-新的" in ori.columns:
            ini["模式"]="药品"
            data=ori            
        else:
            ini["模式"]="其他"                                
    except:
        pass


    try:
        ori=ori.loc[ : , ~ori.columns.str.contains("^Unnamed")]
    except:
        pass
        


    if "UDI" in ori.columns and ini["原始模式"]!="是":
        text.insert(END,"识别出为器械报表,正在进行数据规整...")  
        ini["模式"]="器械"
        ori=CLEAN_qx(ori)
        data=ori        
    if "报告类型-新的" in ori.columns and ini["原始模式"]!="是":
        text.insert(END,"识别出为药品报表,正在进行数据规整...")  
        ini["模式"]="药品"
        ori=CLEAN_yp(ori)
        ori=CLEAN_qx(ori)
        data=ori          
    if "光斑贴试验" in ori.columns and ini["原始模式"]!="是":
        text.insert(END,"识别出为化妆品报表,正在进行数据规整...")  
        ini["模式"]="化妆品"
        ori=CLEAN_hzp(ori)
        ori=CLEAN_qx(ori)
        data=ori  

    
    if ini["模式"]=="其他":
        text.insert(END, "\n数据读取成功，行数："+str(len(ori)))
        data=ori
        PROGRAM_Menubar(root,data, 0, data)
        try:
            ini["button"][0].pack_forget()   
            ini["button"][1].pack_forget()              
            ini["button"][2].pack_forget()              
            ini["button"][3].pack_forget()  
            ini["button"][4].pack_forget()                
        except:
            pass 
            
    else:      
        ini["清洗后的文件"]=data    
        ini["证号"]=Countall(data).df_zhenghao()
        text.insert(END, "\n数据读取成功，行数："+str(len(data))) 
        PROGRAM_Menubar(root,data, 0, data)
        try:
            ini["button"][0].pack_forget()   
            ini["button"][1].pack_forget()              
            ini["button"][2].pack_forget()              
            ini["button"][3].pack_forget()  
            ini["button"][4].pack_forget()                
        except:
            pass         
        B_open_files6 = Button(
            frame0,
            text="地市统计",
            bg="white",
            height=2,
            width=12,
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(Countall(data).df_org("市级监测机构"),1, ori),
        )
        B_open_files6.pack()    

        
        B_open_files7 = Button(
            frame0,
            text="县区统计",
            bg="white",
            height=2,
            width=12,
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(Countall(data).df_org("监测机构"),1, ori),
        )
        B_open_files7.pack()
        
        
        B_open_files8 = Button(
            frame0,
            text="上报单位",
            bg="white",
            height=2,
            width=12,
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(Countall(data).df_user(),1, ori),
        )
        B_open_files8.pack()
        B_open_files9 = Button(
            frame0,
            text="生产企业",
            bg="white",
            height=2,
            width=12,
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(Countall(data).df_chiyouren(),1, ori),
        )
        B_open_files9.pack()
        B_open_files10 = Button(
            frame0,
            text="产品统计",
            bg="white",
            height=2,
            width=12,
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(ini["证号"],1, ori,ori,"dfx_zhenghao"),
        )
        B_open_files10.pack()
        ini["button"]=[B_open_files6,B_open_files7,B_open_files8,B_open_files9,B_open_files10]
    
    text.insert(END, "\n")
        
def TOOLS_sql(data):
    """sql"""
    warnings.filterwarnings("ignore")
    try:
        testtihs=data.columns    
    except:
        return 0
        
    def execsql(sql):    
        try:
            result=pd.read_sql_query( sqltext(sql),con=conn )#
        except:
            showinfo(title="提示", message="SQL语句有误。")
            return 0
        try:
            del result["level_0"]
        except:
            pass
        TABLE_tree_Level_2(result,1,data)
        
        

    filename='sqlite://'
    engine= create_engine(filename)
    try:
        data.to_sql('data',  con=engine,chunksize=10000,if_exists='replace',index=True)#,index_label='id_name')    
    except:
        showinfo(title="提示", message="不支持该表格。")
        return 0
     
    conn=engine.connect()
    query="select * from data" #/*"+str(data.columns.to_list())+"*/\n
 
        
    helper = Toplevel()
    helper.title("SQL查询")
    helper.geometry("700x500")
    
    frame0 = ttk.Frame(helper, width=700, height=20)
    frame0.pack(side=TOP)
    framecanvas = ttk.Frame(helper, width=700, height=20)
    framecanvas.pack(side=BOTTOM)
 
    ##########报表查看器的通用部件#################
    try:
        xt22 = StringVar()
        xt22.set("select * from data WHERE 单位名称='佛山市第一人民医院'")

        import_se1 = Label(frame0, text="SQL查询", anchor='w')
        import_se1.pack(side=LEFT)
        import_se3 = Label(frame0, text="检索：")
        #import_se3.pack(side=LEFT)
        #xentry_t22 = Entry(frame0, width=14, textvariable=xt22).pack(side=LEFT)

    
        B_SAVE = Button(
            framecanvas,
            text="执行",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            width=700,
            command=lambda: execsql(text_helper.get("1.0","end")),
        )  #
        B_SAVE.pack(side=LEFT)
          
        
    except:
        pass
        
    yscrollbar = Scrollbar(helper)
    text_helper = Text(helper, height=80, width=150, bg="#FFFFFF", font="微软雅黑")
    yscrollbar.pack(side=RIGHT, fill=Y)
    text_helper.pack()
    yscrollbar.config(command=text_helper.yview)
    text_helper.config(yscrollcommand=yscrollbar.set)
    def callback1(event=None):
        text_helper.event_generate('<<Copy>>')   
    def callback2(event=None):
        text_helper.event_generate('<<Paste>>')
    def callback3(data,filename):
         TOOLS_savetxt(data,filename,1)
    menu = Menu(text_helper,tearoff=False,)
    menu.add_command(label="复制", command=callback1)
    menu.add_command(label="粘贴", command=callback2)
    menu.add_command(label="源文件列", command=lambda:PROGRAM_helper(data.columns.to_list()))
    def popup(event):
         menu.post(event.x_root, event.y_root)   # post在指定的位置显示弹出菜单
    text_helper.bind("<Button-3>", popup)                 # 绑定鼠标右键,执行popup函数
            

       
    text_helper.insert(END,query)
    

    
def TOOLS_view_dict(str_helper, methon):
    """查看可复制的图标数据"""
    helper = Toplevel()
    helper.title("查看数据")
    helper.geometry("700x500")

    yscrollbar = Scrollbar(helper)
    text_helper = Text(helper, height=100, width=150)
    yscrollbar.pack(side=RIGHT, fill=Y)
    text_helper.pack()
    yscrollbar.config(command=text_helper.yview)
    text_helper.config(yscrollcommand=yscrollbar.set)
    if methon == 1:
        # for x in range(len(str_helper)):
        text_helper.insert(END, str_helper)
        text_helper.insert(END, "\n\n")
        return 0
    for i in range(len(str_helper)):
        text_helper.insert(END, str_helper.iloc[i, 0])
        text_helper.insert(END, ":")
        text_helper.insert(END, str_helper.iloc[i, 1])
        text_helper.insert(END, "\n\n")

def TOOLS_save_dict(data):
    """保存文件"""
    file_path_flhz = filedialog.asksaveasfilename(
        title=u"保存文件",
        initialfile="排序后的原始数据",
        defaultextension="xls",
        filetypes=[("Excel 97-2003 工作簿", "*.xls")],
    )
    try:
        data["详细描述T"]=data["详细描述T"].astype(str)
    except:
        pass
    try:
        data["报告编码"]=data["报告编码"].astype(str)
    except:
        pass

    writer = pd.ExcelWriter(file_path_flhz,engine="xlsxwriter")  # 
    data.to_excel(writer, sheet_name="字典数据")
    writer.close()
    showinfo(title="提示", message="文件写入成功。")

def TOOLS_savetxt(data,filename,methon):
    """保存为txt文件"""          
    file = open(filename,"w",encoding='utf-8') 
    file.write(data)
    # 刷新缓存
    file.flush()  
    if methon==1:
        showinfo(title="提示信息", message="保存成功。")


def TOOLS_deep_view(data, selection,selection2,methon):
    """按钮的核心功能文件：点击按钮出统计清单methon=0 分组  methon=1透视"""
    if methon==0:
        try:
            data[selection]=data[selection].fillna("这个没有填写")
        except:
            pass
        result=data.groupby(selection).agg(计数=(selection2[0],selection2[1]))    
    if methon==1: 
            #result[selection2[0]]=result[selection2[0]].astype(str)
            result = pd.pivot_table(
                data,
                index=selection[:-1],
                columns=selection[-1],
                values=[selection2[0]],
                aggfunc={selection2[0]:selection2[1]},
                fill_value="0",
                margins=True,
                dropna=False,
            )  # .reset_index()
            result.columns = result.columns.droplevel(0)  
            result=result.rename(columns={"All":"计数"})
    
    
    if "日期" in selection  or "时间" in selection   or "季度" in selection   :
        result = result.sort_values(
            [selection], ascending=False, na_position="last"
        )
    else:
       
        result = result.sort_values(
            by=["计数"], ascending=False, na_position="last"
        )
    result = result.reset_index()
    result["构成比(%)"]=round(100*result["计数"]/result["计数"].sum(),2)
    if "计数" in result.columns and methon==1:
        result["构成比(%)"]=result["构成比(%)"]*2
    if methon==0:
        result["报表类型"]="dfx_deepview"+"_"+str(selection)
    if methon==1:
        result["报表类型"]="dfx_deepview"+"_"+str(selection[:-1])
    return result
        
    
        
def TOOLS_easyreadT(bos):  # 查看表格
    """行列互换查看表格"""
    bos[
        "#####分隔符#########"
    ] = "######################################################################"
    bos2 = bos.stack(dropna=False)
    bos2 = pd.DataFrame(bos2).reset_index()
    bos2.columns = ["序号", "条目", "详细描述T"]
    bos2["逐条查看"] = "逐条查看"
    bos2["报表类型"] = "逐条查看"
    return bos2

def TOOLS_data_masking(data):  # 2222222
    """-数据脱敏，meithon= 药品 或者 器械"""
    from random import choices
    from string import ascii_letters, digits

    data = data.reset_index(drop=True)
    if "单位名称.1" in data.columns:
        methon = "器械"
    else:
        methon = "药品"
    umeu = peizhidir+"" + "share_easy_adrmdr_数据脱敏" + ".xls"
    try:
        masking_set = pd.read_excel(
            umeu, sheet_name=methon, header=0, index_col=0
        ).reset_index()
    except:
        showinfo(title="错误信息", message="该功能需要配置文件才能使用！")
        return 0
    x = 0
    x2 = len(data)
    data["abcd"] = "□"
    for i in masking_set["要脱敏的列"]:
        x = x + 1
        PROGRAM_change_schedule(x, x2)
        text.insert(END, "\n正在对以下列进行脱敏处理：")
        text.see(END)
        text.insert(END, i)
        try:
            ids = set(data[i])
        except:
            showinfo(title="提示", message="脱敏文件配置错误，请修改配置表。")
            return 0
        id_mapping = {si: "".join(choices(digits, k=10)) for si in ids}
        data[i] = data[i].map(id_mapping)
        data[i] = data["abcd"] + data[i].astype(str)
    try:
        PROGRAM_change_schedule(10, 10)
        del data["abcd"]
        file_path_flhz = filedialog.asksaveasfilename(
            title=u"保存脱敏后的文件",
            initialfile="脱敏后的文件",
            defaultextension="xlsx",
            filetypes=[("Excel 工作簿", "*.xlsx"), ("Excel 97-2003 工作簿", "*.xls")],
        )
        writer2 = pd.ExcelWriter(file_path_flhz, engine="xlsxwriter")
        data.to_excel(writer2, sheet_name="sheet0")
        writer2.close()
    except:
        text.insert(END, "\n文件未保存，但导入的数据已按要求脱敏。")
    text.insert(END, "\n脱敏操作完成。")
    text.see(END)
    return data
    
def TOOLS_get_new(data,methon):
    """监测新的不良反应"""
    def drug(data):
        """药品不良反应名称统计"""    
        data=data.drop_duplicates("报告编码")    
        rm=str(Counter(TOOLS_get_list_r0("use(器械故障表现).file",data,1000))).replace("Counter({", "{")
        rm=rm.replace("})", "}")
        import ast
        user_dict = ast.literal_eval(rm)    
        df = TOOLS_easyreadT(pd.DataFrame([user_dict]))
        df = df.rename(columns={"逐条查看": "ADR名称规整"})
        return df
    if methon=="证号":
        root.attributes("-topmost", True)
        root.attributes("-topmost", False)
        listxa= data.groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号"]).agg(计数=("报告编码","nunique") ).reset_index()
        listx2=listxa.drop_duplicates("注册证编号/曾用注册证编号").copy()
        listx2["所有不良反应"]=""        #20231011    
        listx2["关注建议"]=""    
        listx2["疑似新的"]=""
        listx2["疑似旧的"]=""
        listx2["疑似新的（高敏）"]=""
        listx2["疑似旧的（高敏）"]=""
        k=1
        p=int(len(listx2))
        for ids,cols in listx2.iterrows():
            datam = data[(data["注册证编号/曾用注册证编号"] == cols["注册证编号/曾用注册证编号"])]
            data_new=datam.loc[datam["报告类型-新的"].str.contains("新", na=False)].copy()
            data_old=datam.loc[~datam["报告类型-新的"].str.contains("新", na=False)].copy()
            list_new=drug(data_new)
            list_old=drug(data_old)
            list_all=drug(datam)#20231011
            PROGRAM_change_schedule(k,p)
            k=k+1
            
            for idc,colc in list_all.iterrows(): #20231011
                    if  "分隔符" not in  colc["条目"]:
                        kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","                
                        listx2.loc[ids,"所有不良反应"]=listx2.loc[ids,"所有不良反应"]+kde    
            
            for idc,colc in list_old.iterrows():
                    if  "分隔符" not in  colc["条目"]:
                        kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","                
                        listx2.loc[ids,"疑似旧的"]=listx2.loc[ids,"疑似旧的"]+kde    
                    #高敏处理
                    if  "分隔符" not in  colc["条目"] and int(colc["详细描述T"])>=2:
                        kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","                
                        listx2.loc[ids,"疑似旧的（高敏）"]=listx2.loc[ids,"疑似旧的（高敏）"]+kde                            
                                                                  
            for idc,colc in list_new.iterrows():
                if str(colc["条目"]).strip() not in str(listx2.loc[ids,"疑似旧的"]) and "分隔符" not in str(colc["条目"]):
                    kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","
                    listx2.loc[ids,"疑似新的"]=listx2.loc[ids,"疑似新的"]+kde    
                    if int(colc["详细描述T"])>=3:
                        listx2.loc[ids,"关注建议"]=listx2.loc[ids,"关注建议"]+"！"    
                    if int(colc["详细描述T"])>=5:
                        listx2.loc[ids,"关注建议"]=listx2.loc[ids,"关注建议"]+"●"
                #高敏处理
                if str(colc["条目"]).strip() not in str(listx2.loc[ids,"疑似旧的（高敏）"]) and "分隔符" not in str(colc["条目"]) and  int(colc["详细描述T"])>=2:
                    kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","
                    listx2.loc[ids,"疑似新的（高敏）"]=listx2.loc[ids,"疑似新的（高敏）"]+kde    
                    #print(kde)                
        listx2["疑似新的"]="{"+listx2["疑似新的"]+"}"
        listx2["疑似旧的"]="{"+listx2["疑似旧的"]+"}"
        listx2["所有不良反应"]="{"+listx2["所有不良反应"]+"}" #20221011        
        listx2["疑似新的（高敏）"]="{"+listx2["疑似新的（高敏）"]+"}"
        listx2["疑似旧的（高敏）"]="{"+listx2["疑似旧的（高敏）"]+"}"        
        
        listx2 = listx2.rename(columns={"器械待评价(药品新的报告比例)": "新的报告比例"})
        listx2 = listx2.rename(columns={"严重伤害待评价比例(药品严重中新的比例)": "严重报告中新的比例"})
        listx2["报表类型"]="dfx_zhenghao"

        data_temp_x2 = pd.pivot_table( data, values=["报告编码"],index=["注册证编号/曾用注册证编号"],columns="报告单位评价",aggfunc={"报告编码": "nunique"},fill_value="0",margins=True,dropna=False,).rename(columns={"报告编码": "数量"})
        data_temp_x2.columns = data_temp_x2.columns.droplevel(0)
        listx2=pd.merge(listx2,  data_temp_x2.reset_index(),on=["注册证编号/曾用注册证编号"], how="left")

        
            
        TABLE_tree_Level_2(listx2.sort_values(by="计数", ascending=[False], na_position="last"),1,data)
    if methon=="品种":
        root.attributes("-topmost", True)
        root.attributes("-topmost", False)
        listxa=data.groupby(["产品类别","产品名称"]).agg(计数=("报告编码","nunique") ).reset_index()
        listx2=listxa.drop_duplicates("产品名称").copy()
        listx2["产品名称"]=listx2["产品名称"].str.replace("*","",regex=False)
        listx2["所有不良反应"]=""        #20231011
        listx2["关注建议"]=""
        listx2["疑似新的"]=""
        listx2["疑似旧的"]=""
        listx2["疑似新的（高敏）"]=""
        listx2["疑似旧的（高敏）"]=""        
        k=1
        p=int(len(listx2))
        
    
        for ids,cols in listx2.iterrows():
            #print(cols["计数项目"])
            datam = data[(data["产品名称"] == cols["产品名称"])]
            #datam=data.loc[data["产品名称"].str.contains(cols["计数项目"], na=False)].copy()
            data_new=datam.loc[datam["报告类型-新的"].str.contains("新", na=False)].copy()
            data_old=datam.loc[~datam["报告类型-新的"].str.contains("新", na=False)].copy()
            list_all=drug(datam)#20231011            
            list_new=drug(data_new)
            list_old=drug(data_old)
            PROGRAM_change_schedule(k,p)
            k=k+1
            
            for idc,colc in list_all.iterrows(): #20231011
                    if  "分隔符" not in  colc["条目"]:
                        kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","                
                        listx2.loc[ids,"所有不良反应"]=listx2.loc[ids,"所有不良反应"]+kde    
            
            
            for idc,colc in list_old.iterrows():
                    if  "分隔符" not in  colc["条目"]:
                        kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","                
                        listx2.loc[ids,"疑似旧的"]=listx2.loc[ids,"疑似旧的"]+kde        
                    #高敏处理
                    if  "分隔符" not in  colc["条目"] and int(colc["详细描述T"])>=2:
                        kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","                
                        listx2.loc[ids,"疑似旧的（高敏）"]=listx2.loc[ids,"疑似旧的（高敏）"]+kde                                
                                                              
            for idc,colc in list_new.iterrows():
                if str(colc["条目"]).strip() not in str(listx2.loc[ids,"疑似旧的"]) and "分隔符" not in str(colc["条目"]):
                    kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","
                    listx2.loc[ids,"疑似新的"]=listx2.loc[ids,"疑似新的"]+kde    
                    if int(colc["详细描述T"])>=3:
                        listx2.loc[ids,"关注建议"]=listx2.loc[ids,"关注建议"]+"！"    
                    if int(colc["详细描述T"])>=5:
                        listx2.loc[ids,"关注建议"]=listx2.loc[ids,"关注建议"]+"●"
                #高敏处理
                if str(colc["条目"]).strip() not in str(listx2.loc[ids,"疑似旧的（高敏）"]) and "分隔符" not in str(colc["条目"]) and  int(colc["详细描述T"])>=2:
                    kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","
                    listx2.loc[ids,"疑似新的（高敏）"]=listx2.loc[ids,"疑似新的（高敏）"]+kde    
                        
        listx2["疑似新的"]="{"+listx2["疑似新的"]+"}"
        listx2["疑似旧的"]="{"+listx2["疑似旧的"]+"}"
        listx2["所有不良反应"]="{"+listx2["所有不良反应"]+"}" #20221011    
        listx2["疑似新的（高敏）"]="{"+listx2["疑似新的（高敏）"]+"}"
        listx2["疑似旧的（高敏）"]="{"+listx2["疑似旧的（高敏）"]+"}"
        listx2["报表类型"]="dfx_chanpin"            

        data_temp_x2 = pd.pivot_table( data, values=["报告编码"],index=["产品名称"],columns="报告单位评价",aggfunc={"报告编码": "nunique"},fill_value="0",margins=True,dropna=False,).rename(columns={"报告编码": "数量"})
        data_temp_x2.columns = data_temp_x2.columns.droplevel(0)    
        listx2=pd.merge(listx2,  data_temp_x2.reset_index(),on=["产品名称"], how="left")            
        TABLE_tree_Level_2(listx2.sort_values(by="计数", ascending=[False], na_position="last"),1,data)
        
    if methon=="页面":
        new=""
        old=""
        data_new=data.loc[data["报告类型-新的"].str.contains("新", na=False)].copy()
        data_old=data.loc[~data["报告类型-新的"].str.contains("新", na=False)].copy()
        list_new=drug(data_new)
        list_old=drug(data_old)
        if 1==1:
            for idc,colc in list_old.iterrows():
                    if  "分隔符" not in  colc["条目"]:
                        kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","                
                        old=old+kde                                              
            for idc,colc in list_new.iterrows():
                if str(colc["条目"]).strip() not in old and "分隔符" not in str(colc["条目"]):
                    kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","
                    new=new+kde    
        old="{"+old+"}"
        new="{"+new+"}"
        allon="\n可能是新的不良反应：\n\n"+new+"\n\n\n可能不是新的不良反应：\n\n"+old
        TOOLS_view_dict(allon,1)
        
def TOOLS_strdict_to_pd(strdict):  # 2222222
    """-文本格式的字典转PD"""
    return pd.DataFrame.from_dict(eval(strdict), orient="index",columns=["content"]).reset_index()  

def TOOLS_xuanze(data,methon):
    """-批量筛选数据专用"""
    if methon==0:
        listx = pd.read_excel(filedialog.askopenfilename(filetypes=[("XLS", ".xls")]),sheet_name=0,header=0,index_col=0,).reset_index()
    else:
        listx = pd.read_excel(peizhidir+"0（范例）批量筛选.xls",sheet_name=0,header=0,index_col=0,).reset_index()
    data["temppr"]=""
    for x in listx.columns.tolist():
        data["temppr"]=data["temppr"]+"----"+data[x]
    namex2 = "测试字段MMMMM"
    for x in listx.columns.tolist():        
        
        for i in listx[x].drop_duplicates():
            if i:
                namex2 = namex2 + "|" + str(i)
    data = data.loc[data["temppr"].str.contains(namex2, na=False)].copy()
    del  data["temppr"]     # 包括的
    data=data.reset_index(drop=True)
    
    TABLE_tree_Level_2(data, 0, data)

def TOOLS_add_c(data,cols):  
            data["关键字查找列o"] =""
            for x in TOOLS_get_list(cols["查找列"]):
                data["关键字查找列o"] = data["关键字查找列o"] + data[x].astype("str")  
            if cols["条件"]== "等于":
                data.loc[(data[cols["查找列"]].astype(str)==str(cols["条件值"])), cols["赋值列名"]] = cols["赋值"] 
            if cols["条件"]== "大于":
                data.loc[(data[cols["查找列"]].astype(float)>cols["条件值"]), cols["赋值列名"]] = cols["赋值"] 
            if cols["条件"]== "小于":
                data.loc[(data[cols["查找列"]].astype(float)<cols["条件值"]), cols["赋值列名"]] = cols["赋值"]                  
            if cols["条件"]== "介于":
                a0=TOOLS_get_list(cols["条件值"])                
                data.loc[((data[cols["查找列"]].astype(float)<float(a0[1]))&(data[cols["查找列"]].astype(float)>float(a0[0]))) , cols["赋值列名"]] = cols["赋值"]  
            if cols["条件"]== "不含":
                data.loc[(~data["关键字查找列o"].str.contains(cols["条件值"])) , cols["赋值列名"]] = cols["赋值"] 
            if cols["条件"]== "包含":
                data.loc[data["关键字查找列o"].str.contains(cols["条件值"], na=False), cols["赋值列名"]] = cols["赋值"] 
            if cols["条件"]== "同时包含":
                list_c=TOOLS_get_list_r0(cols["条件值"],0)
                if len(list_c)==1:
                    data.loc[data["关键字查找列o"].str.contains(list_c[0], na=False), cols["赋值列名"]] = cols["赋值"]                 
                if len(list_c)==2:
                    data.loc[(data["关键字查找列o"].str.contains(list_c[0], na=False))&(data["关键字查找列o"].str.contains(list_c[1], na=False)), cols["赋值列名"]] = cols["赋值"]     
                if len(list_c)==3:
                    data.loc[(data["关键字查找列o"].str.contains(list_c[0], na=False))&(data["关键字查找列o"].str.contains(list_c[1], na=False))&(data["关键字查找列o"].str.contains(list_c[2], na=False)), cols["赋值列名"]] = cols["赋值"]         
                if len(list_c)==4:
                    data.loc[(data["关键字查找列o"].str.contains(list_c[0], na=False))&(data["关键字查找列o"].str.contains(list_c[1], na=False))&(data["关键字查找列o"].str.contains(list_c[2], na=False))&(data["关键字查找列o"].str.contains(list_c[3], na=False)), cols["赋值列名"]] = cols["赋值"]         
                if len(list_c)==5:
                    data.loc[(data["关键字查找列o"].str.contains(list_c[0], na=False))&(data["关键字查找列o"].str.contains(list_c[1], na=False))&(data["关键字查找列o"].str.contains(list_c[2], na=False))&(data["关键字查找列o"].str.contains(list_c[3], na=False))&(data["关键字查找列o"].str.contains(list_c[4], na=False)), cols["赋值列名"]] = cols["赋值"]         
            return data
                                                                         

def TOOL_guizheng(data,methon,rt):
    """数据规整函数"""  
    #data=data.reset_index()
    if methon==0:#选择文件自定义规整
        listxx = pd.read_excel(filedialog.askopenfilename(filetypes=[("XLSX", ".xlsx")]),sheet_name=0,header=0,index_col=0,).reset_index()
        listxx = listxx[(listxx["执行标记"] == "是")].reset_index()          
        for ids, cols in listxx.iterrows():
            data=TOOLS_add_c(data,cols)
        del data["关键字查找列o"]
        
    elif methon==1:#默认规整
        listxx = pd.read_excel(peizhidir+"0（范例）数据规整.xlsx",sheet_name=0,header=0,index_col=0,).reset_index()
        listxx = listxx[(listxx["执行标记"] == "是")].reset_index()          
        for ids, cols in listxx.iterrows():
            data=TOOLS_add_c(data,cols)
        del data["关键字查找列o"]
        
    elif methon=="课题":#课题服务的规整
        listxx = pd.read_excel(peizhidir+"0（范例）品类规整.xlsx",sheet_name=0,header=0,index_col=0,).reset_index()
        listxx = listxx[(listxx["执行标记"] == "是")].reset_index()          
        for ids, cols in listxx.iterrows():
            data=TOOLS_add_c(data,cols)
        del data["关键字查找列o"]
        
    elif methon==2:#使用上报单位表规整
        text.insert(END,"\n开展报告单位和监测机构名称规整...")
        listxx1 = pd.read_excel(peizhidir+"share_adrmdr_pinggu_上报单位.xls",sheet_name="报告单位",header=0,index_col=0,).fillna("没有定义好X").reset_index()
        listxx2 = pd.read_excel(peizhidir+"share_adrmdr_pinggu_上报单位.xls",sheet_name="监测机构",header=0,index_col=0,).fillna("没有定义好X").reset_index()
        listxx3 = pd.read_excel(peizhidir+"share_adrmdr_pinggu_上报单位.xls",sheet_name="地市清单",header=0,index_col=0,).fillna("没有定义好X").reset_index()                
        for ids, cols in listxx1.iterrows():
            data.loc[(data["单位名称"] == cols["曾用名1"]), "单位名称"] = cols["单位名称"]
            data.loc[(data["单位名称"] == cols["曾用名2"]), "单位名称"] = cols["单位名称"]
            data.loc[(data["单位名称"] == cols["曾用名3"]), "单位名称"] = cols["单位名称"]
            data.loc[(data["单位名称"] == cols["曾用名4"]), "单位名称"] = cols["单位名称"]
            data.loc[(data["单位名称"] == cols["曾用名5"]), "单位名称"] = cols["单位名称"]
                        
            data.loc[(data["单位名称"] == cols["单位名称"]), "医疗机构类别"] = cols["医疗机构类别"]
            data.loc[(data["单位名称"] == cols["单位名称"]), "监测机构"] = cols["监测机构"]

        for ids, cols in listxx2.iterrows():
            data.loc[(data["监测机构"] == cols["曾用名1"]), "监测机构"] = cols["监测机构"]
            data.loc[(data["监测机构"] == cols["曾用名2"]), "监测机构"] = cols["监测机构"]
            data.loc[(data["监测机构"] == cols["曾用名3"]), "监测机构"] = cols["监测机构"]
        
        for qwe in listxx3["地市列表"]:
            data.loc[(data["上报单位所属地区"].str.contains(qwe, na=False)), "市级监测机构"] = qwe        
        
            
        data.loc[(data["上报单位所属地区"].str.contains("顺德", na=False)), "市级监测机构"] = "佛山"    
        data["市级监测机构"]=data["市级监测机构"].fillna("-未规整的-")
            
    elif methon==3:#产品名称规整
            dfx = (
                data.groupby(["上市许可持有人名称", "产品类别", "产品名称", "注册证编号/曾用注册证编号"])
                .aggregate({"报告编码": "count"})
                .reset_index()
                )
            dfx = dfx.sort_values(
                by=["注册证编号/曾用注册证编号", "报告编码"], ascending=[False, False], na_position="last"
                ).reset_index()
            text.insert(END,"\n开展产品名称规整(注册证号-产品名称众数法)..")
            del dfx["报告编码"]
            dfx = dfx.drop_duplicates(["注册证编号/曾用注册证编号"])
            data = data.rename(
                columns={"上市许可持有人名称": "上市许可持有人名称（规整前）", "产品类别": "产品类别（规整前）", "产品名称": "产品名称（规整前）"})
            data = pd.merge(data, dfx, on=["注册证编号/曾用注册证编号"], how="left")

    elif methon==4:#化妆品规整
        text.insert(END,"\n正在开展化妆品注册单位规整...")
        listxx2 = pd.read_excel(peizhidir+"0（范例）化妆品注册单位.xlsx",sheet_name="机构列表",header=0,index_col=0,).reset_index()

        for ids, cols in listxx2.iterrows():
            data.loc[(data["单位名称"] == cols["中文全称"]), "监测机构"] = cols["归属地区"]
            data.loc[(data["单位名称"] == cols["中文全称"]), "市级监测机构"] = cols["地市"]            
        data["监测机构"]=data["监测机构"].fillna("未规整")
        data["市级监测机构"]=data["市级监测机构"].fillna("未规整")        
    if rt==True:
        return data
    else:
        TABLE_tree_Level_2(data, 0, data)

def TOOL_person(data):
    """化妆品评表人员专项统计（帮助林科做的）"""
    listxx2 = pd.read_excel(peizhidir+"0（范例）化妆品注册单位.xlsx",sheet_name="专家列表",header=0,index_col=0,).reset_index()
    for ids, cols in listxx2.iterrows():
        data.loc[(data["市级监测机构"] == cols["市级监测机构"]), "评表人员"] = cols["评表人员"]    
        data["评表人员"]=data["评表人员"].fillna("未规整")  
        dfx_guige=data.groupby(["评表人员"]).agg(
            报告数量=("报告编码","nunique"),    
            地市=("市级监测机构",STAT_countx),
            ).sort_values(by="报告数量", ascending=[False], na_position="last").reset_index()
    TABLE_tree_Level_2(dfx_guige, 0, dfx_guige)                

def TOOLS_get_list(ori_list):
    """将字符串转化为列表，返回一个经过整理的、去重的列表，get_list_r0的精简版，一般用于循环"""
    ori_list = str(ori_list)
    uselist_key = []
    uselist_key.append(ori_list)
    uselist_key = ",".join(uselist_key)
    uselist_key = uselist_key.split("|")
    uselist_temp = uselist_key[:]
    uselist_key = list(set(uselist_key))
    uselist_key.sort(key=uselist_temp.index)
    return uselist_key    
    
def TOOLS_get_list_m(ori_list,methon):
    """根据methon将字符串转化为列表，不去重"""
    ori_list = str(ori_list)
    #uselist_key = []
    #uselist_key.append(ori_list)
    if methon:
        uselist_key = re.split(methon,ori_list)
    else:
         uselist_key = re.split("/||,|，|;|；|┋|、",ori_list)        
    return uselist_key      
      
def TOOLS_get_list_r0(ori_list, search_result, *methon): #methon=1000:不去重
    """创建单元格支持多个甚至表单（文件）传入的方法，返回一个经过整理的清单，methon=1000就是不去重"""
    ori_list = str(ori_list)
    # print(methon)
    if pd.notnull(ori_list):
        try:
            if "use(" in str(ori_list):  # 创建支持列表传入的方法
                string = ori_list
                p1 = re.compile(r"[(](.*?)[)]", re.S)
                arr = re.findall(p1, string)
                uselist_key = []
                if ").list" in ori_list:  # 使用配置表的表
                    umeu = peizhidir+"" + str(arr[0]) + ".xls"
                    uselist_keyfile = pd.read_excel(
                        umeu, sheet_name=arr[0], header=0, index_col=0
                    ).reset_index()
                    uselist_keyfile["检索关键字"] = uselist_keyfile["检索关键字"].astype(str)
                    uselist_key = uselist_keyfile["检索关键字"].tolist() + uselist_key
                if ").file" in ori_list:  # 使用原始文件中的列
                    #search_result[arr[0]] = search_result[arr[0]].astype(str)
                    uselist_key = search_result[arr[0]].astype(str).tolist() + uselist_key

                # 增加药品ADR名称的一些适应：
                try:
                    if "报告类型-新的" in search_result.columns:
                        uselist_key = ",".join(uselist_key)  # 拆解含有、的列表元素
                        uselist_key = uselist_key.split(";")
                        uselist_key = ",".join(uselist_key)  # 拆解含有、的列表元素
                        uselist_key = uselist_key.split("；")
                        uselist_key = [c.replace("（严重）", "") for c in uselist_key]
                        uselist_key = [c.replace("（一般）", "") for c in uselist_key]
                except:
                    pass
                # 药品ADR名称适应结束。
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split("┋")                
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split(";")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split("；")
                uselist_key = ",".join(uselist_key)  # 拆解含有、的列表元素
                uselist_key = uselist_key.split("、")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split("，")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split(",")

                
                uselist_temp = uselist_key[:]
                try:
                    if methon[0]==1000:
                      pass
                except:
                      uselist_key = list(set(uselist_key))
                uselist_key.sort(key=uselist_temp.index)

            else:
                ori_list = str(ori_list)
                uselist_key = []
                uselist_key.append(ori_list)
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split("┋")                
                uselist_key = ",".join(uselist_key)  # 拆解含有、的列表元素
                uselist_key = uselist_key.split("、")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split("，")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split(",")

                uselist_temp = uselist_key[:]
                try:
                    if methon[0]==1000:
                      uselist_key = list(set(uselist_key))
                except:
                      pass  
                uselist_key.sort(key=uselist_temp.index)
                uselist_key.sort(key=uselist_temp.index)

        except ValueError:
            showinfo(title="提示信息", message="创建单元格支持多个甚至表单（文件）传入的方法，返回一个经过整理的清单出错，任务终止。")
            return False

    return uselist_key    

def TOOLS_easyread2(datax_owercount_all):
    """规整查看：易读格式预警"""

    datax_owercount_all["分隔符"] = "●"
    datax_owercount_all["上报机构描述"] = (
        datax_owercount_all["使用过程"].astype("str")
        + datax_owercount_all["分隔符"]
        + datax_owercount_all["事件原因分析"].astype("str")
        + datax_owercount_all["分隔符"]
        + datax_owercount_all["事件原因分析描述"].astype("str")
        + datax_owercount_all["分隔符"]
        + datax_owercount_all["初步处置情况"].astype("str")
    )
    datax_owercount_all["持有人处理描述"] = (
        datax_owercount_all["关联性评价"].astype("str")
        + datax_owercount_all["分隔符"]
        + datax_owercount_all["调查情况"].astype("str")
        + datax_owercount_all["分隔符"]
        + datax_owercount_all["事件原因分析"].astype("str")
        + datax_owercount_all["分隔符"]
        + datax_owercount_all["具体控制措施"].astype("str")
        + datax_owercount_all["分隔符"]
        + datax_owercount_all["未采取控制措施原因"].astype("str")
    )
    datax_owercount_easyread = datax_owercount_all[
        [
            "报告编码",
            "事件发生日期",
            "报告日期",
            "单位名称",
            "产品名称",
            "注册证编号/曾用注册证编号",
            "产品批号",
            "型号",
            "规格",
            "上市许可持有人名称",
            "管理类别",
            "伤害",
            "伤害表现",
            "器械故障表现",
            "上报机构描述",
            "持有人处理描述",
            "经营企业使用单位报告状态",
            "监测机构",
            "产品类别",
            "医疗机构类别",
            "年龄",
            "年龄类型",
            "性别"
        ]
    ]  # 证号风险
    datax_owercount_easyread = datax_owercount_easyread.sort_values(
        by=["事件发生日期"],
        ascending=[False],
        na_position="last",
    )
    datax_owercount_easyread=datax_owercount_easyread.rename(columns={"报告编码": "规整编码"})    
    return datax_owercount_easyread
    
# 3.6 人工智能和机器学习函数 ##############################


def fenci(get1,get2,ori):
    """分词模块"""
    import glob
    import jieba
    import random
    
    try:
        ori=ori.drop_duplicates(["报告编码"])
    except:
        pass
    def get_TF(words, topK):
        tf_dic = {}
        for w in words:
            tf_dic[w] = tf_dic.get(w, 0) + 1
        return sorted(tf_dic.items(), key=lambda x: x[1], reverse=True)[:topK]

    init_file = pd.read_excel(
        get1, sheet_name="初始化", header=0, index_col=0
    ).reset_index()
    # stop_words=stop_words_file["停用词"]#
    topK = init_file.iloc[0, 2]
    stop_words_file = pd.read_excel(
        get1, sheet_name="停用词", header=0, index_col=0
    ).reset_index()
    # stop_words=stop_words_file["停用词"]#
    stop_words_file["停用词"] = stop_words_file["停用词"].astype(str)
    stop_words = [l.strip() for l in stop_words_file["停用词"]]
    my_dict_file = pd.read_excel(
        get1, sheet_name="本地词库", header=0, index_col=0
    ).reset_index()
    my_dict = my_dict_file["本地词库"]  #
    jieba.load_userdict(my_dict)  # 加载自定义词典

    # 读取分词工作源数据
    corpus = ""
    columns_list = TOOLS_get_list_r0(
        get2, ori
    )  # 要合并的列清单,注意：如果用到源文件列的方法需要传入源文件。
    try:
        for r in columns_list:
            for i in ori[r]:
                corpus = corpus + str(i)
    except:
        text.insert(END, "分词配置文件未正确设置，将对整个表格进行分词。")
        for r in ori.columns.tolist():
            for i in ori[r]:
                corpus = corpus + str(i)        
    split_words = []
    split_words = split_words + [x for x in jieba.cut(corpus) if x not in stop_words]
    m = dict(get_TF(split_words, topK))
    key_word_list = pd.DataFrame([m]).T
    key_word_list = key_word_list.reset_index()
    return key_word_list

def TOOLS_time(data,timeq,methon):    
    """移动时间窗函数"""
    data2=data.drop_duplicates(["报告编码"]).groupby([timeq]).agg(
            报告总数=("报告编码","nunique"),    
            ).sort_values(by=timeq, ascending=[True], na_position="last").reset_index()    
        
    data2=data2.set_index(timeq)

    data2=data2.resample('D').asfreq(fill_value=0)
    
    data2["time"]=data2.index.values
    data2["time"]=pd.to_datetime(data2["time"], format="%Y/%m/%d").dt.date
    
        

    
    n1=30#30 #365
    n2=30#365

    data2["30日移动平均数"]=round(data2["报告总数"].rolling(n1,min_periods=1).mean(),2)
    
    data2["目标值"]=round(data2["30日移动平均数"].rolling(n2,min_periods=1).mean(),2)        
    
    data2["均值"]=round(data2["目标值"].rolling(n2,min_periods=1).mean(),2)    
    
    data2["标准差"]=round(data2["目标值"].rolling(n2,min_periods=1).std(ddof=1),2)    
    data2["1STD"]=round((data2["均值"]+    data2["标准差"]),2)
    data2["2STD"]=round((data2["均值"]+    data2["标准差"]*2),2)    
    data2["UCL_3STD"]=round((data2["均值"]+    data2["标准差"]*3),2)    


    #data2["90日移动平均数"]=round(data2["报告总数"].rolling(n1,min_periods=1).mean(),2)
    #data2["365日移动平均数"]=round(data2["90日移动平均数"].rolling(n2,min_periods=1).mean(),2)    
    #data2["365日移动平均数标准差"]=round(data2["365日移动平均数"].rolling(n2,min_periods=1).std(ddof=1),2)    
    #data2["1STD"]=round((data2["365日移动平均数"]+    data2["365日移动平均数标准差"]),2)
    #data2["2STD"]=round((data2["365日移动平均数"]+    data2["365日移动平均数标准差"]*2),2)    
    #data2["UCL_3STD"]=round((data2["365日移动平均数"]+    data2["365日移动平均数标准差"]*3),2)        
    
    
    #data2["365日移动平均数"]=round(data2["报告总数"].rolling(n2,min_periods=1).mean(),2)    
    #data2["365日移动平均数标准差"]=round(data2["365日移动平均数"].rolling(n2,min_periods=1).std(ddof=1),2)
    
    #data2["1STD"]=round((data2["365日移动平均数"]+    data2["365日移动平均数标准差"]),2)
    #data2["2STD"]=round((data2["365日移动平均数"]+    data2["365日移动平均数标准差"]*2),2)    
    #data2["UCL_3STD"]=round((data2["365日移动平均数"]+    data2["365日移动平均数标准差"]*3),2)        




    #TABLE_tree_Level_2(data2,1,data2)
    DRAW_make_risk_plot(data2,"time",["30日移动平均数","UCL_3STD"], "折线图", 999)


def TOOLS_time_bak(data,timeq,methon):    
    """移动时间窗函数,备份用，废弃"""
    data2=data.drop_duplicates(["报告编码"]).groupby([timeq]).agg(
            报告总数=("报告编码","nunique"),
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),            
            ).sort_values(by=timeq, ascending=[True], na_position="last").reset_index()    
        
            
            
    data2=data2.set_index(timeq)

    data2=data2.resample('D').asfreq(fill_value=0)
    
    data2["time"]=data2.index.values
    data2["time"]=pd.to_datetime(data2["time"], format="%Y/%m/%d").dt.date
    
    if methon==1:#只是时间处理的话
        #TABLE_tree_Level_2(data2.reset_index(drop=True),1,data2.reset_index(drop=True))
        return data2.reset_index(drop=True)
        
    data2["30天累计数"]=data2["报告总数"].rolling(30,min_periods=1).agg(lambda x:sum(x)).astype(int)
    data2["30天严重伤害累计数"]=data2["严重伤害数"].rolling(30,min_periods=1).agg(lambda x:sum(x)).astype(int)
    data2["30天死亡累计数"]=data2["死亡数量"].rolling(30,min_periods=1).agg(lambda x:sum(x)).astype(int)

    
    
    #data2["30mean"]=round(data2["30天累计数"].rolling(30,min_periods=1).mean(),2)
    #data2["30std"]=round(data2["30天累计数"].rolling(30,min_periods=1).std(ddof=1),2)
    #data2["30ci"]=round(data2["30天累计数"].rolling(30,min_periods=1).agg(lambda x:np.percentile(x, 97.5)),2)

        
    #data2["风险评分"]=data2["30天累计数"].max()+1    
    #risk1=(((data2["30天累计数"]>=3)&(data2["30天严重伤害累计数"]>=1))|(data2["30天累计数"]>=5)|(data2["30天死亡累计数"]>=1))
    #risk2=data2["30天累计数"]>=(data2["30mean"]+data2["30std"])
    #risk3=data2["30天累计数"]>=data2["30ci"]    


    
    #data2.loc[risk1, "风险评分"] = data2["风险评分"]+3    
    #data2.loc[risk1&risk2, "风险评分"] = data2["风险评分"]+1
    #data2.loc[risk1&risk3, "风险评分"] = data2["风险评分"]+1
    #data2.loc[risk1&risk4, "风险评分"] = data2["风险评分"]-1
        
    data2.loc[(((data2["30天累计数"]>=3)&(data2["30天严重伤害累计数"]>=1))|(data2["30天累计数"]>=5)|(data2["30天死亡累计数"]>=1)), "关注区域"] = data2["30天累计数"]    
    
    #pd.set_option('display.max_rows', None)
    #print(data2)
    #TABLE_tree_Level_2(data2,1,data2)
    DRAW_make_risk_plot(data2,"time",["30天累计数","30天严重伤害累计数","关注区域"], "折线图", 999)



def TOOLS_keti(data):
    """日期预警功能"""
    import datetime
    
    def keti(timex,data0):
        if ini["模式"]=="药品":
            kx = pd.read_excel(peizhidir+"0（范例）预警参数.xlsx", header=0, sheet_name="药品").reset_index(drop=True)
        if ini["模式"]=="器械":
            kx = pd.read_excel(peizhidir+"0（范例）预警参数.xlsx", header=0, sheet_name="器械").reset_index(drop=True)    
        if ini["模式"]=="化妆品":
            kx = pd.read_excel(peizhidir+"0（范例）预警参数.xlsx", header=0, sheet_name="化妆品").reset_index(drop=True)                
        k1=kx["权重"][0] #严重比
        k2=kx["权重"][1] #单位数量        
        k3=kx["权重"][2] #批号或型号集中度权重
        k4=kx["权重"][3] #高度关注关键字（一级）        
        k4_values=kx["值"][3] #高度关注关键字（一级） 值    
        
        k5=kx["权重"][4] #高度关注关键字（二级）        
        k5_values=kx["值"][4] #高度关注关键字（二级） 值
        
        k6=kx["权重"][5] #减分项目        
        k6_values=kx["值"][5] #减分项目

        k7=kx["权重"][6] #重点产品及关注限        
        k7_values=kx["值"][6] #重点产品及关注限        
                                
        lastdayfrom = pd.to_datetime(timex)
        data2=data0.copy().set_index('报告日期')
        data2=data2.sort_index()
        if ini["模式"]=="器械":        
            data2["关键字查找列"]=data2["器械故障表现"].astype(str)+data2["伤害表现"].astype(str)+data2["使用过程"].astype(str)+data2["事件原因分析描述"].astype(str)+data2["初步处置情况"].astype(str)#器械故障表现|伤害表现|使用过程|事件原因分析描述|初步处置情况
        else:
            data2["关键字查找列"]=data2["器械故障表现"].astype(str)
        data2.loc[data2["关键字查找列"].str.contains(k4_values, na=False), "高度关注关键字"]  = 1
        data2.loc[data2["关键字查找列"].str.contains(k5_values, na=False), "二级敏感词"]  = 1    
        data2.loc[data2["关键字查找列"].str.contains(k6_values, na=False), "减分项"]  = 1    
                    
        data30 = data2.loc[lastdayfrom - pd.Timedelta(days=30):lastdayfrom].reset_index()
        data365=data2.loc[lastdayfrom - pd.Timedelta(days=365):lastdayfrom].reset_index()
        
        

        #当月数据评分
        df301=data30.groupby(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"]).agg(
            证号计数=("报告编码","nunique"),
            批号个数=("产品批号","nunique"),
            批号列表=("产品批号",STAT_countx),    
            型号个数=("型号","nunique"),
            型号列表=("型号",STAT_countx),        
            规格个数=("规格","nunique"),    
            规格列表=("规格",STAT_countx),        
            ).sort_values(by="证号计数", ascending=[False], na_position="last").reset_index()    

        df302=data30.drop_duplicates(["报告编码"]).groupby(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"]).agg(
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),                    
            待评价数=("持有人报告状态",lambda x: STAT_countpx(x.values,"待评价")),
            严重伤害待评价数=("伤害与评价",lambda x: STAT_countpx(x.values,"严重伤害待评价")),
            高度关注关键字=("高度关注关键字","sum"),    
            二级敏感词=("二级敏感词","sum"),
            减分项=("减分项","sum"),            
            ).reset_index()    
        
        df30=pd.merge(df301,  df302,on=["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"], how="left")    


        
    
        df30xinghao=data30.groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","型号"]).agg(
            型号计数=("报告编码","nunique"),    
            ).sort_values(by="型号计数", ascending=[False], na_position="last").reset_index()        
        df30xinghao=df30xinghao.drop_duplicates("注册证编号/曾用注册证编号")        
            
        df30wu=data30.drop_duplicates(["报告编码"]).groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","产品批号"]).agg(
            批号计数=("报告编码","nunique"),    
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            ).sort_values(by="批号计数", ascending=[False], na_position="last").reset_index()

                    
            
        df30wu["风险评分-影响"]=0        
        df30wu["评分说明"]=""        
        df30wu.loc[((df30wu["批号计数"]>=3)&(df30wu["严重伤害数"]>=1)&(df30wu["产品类别"]!="有源"))|((df30wu["批号计数"]>=5)&(df30wu["产品类别"]!="有源")), "风险评分-影响"] = df30wu["风险评分-影响"]+3    
        df30wu.loc[(df30wu["风险评分-影响"]>=3), "评分说明"] = df30wu["评分说明"]+"●符合省中心无源规则+3;"    
        

        
        df30wu=df30wu.sort_values(by="风险评分-影响", ascending=[False], na_position="last").reset_index(drop=True)    
        df30wu=df30wu.drop_duplicates("注册证编号/曾用注册证编号")
        df30xinghao=df30xinghao[["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","型号","型号计数"]]    
        df30wu=df30wu[["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","产品批号","批号计数","风险评分-影响","评分说明"]]
        df30=pd.merge(df30, df30xinghao, on=["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号"], how="left")
    
        df30=pd.merge(df30, df30wu, on=["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号"], how="left")        

        #TABLE_tree_Level_2(df30,1,data30)        
        #符合省中心规则打分（因为是针对证号，按有源标准）
        df30.loc[((df30["证号计数"]>=3)&(df30["严重伤害数"]>=1)&(df30["产品类别"]=="有源"))|((df30["证号计数"]>=5)&(df30["产品类别"]=="有源")), "风险评分-影响"] = df30["风险评分-影响"]+3    
        df30.loc[(df30["风险评分-影响"]>=3)&(df30["产品类别"]=="有源"), "评分说明"] = df30["评分说明"]+"●符合省中心有源规则+3;"    


                
        #针对死亡
        df30.loc[(df30["死亡数量"]>=1), "风险评分-影响"] = df30["风险评分-影响"]+10    
        df30.loc[(df30["风险评分-影响"]>=10), "评分说明"] = df30["评分说明"]+"存在死亡报告;"    
        
        #严重比评分
        fen_yanzhong=round(k1*(df30["严重伤害数"]/df30["证号计数"]),2)
        df30["风险评分-影响"] = df30["风险评分-影响"]+    fen_yanzhong
        df30["评分说明"] = df30["评分说明"]+"严重比评分"+fen_yanzhong.astype(str)+";"            
        
        #报告单位数评分
        fen_danwei=round(k2*(np.log(df30["单位个数"])),2)
        df30["风险评分-影响"] = df30["风险评分-影响"]+    fen_danwei
        df30["评分说明"] = df30["评分说明"]+"报告单位评分"+fen_danwei.astype(str)+";"                
        
        #批号型号集中度评分
        df30.loc[(df30["产品类别"]=="有源")&(df30["证号计数"]>=3), "风险评分-影响"] = df30["风险评分-影响"]+k3*df30["型号计数"]/df30["证号计数"]            
        df30.loc[(df30["产品类别"]=="有源")&(df30["证号计数"]>=3), "评分说明"] = df30["评分说明"]+"型号集中度评分"+(round(k3*df30["型号计数"]/df30["证号计数"],2)).astype(str)+";"    
        df30.loc[(df30["产品类别"]!="有源")&(df30["证号计数"]>=3), "风险评分-影响"] = df30["风险评分-影响"]+k3*df30["批号计数"]/df30["证号计数"]            
        df30.loc[(df30["产品类别"]!="有源")&(df30["证号计数"]>=3), "评分说明"]  = df30["评分说明"]+"批号集中度评分"+(round(k3*df30["批号计数"]/df30["证号计数"],2)).astype(str)+";"            

        #高度关注关键字（一级）
        df30.loc[(df30["高度关注关键字"]>=1), "风险评分-影响"]  = df30["风险评分-影响"]+k4
        df30.loc[(df30["高度关注关键字"]>=1), "评分说明"] = df30["评分说明"]+"●含有高度关注关键字评分"+str(k4)+"；"                                    

        #二级敏感词
        df30.loc[(df30["二级敏感词"]>=1), "风险评分-影响"]  = df30["风险评分-影响"]+k5
        df30.loc[(df30["二级敏感词"]>=1), "评分说明"] = df30["评分说明"]+"含有二级敏感词评分"+str(k5)+"；"        
        
        #减分项目
        df30.loc[(df30["减分项"]>=1), "风险评分-影响"]  = df30["风险评分-影响"]+k6
        df30.loc[(df30["减分项"]>=1), "评分说明"] = df30["评分说明"]+"减分项评分"+str(k6)+"；"    
                
        #历史比较（月份）
        df365month=Countall(data365).df_findrisk("事件发生月份")
        df365month=df365month.drop_duplicates("注册证编号/曾用注册证编号")    
        df365month=df365month[["注册证编号/曾用注册证编号","均值","标准差","CI上限"]]
        df30=pd.merge(df30, df365month, on=["注册证编号/曾用注册证编号"], how="left")    
    
        df30["风险评分-月份"]=1
        df30["mfc"]=""
        df30.loc[((df30["证号计数"]>df30["均值"])&(df30["标准差"].astype(str)=="nan")), "风险评分-月份"]  = df30["风险评分-月份"]+1
        df30.loc[(df30["证号计数"]>df30["均值"]),  "mfc"] = "月份计数超过历史均值"+df30["均值"].astype(str)+"；"    
            
        df30.loc[(df30["证号计数"]>=(df30["均值"]+df30["标准差"]))&(df30["证号计数"]>=3), "风险评分-月份"]  = df30["风险评分-月份"]+1
        df30.loc[(df30["证号计数"]>=(df30["均值"]+df30["标准差"]))&(df30["证号计数"]>=3), "mfc"] = "月份计数超过3例超过历史均值一个标准差("+df30["标准差"].astype(str)+")；"            
        
        df30.loc[(df30["证号计数"]>=df30["CI上限"])&(df30["证号计数"]>=3), "风险评分-月份"]  = df30["风险评分-月份"]+2
        df30.loc[(df30["证号计数"]>=df30["CI上限"])&(df30["证号计数"]>=3),  "mfc"] = "月份计数超过3例且超过历史95%CI上限("+df30["CI上限"].astype(str)+")；"            

        df30.loc[(df30["证号计数"]>=df30["CI上限"])&(df30["证号计数"]>=5), "风险评分-月份"]  = df30["风险评分-月份"]+1
        df30.loc[(df30["证号计数"]>=df30["CI上限"])&(df30["证号计数"]>=5),  "mfc"] = "月份计数超过5例且超过历史95%CI上限("+df30["CI上限"].astype(str)+")；"            

        df30.loc[(df30["证号计数"]>=df30["CI上限"])&(df30["证号计数"]>=7), "风险评分-月份"]  = df30["风险评分-月份"]+1
        df30.loc[(df30["证号计数"]>=df30["CI上限"])&(df30["证号计数"]>=7),  "mfc"] = "月份计数超过7例且超过历史95%CI上限("+df30["CI上限"].astype(str)+")；"            

        df30.loc[(df30["证号计数"]>=df30["CI上限"])&(df30["证号计数"]>=9), "风险评分-月份"]  = df30["风险评分-月份"]+1
        df30.loc[(df30["证号计数"]>=df30["CI上限"])&(df30["证号计数"]>=9),  "mfc"] = "月份计数超过9例且超过历史95%CI上限("+df30["CI上限"].astype(str)+")；"            


        
        df30.loc[(df30["证号计数"]>=3)&(df30["标准差"].astype(str)=="nan"), "风险评分-月份"]  = 3
        df30.loc[(df30["证号计数"]>=3)&(df30["标准差"].astype(str)=="nan"),  "mfc"] = "无历史数据但数量超过3例；"            


        df30["评分说明"]=df30["评分说明"]+"●●证号数量："+df30["证号计数"].astype(str)+";"+ df30["mfc"]    
        del df30["mfc"]
        df30=df30.rename(columns={"均值": "月份均值","标准差": "月份标准差","CI上限": "月份CI上限"})
        

        #历史比较（批号）
        df365month=Countall(data365).df_findrisk("产品批号")
        df365month=df365month.drop_duplicates("注册证编号/曾用注册证编号")    
        df365month=df365month[["注册证编号/曾用注册证编号","均值","标准差","CI上限"]]
        df30=pd.merge(df30, df365month, on=["注册证编号/曾用注册证编号"], how="left")    
    
        df30["风险评分-批号"]=1
        df30.loc[(df30["产品类别"]!="有源"), "评分说明"] =df30["评分说明"]+"●●高峰批号数量："+df30["批号计数"].astype(str)+";"
        
        df30.loc[(df30["批号计数"]>df30["均值"]), "风险评分-批号"]  = df30["风险评分-批号"]+1
        df30.loc[(df30["批号计数"]>df30["均值"]),  "评分说明"] = df30["评分说明"]+"高峰批号计数超过历史均值"+df30["均值"].astype(str)+"；"        
        df30.loc[(df30["批号计数"]>(df30["均值"]+df30["标准差"]))&(df30["批号计数"]>=3), "风险评分-批号"]  = df30["风险评分-批号"]+1
        df30.loc[(df30["批号计数"]>(df30["均值"]+df30["标准差"]))&(df30["批号计数"]>=3), "评分说明"] = df30["评分说明"]+"高峰批号计数超过3例超过历史均值一个标准差("+df30["标准差"].astype(str)+")；"            
        df30.loc[(df30["批号计数"]>df30["CI上限"])&(df30["批号计数"]>=3), "风险评分-批号"]  = df30["风险评分-批号"]+1
        df30.loc[(df30["批号计数"]>df30["CI上限"])&(df30["批号计数"]>=3),  "评分说明"] = df30["评分说明"]+"高峰批号计数超过3例且超过历史95%CI上限("+df30["CI上限"].astype(str)+")；"            
        
        df30.loc[(df30["批号计数"]>=3)&(df30["标准差"].astype(str)=="nan"), "风险评分-月份"]  = 3
        df30.loc[(df30["批号计数"]>=3)&(df30["标准差"].astype(str)=="nan"),  "评分说明"] = df30["评分说明"]+"无历史数据但数量超过3例；"                
        df30=df30.rename(columns={"均值": "高峰批号均值","标准差": "高峰批号标准差","CI上限": "高峰批号CI上限"})

        
        df30["风险评分-影响"]=round(df30["风险评分-影响"],2)
        df30["风险评分-月份"]=round(df30["风险评分-月份"],2)
        df30["风险评分-批号"]=round(df30["风险评分-批号"],2)
        
        df30["总体评分"]=df30["风险评分-影响"].copy()
        df30["关注建议"]=""
        df30.loc[(df30["风险评分-影响"]>=3),  "关注建议"]=df30["关注建议"]+"●建议关注(影响范围)；" 
        df30.loc[(df30["风险评分-月份"]>=3),  "关注建议"]=df30["关注建议"]+"●建议关注(当月数量异常)；"
        df30.loc[(df30["风险评分-批号"]>=3),  "关注建议"]=df30["关注建议"]+"●建议关注(高峰批号数量异常)。"        
        #df30.loc[(df30["风险评分-影响"]>=3),  "总体评分"]=df30["总体评分"]    +100
        #df30.loc[(df30["风险评分-月份"]>=3),  "总体评分"]=df30["总体评分"]+100
        #df30.loc[(df30["风险评分-批号"]>=3),  "总体评分"]=df30["总体评分"]    +100    
        df30.loc[(df30["风险评分-月份"]>=df30["风险评分-批号"]),  "总体评分"]=df30["风险评分-影响"]*df30["风险评分-月份"]
        df30.loc[(df30["风险评分-月份"]<df30["风险评分-批号"]),  "总体评分"]=df30["风险评分-影响"]*df30["风险评分-批号"]

        df30["总体评分"]=round(df30["总体评分"],2)        
        df30["评分说明"]=df30["关注建议"]    +df30["评分说明"]        
        df30=df30.sort_values(by=["总体评分","风险评分-影响"], ascending=[False,False], na_position="last").reset_index(drop=True)
        
        #增加故障分类
        df30["主要故障分类"]=""
        for ids, cols in df30.iterrows():
            data30s =data30[(data30["注册证编号/曾用注册证编号"]==cols["注册证编号/曾用注册证编号"])].copy() 
            if cols["总体评分"]>=float(k7):
                if cols["规整后品类"]!="N":
                    usheet=Countall(data30s).df_psur("特定品种",cols["规整后品类"])
                elif cols["产品类别"]=="无源":
                    usheet=Countall(data30s).df_psur("通用无源")
                elif cols["产品类别"]=="有源":
                    usheet=Countall(data30s).df_psur("通用有源")        
                elif cols["产品类别"]=="体外诊断试剂":
                    usheet=Countall(data30s).df_psur("体外诊断试剂")                
                
                df=usheet[["事件分类","总数量"]].copy()
                m=""
                for ids2, cols2 in df.iterrows(): 
                    m=m+str(cols2["事件分类"])+":"+str(cols2["总数量"])+";"
                df30.loc[ids,"主要故障分类"]=m
            else:
                break
            
            
            
        df30=df30[["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号","证号计数","严重伤害数","死亡数量","总体评分","风险评分-影响","风险评分-月份","风险评分-批号","主要故障分类","评分说明","单位个数","单位列表","批号个数","批号列表","型号个数","型号列表","规格个数","规格列表","待评价数","严重伤害待评价数","高度关注关键字","二级敏感词","月份均值","月份标准差","月份CI上限","高峰批号均值","高峰批号标准差","高峰批号CI上限","型号","型号计数","产品批号","批号计数"]]
        df30["报表类型"]="dfx_zhenghao"
        TABLE_tree_Level_2(df30,1,data30,data365)
        pass            
    

    se = Toplevel()
    se.title('风险预警')
    sw_se = se.winfo_screenwidth()
    #得到屏幕宽度
    sh_se = se.winfo_screenheight()
    #得到屏幕高度
    ww_se = 350
    wh_se = 35
    #窗口宽高为100
    x_se = (sw_se-ww_se) / 2
    y_se = (sh_se-wh_se) / 2
    se.geometry("%dx%d+%d+%d" %(ww_se,wh_se,x_se,y_se)) 

    import_se=Label(se,text="预警日期：")
    import_se.grid(row=1, column=0, sticky="w")
    import_se_entry=Entry(se, width = 30)
    import_se_entry.insert(0,datetime.date.today())
    import_se_entry.grid(row=1, column=1, sticky="w")


    
    btn_se=Button(se,text="确定",width=10,command=lambda:TABLE_tree_Level_2(keti(import_se_entry.get(),data),1,data))
    btn_se.grid(row=1, column=3, sticky="w")

    pass
    
def TOOLS_count_elements(df, elements, column_name):
    """统计报告中的元素-器械故障表现各个细项"""
    # 创建一个新的 DataFrame，其中包含特定列中包含列表中每个元素的个数
    new_df = pd.DataFrame(columns=[column_name, 'count'])
    count_x=[]
    keyword_x=[]

    # 遍历列表中的每个元素
    for element in TOOLS_get_list(elements):
        # 计算特定列中包含元素的个数
        count = df[df[column_name].str.contains(element)].shape[0]
        
        # 如果个数不为 0，则将其添加到新的 DataFrame 中
        if count > 0:
            count_x.append(count)    
            keyword_x.append(element)    
    result=pd.DataFrame({"index":keyword_x,'计数': count_x})
    result["构成比(%)"]=round(100*result["计数"]/result["计数"].sum(),2)
    result["报表类型"]="dfx_deepvie2"+"_"+str([column_name])

    return result
        
def TOOLS_autocount(mydata, methon):
    """自动简报核心文件"""
    data_org = pd.read_excel(
        peizhidir+"share_adrmdr_pinggu_上报单位.xls", sheet_name="监测机构", header=0, index_col=0
    ).reset_index()
    data_user = pd.read_excel(
        peizhidir+"share_adrmdr_pinggu_上报单位.xls", sheet_name="报告单位", header=0, index_col=0
    ).reset_index()
    data_user_erji=data_user[(data_user["是否属于二级以上医疗机构"]=="是")]
        
    
    if methon == "药品":
        mydata = mydata.reset_index(drop=True)
        if "再次使用可疑药是否出现同样反应" not in mydata.columns:
            showinfo(title="错误信息", message="导入的疑似不是药品报告表。")
            return 0

        orgcount0 = Countall(mydata).df_org("监测机构")
        orgcount0=pd.merge(orgcount0, data_org, on="监测机构", how="left")
        orgcount0=orgcount0[["监测机构序号","监测机构","药品数量指标","报告数量","审核通过数","新严比","严重比","超时比"]].sort_values(by=["监测机构序号"], ascending=True, na_position="last" ).fillna(0)
        a=["药品数量指标","审核通过数","报告数量"]
        orgcount0[a] = orgcount0[a].apply(lambda x: x.astype(int) )    
        
        usercount0 = Countall(mydata).df_user()
        usercount0=pd.merge(usercount0, data_user, on=["监测机构","单位名称"], how="left")
        usercount0=pd.merge(usercount0, data_org[["监测机构序号","监测机构"]], on="监测机构", how="left")
        #usercount0=usercount0.sort_values(by=["报告数量"], ascending=False, na_position="last" )
        usercount0=usercount0[["监测机构序号","监测机构","单位名称","药品数量指标","报告数量","审核通过数","新严比","严重比","超时比"]].sort_values(by=["监测机构序号","报告数量"], ascending=[True,False], na_position="last" ).fillna(0)
        a=["药品数量指标","审核通过数","报告数量"]
        usercount0[a] = usercount0[a].apply(lambda x: x.astype(int) )    

        erji=pd.merge(data_user_erji,usercount0, on=["监测机构","单位名称"], how="left").sort_values(by=["监测机构"], ascending=True, na_position="last" ).fillna(0)
        erji=erji[(erji["审核通过数"]<1)]
        erji=erji[["监测机构","单位名称","报告数量","审核通过数","严重比","超时比"]]

    if methon == "器械":
        mydata = mydata.reset_index(drop=True)
        if "产品编号" not in mydata.columns:
            showinfo(title="错误信息", message="导入的疑似不是器械报告表。")
            return 0

        orgcount0 = Countall(mydata).df_org("监测机构")
        orgcount0=pd.merge(orgcount0, data_org, on="监测机构", how="left")
        orgcount0=orgcount0[["监测机构序号","监测机构","器械数量指标","报告数量","审核通过数","严重比","超时比"]].sort_values(by=["监测机构序号"], ascending=True, na_position="last" ).fillna(0)
        a=["器械数量指标","审核通过数","报告数量"]
        orgcount0[a] = orgcount0[a].apply(lambda x: x.astype(int) )    
        
        usercount0 = Countall(mydata).df_user()
        usercount0=pd.merge(usercount0, data_user, on=["监测机构","单位名称"], how="left")
        usercount0=pd.merge(usercount0, data_org[["监测机构序号","监测机构"]], on="监测机构", how="left")
        #usercount0=usercount0.sort_values(by=["报告数量"], ascending=False, na_position="last" )
        usercount0=usercount0[["监测机构序号","监测机构","单位名称","器械数量指标","报告数量","审核通过数","严重比","超时比"]].sort_values(by=["监测机构序号","报告数量"], ascending=[True,False], na_position="last" ).fillna(0)
        a=["器械数量指标","审核通过数","报告数量"]

        usercount0[a] = usercount0[a].apply(lambda x: x.astype(int) )    

        erji=pd.merge(data_user_erji,usercount0, on=["监测机构","单位名称"], how="left").sort_values(by=["监测机构"], ascending=True, na_position="last" ).fillna(0)
        erji=erji[(erji["审核通过数"]<1)]
        erji=erji[["监测机构","单位名称","报告数量","审核通过数","严重比","超时比"]]
                  
 
    if methon == "化妆品":
        mydata = mydata.reset_index(drop=True)
        if "初步判断" not in mydata.columns:
            showinfo(title="错误信息", message="导入的疑似不是化妆品报告表。")
            return 0

        orgcount0 = Countall(mydata).df_org("监测机构")
        orgcount0=pd.merge(orgcount0, data_org, on="监测机构", how="left")
        orgcount0=orgcount0[["监测机构序号","监测机构","化妆品数量指标","报告数量","审核通过数",'报告分数']].sort_values(by=["监测机构序号"], ascending=True, na_position="last" ).fillna(0)
        a=["化妆品数量指标","审核通过数","报告数量"]
        orgcount0[a] = orgcount0[a].apply(lambda x: x.astype(int) )    
        
        usercount0 = Countall(mydata).df_user()
        usercount0=pd.merge(usercount0, data_user, on=["监测机构","单位名称"], how="left")
        usercount0=pd.merge(usercount0, data_org[["监测机构序号","监测机构"]], on="监测机构", how="left")
        usercount0=usercount0[["监测机构序号","监测机构","单位名称","化妆品数量指标","报告数量","审核通过数",'报告分数']].sort_values(by=["监测机构序号","报告数量"], ascending=[True,False], na_position="last" ).fillna(0)
        a=["化妆品数量指标","审核通过数","报告数量"]
        usercount0[a] = usercount0[a].apply(lambda x: x.astype(int) )    

        erji=pd.merge(data_user_erji,usercount0, on=["监测机构","单位名称"], how="left").sort_values(by=["监测机构"], ascending=True, na_position="last" ).fillna(0)
        erji=erji[(erji["审核通过数"]<1)]
        erji=erji[["监测机构","单位名称","报告数量","审核通过数",'报告分数']]

    file_path_flhz = filedialog.asksaveasfilename(
        title=u"保存文件",
        initialfile=methon,
        defaultextension="xls",
        filetypes=[("Excel 97-2003 工作簿", "*.xls")],
    )
    writer = pd.ExcelWriter(file_path_flhz,engine="xlsxwriter")  # engin="xlsxwriter"
    orgcount0.to_excel(writer, sheet_name="监测机构")
    usercount0.to_excel(writer, sheet_name="上报单位")
    erji.to_excel(writer, sheet_name="未上报的二级以上医疗机构")
    writer.close()
    showinfo(title="提示", message="文件写入成功。")

def TOOLS_web_view(ori_data):    
    """web_view"""
    import pybi as pbi
    writer = pd.ExcelWriter("temp_webview.xls")
    ori_data.to_excel(writer, sheet_name="temp_webview")
    writer.close()
    ori_data=pd.read_excel("temp_webview.xls", header=0, sheet_name=0).reset_index(drop=True)
    data2=pbi.set_source(ori_data)
    with pbi.flowBox():
        for col in ori_data.columns:
            pbi.add_slicer(data2[col])
    pbi.add_table(data2)
    rst="temp_webview.html"
    pbi.to_html(rst)     
    webbrowser.open_new_tab(rst)    



                     
def TOOLS_Autotable_0(tips,methon,*xyz):
    """自助图表的辅助文件"""
   
    ori_list=[xyz[0],xyz[1],xyz[2]] 

    aoto_index= list(set([i for i in ori_list if i!='']))
    aoto_index.sort(key = ori_list.index)
    if len(aoto_index)==0:
        showinfo(title="提示信息", message="分组项请选择至少一列。")    
        return 0
    fulltips=[xyz[3],xyz[4]]
    if (xyz[3]=="" or xyz[4]=="") and methon in ["数据透视","分组统计"]:
        if "报告编码" in tips.columns:
            fulltips[0]="报告编码"
            fulltips[1]="nunique"
            text.insert(END,"值项未配置,将使用报告编码进行唯一值计数。")
        else:
            showinfo(title="提示信息", message="值项未配置。")    
            return 0  
        
    if xyz[4]=="计数":
        fulltips[1]="count"    
    elif xyz[4]=="求和":
        fulltips[1]="sum"   
    elif xyz[4]=="唯一值计数":
        fulltips[1]="nunique"                

           
    if methon == "分组统计": 
        TABLE_tree_Level_2(TOOLS_deep_view(tips, aoto_index,fulltips,0),1,tips)   
  
    if methon == "数据透视": 
        TABLE_tree_Level_2(TOOLS_deep_view(tips, aoto_index,fulltips,1),1,tips)   
        
    if methon == "描述性统计(X)": 
        TABLE_tree_Level_2(tips[aoto_index].describe().reset_index(),1,tips)

        
    if methon == "拆分成字典(X-Y)": 
        

        data=tips.copy()
        data["c"]="c"
        listxa=data.groupby([xyz[0]]).agg(计数=("c","count") ).reset_index()
        listx2=listxa.copy()
        listx2[xyz[0]]=listx2[xyz[0]].str.replace("*","",regex=False)
        listx2["所有项目"]=""        #20231011
        k=1
        p=int(len(listx2))
        for ids,cols in listx2.iterrows():
            #print(cols["计数项目"])
            datam = data[(data[xyz[0]] == cols[xyz[0]])]
            #datam=data.loc[data["产品名称"].str.contains(cols["计数项目"], na=False)].copy()
            rm=str(Counter(TOOLS_get_list_r0("use("+str(xyz[1])+").file",datam,1000))).replace("Counter({", "{")
            rm=rm.replace("})", "}")
            import ast
            user_dict = ast.literal_eval(rm)    
            list_all = TOOLS_easyreadT(pd.DataFrame([user_dict]))
            list_all = list_all.rename(columns={"逐条查看": "名称规整"})
            
            PROGRAM_change_schedule(k,p)
            k=k+1
            for idc,colc in list_all.iterrows(): #20231011
                    if  "分隔符" not in  colc["条目"]:
                        kde="'"+str(colc["条目"])+"':"+str(colc["详细描述T"])+","                
                        listx2.loc[ids,"所有项目"]=listx2.loc[ids,"所有项目"]+kde    
            
        listx2["所有项目"]="{"+listx2["所有项目"]+"}" #20221011    
        listx2["报表类型"]="dfx_deepview_"+str([xyz[0]])            

        TABLE_tree_Level_2(listx2.sort_values(by="计数", ascending=[False], na_position="last"),1,data)
        
    if methon == "追加外部表格信息": 
        allfileName = filedialog.askopenfilenames(
            filetypes=[("XLS", ".xls"), ("XLSX", ".xlsx")]
        )
        k = [pd.read_excel(x, header=0, sheet_name=0) for x in allfileName] #,index_col=0
        out_data = pd.concat(k, ignore_index=True).drop_duplicates(aoto_index)   
        df_empty = pd.merge(tips, out_data, on=aoto_index, how="left")
        TABLE_tree_Level_2(df_empty,1,df_empty) 

    if methon == "添加到外部表格": 
        allfileName = filedialog.askopenfilenames(
            filetypes=[("XLS", ".xls"), ("XLSX", ".xlsx")]
        )
        k = [pd.read_excel(x, header=0, sheet_name=0) for x in allfileName] #,index_col=0
        out_data = pd.concat(k, ignore_index=True).drop_duplicates()   
        df_empty = pd.merge(out_data, tips.drop_duplicates(aoto_index), on=aoto_index, how="left")
        TABLE_tree_Level_2(df_empty,1,df_empty) 

 
    if methon == "饼图(XY)":    
        DRAW_make_one(tips, "饼图", xyz[0],xyz[1],"饼图")
    if methon == "柱状图(XY)":     
        DRAW_make_one(tips, "柱状图", xyz[0],xyz[1],"柱状图") 
    if methon == "折线图(XY)":   
        DRAW_make_one(tips, "折线图", xyz[0],xyz[1],"折线图")        
    if methon == "托帕斯图(XY)":   
        DRAW_make_one(tips, "托帕斯图", xyz[0],xyz[1],"托帕斯图")                      
    if methon == "堆叠柱状图（X-YZ）":     #DRAW_make_mutibar(data, y, y1, index, yL, y1L, title):  # y=大数，y1=小数，index=标签  
        DRAW_make_mutibar(tips,ori_list[1], ori_list[2],  ori_list[0],ori_list[1],ori_list[2], "堆叠柱状图")




  
######################################################################
#其他小型函数
######################################################################
    
def STAT_countx(x):
    """所有成分关键字计数,返回一个字典""" 
    return x.value_counts().to_dict()
    
def STAT_countpx(x,y):
    """特定成分关键字计数,返回一个数值""" 
    return len(x[(x==y)])#.values
    
def STAT_countnpx(x,y):
    """不含特定成分关键字计数,返回一个数值""" 
    return len(x[(x not in y)])#.values
    
def STAT_get_max(df):
    """返回最大值""" 
    return df.value_counts().max()

def STAT_get_mean(df):
    """返回平均值""" 
    return round(df.value_counts().mean(),2)
    
def STAT_get_std(df):
    """返回标准差""" 
    return round(df.value_counts().std(ddof=1),2)
    
def STAT_get_95ci(data):
    """返回95%置信区间上限""" 
    confidence_level = 0.95  
    df2=data.value_counts().tolist()
    if len(df2)<30:
        result=st.t.interval(confidence_level, df=len(df2)-1,loc=np.mean(df2),scale=st.sem(df2))
    else:
        result=st.norm.interval(confidence_level,loc=np.mean(df2),scale=st.sem(df2))
    return round(result[1],2)#stats.norm.interval(0.95, loc=mean, scale=std)
    
def STAT_get_mean_std_ci(x,allx):
    """一次性返回MEAN,STD,CI,用于关键字统计模块"""     
    warnings.filterwarnings("ignore")
    dfe=TOOLS_strdict_to_pd(str(x))["content"].values/allx    
    xmean=round(dfe.mean(),2)
    xstd=round(dfe.std(ddof=1),2)

    if len(dfe)<30:
        xci=st.t.interval(0.95, df=len(dfe)-1,loc=np.mean(dfe),scale=st.sem(dfe))
    else:
        xci=st.norm.interval(0.95,loc=np.mean(dfe),scale=st.sem(dfe))    
    #xci=round(np.percentile(dfe, 97.5),2)
    
                
    return pd.Series((xmean, xstd, xci[1]))    
    
def STAT_findx_value(x,who):
    """一次性返回符合某个对象的值"""     
    warnings.filterwarnings("ignore")
    dfe=TOOLS_strdict_to_pd(str(x))    
    #print(dfe)
    result=dfe.where(dfe["index"] == str(who))    
    print(result)        
    return result    
    
def STAT_judge_x(a,b):
    """PSUR模块的辅助统计函数"""     
    for keyword_value1 in b:
        if a.find(keyword_value1)>-1:
            return 1
            
def STAT_recent30(data,j_target):
    """判断最近30天报告的风险（非发生日期）"""             
    import datetime    
    #print("rsdt")
    #print(data["报告日期"])
    #print(datetime.date.today()- datetime.timedelta(days = 30)  )
    data_current30=data[(data["报告日期"].dt.date> (datetime.date.today()- datetime.timedelta(days = 30)  ))]
    
    D30=data_current30.drop_duplicates(["报告编码"]).groupby(j_target).agg(
                最近30天报告数=("报告编码","nunique"),
                最近30天报告严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
                最近30天报告死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),
                最近30天报告单位个数=("单位名称","nunique"),                
                ).reset_index()        
    D30=STAT_basic_risk(D30,"最近30天报告数","最近30天报告严重伤害数","最近30天报告死亡数量","最近30天报告单位个数")    .fillna(0)
        
    D30=D30.rename(columns={"风险评分": "最近30天风险评分"})    
    return D30

            
def STAT_PPR_ROR_1(expose_columns, expose_value, keyword_columns, keyword_value, data):
    """根据原始文件计算出某一产品的abcd，进而计算STAT_PPR_ROR_0，返回一个包括关键字名称，目标药物中包括特定关键字的报告数量和比例，STAT_PPR_ROR_0计算结果，四分表（abcd）等信息列表"""
    # expose_columns（目标药物列名）,expose_value（目标药物名称）,keyword_columns（关键字所在列）,keyword_value（关键字名称）,data（传入的源文件）
    #prinf(expose_columns+expose_value)
    ab = data[(data[expose_columns]==expose_value)] # 所有目标药物
    a = ab.loc[ab[keyword_columns].str.contains(keyword_value, na=False)]  # 目标药物包括关键字
    cd = data[(data[expose_columns]!=expose_value)]  # 所有非目标药物
    c = cd.loc[cd[keyword_columns].str.contains(keyword_value, na=False)]  # 非目标药物包括关键字
    table = (len(a), (len(ab) - len(a)), len(c), (len(cd) - len(c)))
    if len(a) > 0:
        count_x = STAT_PPR_ROR_0(len(a), (len(ab) - len(a)), len(c), (len(cd) - len(c)))
    else:
        count_x = (0, 0, 0, 0, 0)
    # ['特定关键字',"出现频次","占比","ROR值","ROR值的95CI%下限","PRR值","PRR值的95CI%下限"])#单品种
    #      0            1         2      3           4              5            6
    ex_0 = len(ab)
    if ex_0 == 0:
        ex_0 = 0.5
    return (
        keyword_value,
        len(a),
        round(len(a) / ex_0 * 100, 2),
        round(count_x[0], 2),
        round(count_x[1], 2),
        round(count_x[2], 2),
        round(count_x[3], 2),
        round(count_x[4], 2),
        str(table),
    )
    #          关键字名称，目标药物中包括关键字的报告数量和比例，STAT_PPR_ROR_0计算结果，四分表（abcd）


def STAT_basic_risk(df,a,b,c,d):    
    """改良的省中心预警规则"""
    df["风险评分"]=0
    df.loc[((df[a]>=3)&(df[b]>=1))|(df[a]>=5), "风险评分"] = df["风险评分"]+5    
    df.loc[(df[b]>=3), "风险评分"] = df["风险评分"]+1    
    df.loc[(df[c]>=1), "风险评分"] = df["风险评分"]+10        
    df["风险评分"] = df["风险评分"]+df[d]/100
    return df


def STAT_PPR_ROR_0(a, b, c, d):
    """根据某一产品的abcd，计算STAT_PPR_ROR_0及置信区间，返回ROR,ROR_CI_95[0],PRR,PRR_CI_95[0],X2（卡方值）"""
    # 比例不平衡四格表
    #            目标不良反应    其他不良反应
    # 目标药物        a                  b
    # 其他药物        c                  d
    if a * b * c * d == 0:
        a = a + 1
        b = b + 1
        c = c + 1
        d = d + 1
    PRR = (a / (a + b)) / (c / (c + d))
    PRR_SE = math.sqrt(1 / a - 1 / (a + b) + 1 / c - 1 / (c + d))
    PRR_CI_95 = (
        math.exp(math.log(PRR) - 1.96 * PRR_SE),
        math.exp(math.log(PRR) + 1.96 * PRR_SE),
    )
    ROR = (a / c) / (b / d)
    ROR_SE = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    ROR_CI_95 = (
        math.exp(math.log(ROR) - 1.96 * ROR_SE),
        math.exp(math.log(ROR) + 1.96 * ROR_SE),
    )
    X2 = ((a * b - b * c) * (a * b - b * c) * (a + b + c + d)) / (
        (a + b) * (c + d) * (a + c) * (b + d)
    )
    return ROR, ROR_CI_95[0], PRR, PRR_CI_95[0], X2

def STAT_find_keyword_risk(df,cols_list,main_col,target,allx):    
        """关键字评分及预警模块,cols_list为所要引入的列（列表形式），main_col统计对象列（关键字），target为月份、季度或者批号等,allx为证号总数量"""
        df=df.drop_duplicates(["报告编码"]).reset_index(drop=True)
        dfx_findrisk1=df.groupby(cols_list).agg(
            证号关键字总数量=(main_col,"count"),    
            包含元素个数=(target,"nunique"),
            包含元素=(target,STAT_countx),                
            ).reset_index()
        
        cols_list2=cols_list.copy()
        cols_list2.append(target)
        dfx_findrisk2=df.groupby(cols_list2).agg(
            计数=(target,"count"),
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),                            
            ).reset_index()    
        
        #算出批号等计数
        cols_list3=    cols_list2.copy()
        cols_list3.remove("关键字") #不含关键字的
        dfx_findrisk3=df.groupby(cols_list3).agg(
            该元素总数=(target,"count"),                        
            ).reset_index()    
                
        dfx_findrisk2["证号总数"]=allx
        dfx_findrisk=pd.merge(dfx_findrisk2,dfx_findrisk1,on=cols_list,how="left")#.reset_index()            
    
        
        
            
        if len(dfx_findrisk)>0:        
            dfx_findrisk[['数量均值', '数量标准差', '数量CI']] = dfx_findrisk.包含元素.apply(lambda x: STAT_get_mean_std_ci(x,1))        
            #dfx_findrisk[['比例均值', '比例标准差', '比例CI']] = dfx_findrisk.包含元素.apply(lambda x: STAT_get_mean_std_ci(x,dfx_findrisk[[target,"该元素总数"]]))        

        return dfx_findrisk        
    




def STAT_find_risk(df,cols_list,main_col,target):    
        """评分及预警模块,cols_list为所要引入的列（列表形式），main_col统计对象列（关键字），target为月份、季度或者批号等""" 
        df=df.drop_duplicates(["报告编码"]).reset_index(drop=True)
        dfx_findrisk1=df.groupby(cols_list).agg(
            证号总数量=(main_col,"count"),    
            包含元素个数=(target,"nunique"),
            包含元素=(target,STAT_countx),        
            均值=(target,STAT_get_mean),
            标准差=(target,STAT_get_std),
            CI上限=(target,STAT_get_95ci),                
            ).reset_index()
                    
        cols_list2=cols_list.copy()
        cols_list2.append(target)
        dfx_findrisk2=df.groupby(cols_list2).agg(
            计数=(target,"count"),
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),                            
            ).reset_index()                

        dfx_findrisk=pd.merge(dfx_findrisk2,dfx_findrisk1,on=cols_list,how="left")#.reset_index()    
                
        dfx_findrisk["风险评分"]=0
        dfx_findrisk["报表类型"]="dfx_findrisk"+target
        dfx_findrisk.loc[((dfx_findrisk["计数"]>=3)&(dfx_findrisk["严重伤害数"]>=1)|(dfx_findrisk["计数"]>=5)), "风险评分"] = dfx_findrisk["风险评分"]+5    
        dfx_findrisk.loc[(dfx_findrisk["计数"]>=(dfx_findrisk["均值"]+dfx_findrisk["标准差"])), "风险评分"] = dfx_findrisk["风险评分"]+1            
        dfx_findrisk.loc[(dfx_findrisk["计数"]>=dfx_findrisk["CI上限"]), "风险评分"] = dfx_findrisk["风险评分"]+1        
        dfx_findrisk.loc[(dfx_findrisk["严重伤害数"]>=3)&(dfx_findrisk["风险评分"]>=7), "风险评分"] = dfx_findrisk["风险评分"]+1    
        dfx_findrisk.loc[(dfx_findrisk["死亡数量"]>=1), "风险评分"] = dfx_findrisk["风险评分"]+10        
        dfx_findrisk["风险评分"] = dfx_findrisk["风险评分"]+dfx_findrisk["单位个数"]/100    
        dfx_findrisk =dfx_findrisk.sort_values(by="风险评分", ascending=[False], na_position="last").reset_index(drop=True)        

        return dfx_findrisk
        

        
######################################################################
#界面函数
######################################################################
def TABLE_tree_Level_2(ori_owercount_easyread, methon, ori, *others):  # methon=0表示原始报表那个层级，其他就使用传入文件。
    """-报表查看器"""
    #如果不是表格则返回0
    try:
        testtihs=ori_owercount_easyread.columns    
    except:
        return 0
        
    if "报告编码" in ori_owercount_easyread.columns:
        methon=0
    try:
        zte=len(np.unique(ori_owercount_easyread["注册证编号/曾用注册证编号"].values)) #看看是不是只有一个同注册证号产品的报告 zte=1
    except:
        zte=10
    #print(ini["源文件"]).head(10)    
    ##########报表查看器初始化模块#################
    treeQ = Toplevel()
    treeQ.title("报表查看器")
    sw_treeQ = treeQ.winfo_screenwidth()
    # 得到屏幕宽度
    sh_treeQ = treeQ.winfo_screenheight()
    # 得到屏幕高度
    ww_treeQ = 1350
    wh_treeQ = 600
    try:
        if others[0]=="tools_x":
           wh_treeQ = 60
    except:
            pass
    
    # 窗口宽高为100
    x_treeQ = (sw_treeQ - ww_treeQ) / 2
    y_treeQ = (sh_treeQ - wh_treeQ) / 2
    treeQ.geometry("%dx%d+%d+%d" % (ww_treeQ, wh_treeQ, x_treeQ, y_treeQ))
      
        
    frame0 = ttk.Frame(treeQ, width=1310, height=20)
    frame0.pack(side=TOP)
    framecanvas = ttk.Frame(treeQ, width=1310, height=20)
    framecanvas.pack(side=BOTTOM)
    frame = ttk.Frame(treeQ, width=1310, height=600)
    frame.pack(fill="both", expand="false")

    
    
    if methon==0:
        PROGRAM_Menubar(treeQ,ori_owercount_easyread, methon, ori)
 
    ##########报表查看器的通用部件#################
    try:
        xt11 = StringVar()
        xt11.set("产品类别")
        def xt11set(*arg):
            xt11.set(comboxlist.get())
        xt22 = StringVar()
        xt22.set("无源|诊断试剂")
        import_se1 = Label(frame0, text="")
        import_se1.pack(side=LEFT)
        import_se1 = Label(frame0, text="位置：")
        import_se1.pack(side=LEFT)
        comvalue = StringVar()  # 窗体自带的文本，新建一个值
        comboxlist = ttk.Combobox(
            frame0, width=12, height=30, state="readonly", textvariable=comvalue
        )  # 初始化
        comboxlist["values"] = ori_owercount_easyread.columns.tolist()
        comboxlist.current(0)  # 选择第一个
        comboxlist.bind("<<ComboboxSelected>>", xt11set)  # 绑定事件,(下拉列表框被选中时，绑定XT11SET函数)
        comboxlist.pack(side=LEFT)
        import_se3 = Label(frame0, text="检索：")
        import_se3.pack(side=LEFT)
        xentry_t22 = Entry(frame0, width=12, textvariable=xt22).pack(side=LEFT)
        
        def  Tbutton1_all(): #标记定位作用
            pass  
        


            
               
        B_SAVE = Button(
            frame0,
            text="导出",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TOOLS_save_dict(ori_owercount_easyread),
        )  #
        B_SAVE.pack(side=LEFT)
        B_SAVE2 = Button(
            frame0,
            text="视图",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(TOOLS_easyreadT(ori_owercount_easyread), 1, ori),
        )  # easyreadT
        if "详细描述T" not in ori_owercount_easyread.columns:
            B_SAVE2.pack(side=LEFT)

        B_SAVE2 = Button(
            frame0,
            text="网",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TOOLS_web_view(ori_owercount_easyread),
        )  # easyreadT
        if "详细描述T" not in ori_owercount_easyread.columns:
            pass
            #B_SAVE2.pack(side=LEFT)
                    
        BX_var = Button(
            frame0,
            text="含",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.loc[
                    ori_owercount_easyread[xt11.get()].astype(str).str.contains(
                        str(xt22.get()), na=False
                    )
                ],
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)
        BX_var = Button(
            frame0,
            text="无",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.loc[~
                    ori_owercount_easyread[xt11.get()].astype(str).str.contains(
                        str(xt22.get()), na=False
                    )
                ],
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)
        BX_var = Button(
            frame0,
            text="大",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.loc[
                    ori_owercount_easyread[xt11.get()].astype(float)>float(xt22.get())
                ],
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)
        BX_var = Button(
            frame0,
            text="小",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.loc[
                    ori_owercount_easyread[xt11.get()].astype(float)<float(xt22.get())
                ],
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)
        BX_var = Button(
            frame0,
            text="等",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.loc[
                    ori_owercount_easyread[xt11.get()].astype(float)==float(xt22.get())
                ],
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)
        
        BX_var = Button(
            frame0,
            text="式",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda:TOOLS_findin(ori_owercount_easyread,ori))  
        BX_var.pack(side=LEFT)

        BX_var = Button(
            frame0,
            text="前",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.head(int(xt22.get()))
                ,
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)

        BX_var = Button(
            frame0,
            text="升",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.sort_values(by=(xt11.get()),ascending=[True],na_position="last") 
                ,
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)

        BX_var = Button(
            frame0,
            text="降",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.sort_values(by=(xt11.get()),ascending=[False],na_position="last") 
                ,
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)
        
        
        BX_var = Button(
            frame0,
            text="重",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread.drop_duplicates(xt11.get())
                ,
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)  
        
        BX_var = Button(
            frame0,
            text="统",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                STAT_pinzhong(ori_owercount_easyread,xt11.get(),0)
                ,
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)          
              

        BX_var = Button(
            frame0,
            text="SQL",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TOOLS_sql(ori_owercount_easyread),
        )  #
        BX_var.pack(side=LEFT)


    except:
        pass

    ##########报表查看器的个性化部件（药械妆）#################
    if ini["模式"]!="其他":
        B_tmd  = Button(
                frame0,
                text="近月",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    ori_owercount_easyread[(ori_owercount_easyread["最近30天报告单位个数"]>=1)],
                    1,
                    ori,
                ),
            )
        if "最近30天报告数" in ori_owercount_easyread.columns:
            B_tmd.pack(side=LEFT)



        BX_var = Button(
            frame0,
            text="图表",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: DRAW_pre(ori_owercount_easyread),
            )
        if methon!=0:    
            BX_var.pack(side=LEFT)
            
            
 

        def  Tbutton2_button(): #标记定位作用
            pass 


        if methon==0:
            
            B_tmd  = Button(
                frame0,
                text="精简",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    TOOLS_easyread2(ori_owercount_easyread),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT)    

            
        if methon==0:
            
            B_tmd  = Button(
                frame0,
                text="证号",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_zhenghao(),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT)    
            
            B_tmd  = Button(
                frame0,
                text="图",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: DRAW_pre(Countall(ori_owercount_easyread).df_zhenghao())  )
            B_tmd.pack(side=LEFT)                


            B_tmd  = Button(
                frame0,
                text="批号",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_pihao(),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT)
            
            B_tmd  = Button(
                frame0,
                text="图",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: DRAW_pre(Countall(ori_owercount_easyread).df_pihao())  )
            B_tmd.pack(side=LEFT)                  
            
        
            B_tmd  = Button(
                frame0,
                text="型号",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_xinghao(),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT) 
            
            B_tmd  = Button(
                frame0,
                text="图",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: DRAW_pre(Countall(ori_owercount_easyread).df_xinghao())  )
            B_tmd.pack(side=LEFT)      
                   
        
            B_tmd  = Button(
                frame0,
                text="规格",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_guige(),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT)  
            
            B_tmd  = Button(
                frame0,
                text="图",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: DRAW_pre(Countall(ori_owercount_easyread).df_guige())  )
            B_tmd.pack(side=LEFT)    
            
        
            B_tmd  = Button(
                frame0,
                text="企业",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_chiyouren(),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT)  



            B_tmd  = Button(
                frame0,
                text="县区",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_org("监测机构"),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT) 
            B_tmd  = Button(
                frame0,
                text="单位",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_user(),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT) 

            B_tmd  = Button(
                frame0,
                text="年龄",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_age(),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT)

            B_tmd  = Button(
                frame0,
                text="时隔",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    TOOLS_deep_view(ori_owercount_easyread,["时隔"],["报告编码","nunique"],0),
                    1,
                    ori,
                ),
            )
            B_tmd.pack(side=LEFT)

            B_tmd  = Button(
                frame0,
                text="表现",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    Countall(ori_owercount_easyread).df_psur(),
                    1,
                    ori,
                ),
            )
            if "UDI" not in ori_owercount_easyread.columns:
                B_tmd.pack(side=LEFT)  #TOOLS_get_guize2(ori_owercount_easyread)
            B_tmd  = Button(
                frame0,
                text="表现",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TABLE_tree_Level_2(
                    TOOLS_get_guize2(ori_owercount_easyread),
                    1,
                    ori,
                ),
            )
            if "UDI" in ori_owercount_easyread.columns:
                B_tmd.pack(side=LEFT)  #
            B_tmd  = Button(
                frame0,
                text="发生时间",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: TOOLS_time(ori_owercount_easyread,"事件发生日期",0),
            )
            B_tmd.pack(side=LEFT)           

            B_tmd  = Button(
                frame0,
                text="报告时间",
                bg="white",
                font=("微软雅黑", 10),
                relief=GROOVE,
                activebackground="green",
                command=lambda: DRAW_make_one(TOOLS_time(ori_owercount_easyread,"报告日期",1), "时间托帕斯图", "time", "报告总数","超级托帕斯图(严重伤害数)"),
            )
            B_tmd.pack(side=LEFT)





    try:                      
        #下面的框
        a_labeee = ttk.Label(framecanvas, text="方法：")
        a_labeee.pack(side=LEFT)
        number = StringVar()
        number_chosen = ttk.Combobox(framecanvas, width=15, textvariable=number, state='readonly')
        number_chosen['values'] = ("分组统计","数据透视","拆分成字典(X-Y)","描述性统计(X)","饼图(XY)","柱状图(XY)","折线图(XY)","托帕斯图(XY)","堆叠柱状图（X-YZ）","追加外部表格信息","添加到外部表格")
        #if "报告编码" in ori_owercount_easyread.columns:
        #    number_chosen['values'] =("分组统计","数据透视","追加外部表格信息","添加到外部表格") #    + number_chosen['values']

        number_chosen.pack(side=LEFT)
        number_chosen.current(0)
        a_label = ttk.Label(framecanvas, text="分组列（X-Y-Z）:")
        a_label.pack(side=LEFT)    


        j_x =StringVar()
        x_entered = ttk.Combobox(framecanvas, width=15, textvariable=j_x, state='readonly')
        x_entered['values']=ori_owercount_easyread.columns.tolist() 
        x_entered.pack(side=LEFT)  
        j_y =StringVar()
        y_entered = ttk.Combobox(framecanvas, width=15, textvariable=j_y, state='readonly')
        y_entered['values']=ori_owercount_easyread.columns.tolist() 
        y_entered.pack(side=LEFT)
        j_z =StringVar()
        z_entered = ttk.Combobox(framecanvas, width=15, textvariable=j_z, state='readonly')
        z_entered['values']=ori_owercount_easyread.columns.tolist() 
        z_entered.pack(side=LEFT)
        j_v =StringVar()
        j_m =StringVar()        
        a_label = ttk.Label(framecanvas, text="计算列（V-M）:")
        a_label.pack(side=LEFT) 
        
        v_entered = ttk.Combobox(framecanvas, width=10, textvariable=j_v, state='readonly')
        v_entered['values']=ori_owercount_easyread.columns.tolist() 
        v_entered.pack(side=LEFT)
        m_entered = ttk.Combobox(framecanvas, width=10, textvariable=j_m, state='readonly')
        m_entered['values']=["计数","求和","唯一值计数"] 
        m_entered.pack(side=LEFT)        
        
        B_fengxian1 = Button(framecanvas,text="自助报表",bg="white",font=("微软雅黑", 10),relief=GROOVE,activebackground="green",command=lambda: TOOLS_Autotable_0(ori_owercount_easyread,number_chosen.get(),j_x.get(),j_y.get(),j_z.get(),j_v.get(),j_m.get(),ori_owercount_easyread))
        B_fengxian1.pack(side=LEFT)
            
         

        BX_var = Button(
            framecanvas,
            text="去首行",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread[1:]
                ,
                1,
                ori,
            )
        )  #
        BX_var.pack(side=LEFT)  

        BX_var = Button(
            framecanvas,
            text="去尾行",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(
                ori_owercount_easyread[:-1]
                ,
                1,
                ori,
            ),
        )  #
        BX_var.pack(side=LEFT)        
            
        B_tmd = Button(
            framecanvas,
            text="行数:"+str(len(ori_owercount_easyread)),
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",

        )
        B_tmd.pack(side=LEFT)  

                 
    except:
        showinfo(title="提示信息", message="界面初始化失败。")    



    #为作为一个工具箱使用的一个兼容
    try:
        if others[0]=="tools_x":
           return 0
    except:
            pass

    ##########查看器上的表格显示模块#################
    bookList = ori_owercount_easyread.values.tolist()
    columns_list = ori_owercount_easyread.columns.values.tolist()
    tree = ttk.Treeview(frame, columns=columns_list, show="headings", height=45)

    
    for i in columns_list:
        tree.heading(i, text=i)
    for item in bookList:
        tree.insert("", "end", values=item)

    for b in columns_list:
        try:
            tree.column(b, minwidth=0, width=80, stretch=NO)
            if "只剩" in b:
                tree.column(b, minwidth=0, width=150, stretch=NO)
        except:
            pass
    #调节行间距
    setlist800 = [
        "评分说明"
    ]    
    
    #调节行间距
    setlist200 = [
        "该单位喜好上报的品种统计",
        "报告编码",
        "产品名称",
        "上报机构描述",
        "持有人处理描述",
        "该注册证编号/曾用注册证编号报告数量",
        "通用名称",
        "该批准文号报告数量",
        "上市许可持有人名称",         
    ]
    setlist140 = [
        "注册证编号/曾用注册证编号",
        "监测机构",
        "报告月份",
        "报告季度",
        "单位列表",      
        "单位名称",                   
    ]    
 
    setlist40 = [
        "管理类别",
    ]   

    
    for b in setlist200:
        try:
            tree.column(b, minwidth=0, width=200, stretch=NO)
        except:
            pass

 
    for b in setlist140:
        try:
            tree.column(b, minwidth=0, width=140, stretch=NO)
        except:
            pass
    for b in setlist40:
        try:
            tree.column(b, minwidth=0, width=40, stretch=NO)
        except:
            pass
    for b in setlist800:
        try:
            tree.column(b, minwidth=0, width=800, stretch=NO)
        except:
            pass

    try:
        tree.column(
            "请选择需要查看的表格", minwidth=1, width=300, stretch=NO
        )  # 第一层是个exel文件（多单元表）的时候使用
    except:
        pass

    try:
        tree.column(
            "详细描述T", minwidth=1, width=2300, stretch=NO
        )  # 第一层是个exel文件（多单元表）的时候使用，调整列间距
    except:
        pass

    yscrollbar = Scrollbar(frame, orient="vertical")  # horizontal
    yscrollbar.pack(side=RIGHT, fill=Y)
    yscrollbar.config(command=tree.yview)
    tree.config(yscrollcommand=yscrollbar.set)

    xscrollbar = Scrollbar(frame, orient="horizontal")  # horizontal
    xscrollbar.pack(side=BOTTOM, fill=X)
    xscrollbar.config(command=tree.xview)
    tree.config(yscrollcommand=yscrollbar.set)

    # 核心功能：根据表格判断下一层级该筛选和执行什么
    def trefun_1(event, columns_list, ori):

        for item in tree.selection():
            selection = tree.item(item, "values")
        s_dict=dict(zip(columns_list,selection))

        
        # 以下根据每个具体的表格定制：
        if "详细描述T" in columns_list and "{" in s_dict["详细描述T"]:
            dict_ori=eval(s_dict["详细描述T"]) 
            dict_ori=pd.DataFrame.from_dict(dict_ori, orient="index",columns=["content"]).reset_index()
            dict_ori=dict_ori.sort_values(by="content",ascending=[False],na_position="last") 
            DRAW_make_one(dict_ori, s_dict["条目"], "index", "content","饼图")
            return 0



        #针对deep_view
        if "dfx_deepview" in s_dict["报表类型"]:
            index_list=eval(s_dict["报表类型"][13:])
            data_s=ori.copy()
            for ifo in index_list:
                data_s =data_s[(data_s[ifo].astype(str)==selection[index_list.index(ifo)])].copy() # bao括的
            data_s["报表类型"]="ori_dfx_deepview"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0        

        #针对deep_view2  #包含关系的那种
        if "dfx_deepvie2" in s_dict["报表类型"]:
            index_list=eval(s_dict["报表类型"][13:])
            data_s=ori.copy()
            for ifo in index_list:
                data_s =data_s[data_s[ifo].str.contains(selection[index_list.index(ifo)], na=False)].copy() # bao括的
            data_s["报表类型"]="ori_dfx_deepview"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0


        #针对"注册证编号/曾用注册证编号"
        if "dfx_zhenghao" in s_dict["报表类型"]:
            data_s =ori[(ori["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
            data_s["报表类型"]="ori_dfx_zhenghao"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0


        #针对"批号 型号 规格及其预警"（只有一个证号）
        if ("dfx_pihao" in s_dict["报表类型"] or "dfx_findrisk" in s_dict["报表类型"] or  "dfx_xinghao" in s_dict["报表类型"]  or  "dfx_guige" in s_dict["报表类型"]) and zte==1:
            namex="CLT"
            if "pihao" in s_dict["报表类型"] or  "产品批号" in s_dict["报表类型"]:
                namex="产品批号"  
            if "xinghao" in s_dict["报表类型"] or  "型号" in s_dict["报表类型"]:
                namex="型号"    
            if "guige" in s_dict["报表类型"] or  "规格" in s_dict["报表类型"]:
                namex="规格"  
            if "事件发生季度" in s_dict["报表类型"]:
                namex="事件发生季度" 
            if "事件发生月份" in s_dict["报表类型"]:
                namex="事件发生月份" 
            if "性别" in s_dict["报表类型"]:
                namex="性别" 
            if "年龄段" in s_dict["报表类型"]:
                namex="年龄段" 
            data_s =ori[(ori["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])&(ori[namex]==s_dict[namex])].copy()  # bao括的
            data_s["报表类型"]="ori_pihao"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0

        #针对批号，型号，规格，关键字预警等，调出该注册证的所有的(有多个证号）

        if ("findrisk" in s_dict["报表类型"] or "dfx_pihao" in s_dict["报表类型"] or  "dfx_xinghao" in s_dict["报表类型"] or  "dfx_guige" in s_dict["报表类型"]) and  zte!=1:
            data_s =ori_owercount_easyread[(ori_owercount_easyread["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
            data_s["报表类型"]=s_dict["报表类型"]+"1"
            TABLE_tree_Level_2(data_s,1,ori)
            
            return 0    

        #针对"县区"
        if "dfx_org监测机构" in s_dict["报表类型"]:
            data_s =ori[(ori["监测机构"]==s_dict["监测机构"])].copy()  # bao括的
            data_s["报表类型"]="ori_dfx_org"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0
        #针对"地市"
        if "dfx_org市级监测机构" in s_dict["报表类型"]:
            data_s =ori[(ori["市级监测机构"]==s_dict["市级监测机构"])].copy()  # bao括的
            data_s["报表类型"]="ori_dfx_org"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0

        #针对"报告单位"
        if "dfx_user" in s_dict["报表类型"]:
            data_s =ori[(ori["单位名称"]==s_dict["单位名称"])].copy()  # bao括的
            data_s["报表类型"]="ori_dfx_user"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0
            

        #针对"生产企业"
        if "dfx_chiyouren" in s_dict["报表类型"]:
            data_s =ori[(ori["上市许可持有人名称"]==s_dict["上市许可持有人名称"])].copy()  # bao括的
            data_s["报表类型"]="ori_dfx_chiyouren"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0
        #针对"产品"
        if "dfx_chanpin" in s_dict["报表类型"]:
            data_s =ori[(ori["产品名称"]==s_dict["产品名称"])].copy()  # bao括的
            data_s["报表类型"]="ori_dfx_chanpin"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0            
            
            
            
        #针对"季度预警"
        if "dfx_findrisk事件发生季度1" in s_dict["报表类型"]:
            data_s =ori[(ori["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])&(ori["事件发生季度"]==s_dict["事件发生季度"])].copy()  # bao括的
            data_s["报表类型"]="ori_dfx_findrisk事件发生季度"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0

        #针对"月份预警"
        if "dfx_findrisk事件发生月份1" in s_dict["报表类型"]:
            data_s =ori[(ori["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])&(ori["事件发生月份"]==s_dict["事件发生月份"])].copy()  # bao括的
            data_s["报表类型"]="ori_dfx_findrisk事件发生月份"
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0

        #针对"关键字预警（批号）-1"
        if ("keyword_findrisk" in s_dict["报表类型"]) and zte==1:
            namex="CLT"
            if "批号" in s_dict["报表类型"]:
                namex="产品批号"  
            if "事件发生季度" in s_dict["报表类型"]:
                namex="事件发生季度"    
            if "事件发生月份" in s_dict["报表类型"]:
                namex="事件发生月份"    
            if "性别" in s_dict["报表类型"]:
                namex="性别" 
            if "年龄段" in s_dict["报表类型"]:
                namex="年龄段"                 
            data_s =ori[(ori["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])&(ori[namex]==s_dict[namex])].copy()  # bao括的
            data_s["关键字查找列"] = ""
            for x in TOOLS_get_list(s_dict["关键字查找列"]):
                data_s["关键字查找列"] = data_s["关键字查找列"] + data_s[x].astype("str")
            data_s =data_s[(data_s["关键字查找列"].str.contains(s_dict["关键字组合"], na=False))]  
            
            if str(s_dict["排除值"])!="nan":  # 需要排除的
                data_s = data_s.loc[~data_s["关键字查找列"].str.contains(s_dict["排除值"], na=False)]
            
            data_s["报表类型"]="ori_"+s_dict["报表类型"]
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0
                
            
                    
        #针对PSUR"
        if ("PSUR" in s_dict["报表类型"]):
            data_s=ori.copy()
            if ini["模式"]=="器械":
                data_s["关键字查找列"] = data_s["器械故障表现"].astype(str)+data_s["伤害表现"].astype(str)+data_s["使用过程"].astype(str)+data_s["事件原因分析描述"].astype(str)+data_s["初步处置情况"].astype(str)#器械故障表现|伤害表现|使用过程|事件原因分析描述|初步处置情况
            else:
                data_s["关键字查找列"] = data_s["器械故障表现"]
                
            if "-其他关键字-" in str(s_dict["关键字标记"]):
                data_s = data_s.loc[~data_s["关键字查找列"].str.contains(s_dict["关键字标记"], na=False)].copy()    
                TABLE_tree_Level_2(data_s,0,data_s)
                return 0
             
            #不是其他关键字的情况                    
            data_s =data_s[(data_s["关键字查找列"].str.contains(s_dict["关键字标记"], na=False))]  
            if str(s_dict["排除值"])!="没有排除值":  # 需要排除的
                data_s = data_s.loc[~data_s["关键字查找列"].str.contains(s_dict["排除值"], na=False)]

                       
            #data_s["报表类型"]="ori_"+selection[-1]
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0

        #一个通用的，通过字典定义
        if ("ROR" in s_dict["报表类型"]):
            globalsE = {'nan': "-未定义-"    }
            data = eval(s_dict["报表定位"], globalsE)
            data_s=ori.copy()
            
            for k,v  in data.items():            

                if k=="合并列" and v!={}:
                    for k1,v1 in v.items(): 
                        if v1!="-未定义-":
                            v2=TOOLS_get_list(v1)
                            data_s[k1]=""  
                            for vx in v2: 
                                data_s[k1] = data_s[k1]+ data_s[vx].astype("str")
                        
                if k=="等于" and v!={}:
                    for k1,v1 in v.items(): 
                        data_s=data_s[(data_s[k1]==v1)]                     
                        
                if k=="不等于" and v!={}:
                    for k1,v1 in v.items(): 
                        if v1!="-未定义-":                    
                            data_s=data_s[(data_s[k1]!=v1)]                           

                if k=="包含" and v!={}:
                    for k1,v1 in v.items(): 
                        if v1!="-未定义-":
                            data_s = data_s.loc[data_s[k1].str.contains(v1, na=False)]

                if k=="不包含" and v!={}:
                    for k1,v1 in v.items(): 
                        if v1!="-未定义-":
                            data_s = data_s.loc[~data_s[k1].str.contains(v1, na=False)]   
                                            
            TABLE_tree_Level_2(data_s,0,data_s)
            return 0
    
    #为有关键字标记的PSUR增加一个右键菜单        
    if  ("关键字标记" in  comboxlist["values"]) and  ("该类别不良事件计数" in  comboxlist["values"]):
            def callbackK1(event=None):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s=ori.copy()
                if ini["模式"]=="器械":
                    data_s["关键字查找列"] = data_s["器械故障表现"].astype(str)+data_s["伤害表现"].astype(str)+data_s["使用过程"].astype(str)+data_s["事件原因分析描述"].astype(str)+data_s["初步处置情况"].astype(str)#器械故障表现|伤害表现|使用过程|事件原因分析描述|初步处置情况
                else:
                    data_s["关键字查找列"] = data_s["器械故障表现"]
                if "-其他关键字-" in str(s_dict["关键字标记"]):
                    data_s = data_s.loc[~data_s["关键字查找列"].str.contains(s_dict["关键字标记"], na=False)].copy()   
                #不是其他关键字的情况                    
                data_s =data_s[(data_s["关键字查找列"].str.contains(s_dict["关键字标记"], na=False))]  
                if str(s_dict["排除值"])!="没有排除值":  # 需要排除的
                    data_s = data_s.loc[~data_s["关键字查找列"].str.contains(s_dict["排除值"], na=False)]
                resul=TOOLS_count_elements(data_s, s_dict["关键字标记"], "关键字查找列")
                resul=resul.sort_values(by="计数", ascending=[False], na_position="last").reset_index(drop=True)
                TABLE_tree_Level_2(resul,1,data_s)      
            menu = Menu(treeQ,tearoff=False,)
            menu.add_command(label="表现具体细项", command=callbackK1)  
            def popup(event):
                menu.post(event.x_root, event.y_root)   # post在指定的位置显示弹出菜单
            treeQ.bind("<Button-3>",popup)                 # 绑定鼠标右键,执行popup函数  # lambda event: trefun_0(event, ori_owercount_easyread))#

    
    #为课题服务的一个右键按钮
    try:
        if others[1]=="dfx_zhenghao":
            mdy="dfx_zhenghao"
            timefor=""
    except:
            mdy=""
            timefor="近一年"
       
    if  (("总体评分" in  comboxlist["values"]) and   ("高峰批号均值" in  comboxlist["values"]) and  ("月份均值" in  comboxlist["values"])) or mdy=="dfx_zhenghao":
    #ori是data30,other[0]=data365
        
            def callback1(event=None):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s =ori[(ori["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"
                TABLE_tree_Level_2(data_s,1,ori)      
            def callback2(event=None):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s =others[0][(others[0]["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"
                TABLE_tree_Level_2(data_s,1,others[0])     
            def callback3(msd):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                
                #先统计近30天的       
                data_s =ori[(ori["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"  
                m30=Countall(data_s).df_psur(msd,s_dict["规整后品类"])[["关键字标记","总数量","严重比"]]  
                m30=m30.rename(columns={"总数量":"最近30天总数量"})   
                m30=m30.rename(columns={"严重比":"最近30天严重比"}) 
                #再统计近一年的                
                data_s =others[0][(others[0]["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"                
                m365=Countall(data_s).df_psur(msd,s_dict["规整后品类"])
                
                result=pd.merge(m365,m30,on="关键字标记", how="left")#.reset_index(drop)    
                del result["报表类型"] 
                result["报表类型"]="PSUR" 
                                          
                TABLE_tree_Level_2(result,1, data_s)       
                                    
            
            def callback4(msdx):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s=others[0]
                if s_dict["规整后品类"]=="N":
                    if msdx=="特定品种":
                        showinfo(title="关于", message="未能适配该品种规则，可能未制定或者数据规整不完善。")
                        return 0
                    data_s = data_s.loc[data_s["产品名称"].str.contains(s_dict["产品名称"], na=False)].copy()   
                else:
                    data_s = data_s.loc[data_s["规整后品类"].str.contains(s_dict["规整后品类"], na=False)].copy()
                data_s= data_s.loc[data_s["产品类别"].str.contains(s_dict["产品类别"], na=False)].copy()
                     
                data_s["报表类型"]=s_dict["报表类型"]+"1"
                if msdx=="特定品种":
                    TABLE_tree_Level_2(Countall(data_s).df_ror(["产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"],s_dict["规整后品类"],s_dict["注册证编号/曾用注册证编号"]), 1,data_s)       
                else:
                    TABLE_tree_Level_2(Countall(data_s).df_ror(["产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"],msdx,s_dict["注册证编号/曾用注册证编号"]), 1,data_s) 
            
            def callback5(event=None):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s =others[0][(others[0]["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"
                TABLE_tree_Level_2(
                    Countall(data_s).df_pihao(),
                    1,
                    data_s,
                )  
                
            def callback6(event=None):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s =others[0][(others[0]["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"
                TABLE_tree_Level_2(
                    Countall(data_s).df_xinghao(),
                    1,
                    data_s,
                )   
                  
            def callback7(event=None):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s =others[0][(others[0]["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"               
                TABLE_tree_Level_2(
                    Countall(data_s).df_user(),
                    1,
                    data_s,
                )               
                    
            def callback8(event=None):

                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s =others[0][(others[0]["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"     
                kx_o = pd.read_excel(peizhidir+"0（范例）预警参数.xlsx", header=0, sheet_name=0).reset_index(drop=True)
                if ini["模式"]=="药品":
                    kx_o = pd.read_excel(peizhidir+"0（范例）预警参数.xlsx", header=0, sheet_name="药品").reset_index(drop=True)
                if ini["模式"]=="器械":
                    kx_o = pd.read_excel(peizhidir+"0（范例）预警参数.xlsx", header=0, sheet_name="器械").reset_index(drop=True)    
                if ini["模式"]=="化妆品":
                    kx_o = pd.read_excel(peizhidir+"0（范例）预警参数.xlsx", header=0, sheet_name="化妆品").reset_index(drop=True)    
                k4_o=kx_o["值"][3]+"|"+kx_o["值"][4] #高度关注关键字（一级）
                if ini["模式"]=="器械":
                    data_s["关键字查找列"] = data_s["器械故障表现"].astype(str)+data_s["伤害表现"].astype(str)+data_s["使用过程"].astype(str)+data_s["事件原因分析描述"].astype(str)+data_s["初步处置情况"].astype(str)#器械故障表现|伤害表现|使用过程|事件原因分析描述|初步处置情况
                else:
                    data_s["关键字查找列"] = data_s["器械故障表现"].astype(str)
                data_s = data_s.loc[data_s["关键字查找列"].str.contains(k4_o, na=False)].copy().reset_index(drop=True)         

                TABLE_tree_Level_2(
                    data_s,
                    0,
                    data_s,
                )  

               
            def callback9(event=None):
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s =others[0][(others[0]["注册证编号/曾用注册证编号"]==s_dict["注册证编号/曾用注册证编号"])].copy()  # bao括的
                data_s["报表类型"]=s_dict["报表类型"]+"1"    
                TOOLS_time(data_s,"事件发生日期",0)    

            def callback10(msdx,meth):
                
                for item in tree.selection():
                    selection = tree.item(item, "values")
                s_dict=dict(zip(columns_list,selection))
                data_s=others[0]
                if s_dict["规整后品类"]=="N":
                    if msdx=="特定品种":
                        showinfo(title="关于", message="未能适配该品种规则，可能未制定或者数据规整不完善。")
                        return 0
                data_s = data_s.loc[data_s["注册证编号/曾用注册证编号"].str.contains(s_dict["注册证编号/曾用注册证编号"], na=False)].copy()   
                data_s["报表类型"]=s_dict["报表类型"]+"1"
                if msdx=="特定品种":
                    TABLE_tree_Level_2(Countall(data_s).df_find_all_keword_risk(meth,s_dict["规整后品类"]), 1,data_s)       
                else:
                    TABLE_tree_Level_2(Countall(data_s).df_find_all_keword_risk(meth,msdx), 1,data_s)       

            
                  
            menu = Menu(treeQ,tearoff=False,)
            menu.add_command(label=timefor+"故障表现分类（无源）", command=lambda: callback3("通用无源"))  
            menu.add_command(label=timefor+"故障表现分类（有源）", command=lambda: callback3("通用有源")) 
            menu.add_command(label=timefor+"故障表现分类（特定品种）", command=lambda: callback3("特定品种"))  

            menu.add_separator()   
            if mdy=="":                               
                menu.add_command(label=timefor+"同类比较(ROR-无源)", command=lambda: callback4("无源")) 
                menu.add_command(label=timefor+"同类比较(ROR-有源)", command=lambda: callback4("有源"))    
                menu.add_command(label=timefor+"同类比较(ROR-特定品种)", command=lambda: callback4("特定品种"))  
            
            menu.add_separator()                                    
            menu.add_command(label=timefor+"关键字趋势(批号-无源)", command=lambda: callback10("无源","产品批号"))          
            menu.add_command(label=timefor+"关键字趋势(批号-特定品种)", command=lambda: callback10("特定品种","产品批号"))  
            menu.add_command(label=timefor+"关键字趋势(月份-无源)", command=lambda: callback10("无源","事件发生月份")) 
            menu.add_command(label=timefor+"关键字趋势(月份-有源)", command=lambda: callback10("有源","事件发生月份"))             
            menu.add_command(label=timefor+"关键字趋势(月份-特定品种)", command=lambda: callback10("特定品种","事件发生月份"))  
            menu.add_command(label=timefor+"关键字趋势(季度-无源)", command=lambda: callback10("无源","事件发生季度")) 
            menu.add_command(label=timefor+"关键字趋势(季度-有源)", command=lambda: callback10("有源","事件发生季度"))             
            menu.add_command(label=timefor+"关键字趋势(季度-特定品种)", command=lambda: callback10("特定品种","事件发生季度"))  
                                      
            menu.add_separator() 
            menu.add_command(label=timefor+"各批号报送情况", command=callback5) 
            menu.add_command(label=timefor+"各型号报送情况", command=callback6) 
            menu.add_command(label=timefor+"报告单位情况", command=callback7)
            menu.add_command(label=timefor+"事件发生时间曲线", command=callback9)
            menu.add_separator()             
            menu.add_command(label=timefor+"原始数据", command=callback2)
            if mdy=="":  
                menu.add_command(label="近30天原始数据", command=callback1)
            menu.add_command(label=timefor+"高度关注(一级和二级)", command=callback8)  

            def popup(event):
                menu.post(event.x_root, event.y_root)   # post在指定的位置显示弹出菜单
            treeQ.bind("<Button-3>",popup)                 # 绑定鼠标右键,执行popup函数  # lambda event: trefun_0(event, ori_owercount_easyread))#


    if methon == 0 or "规整编码" in ori_owercount_easyread.columns:  # 根据编码，查看源文件
        tree.bind("<Double-1>", lambda event: trefun_0(event, ori_owercount_easyread))
    if methon == 1 and "规整编码"  not in ori_owercount_easyread.columns:  # 器械适用，查看非源文件
        tree.bind("<Double-1>", lambda event: trefun_1(event, columns_list, ori))
    # 以下是排序功能：

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
        
        
    ##########查看器上的查看源文件模块#################
    def trefun_0(event, data):  # 根据编码，查看源文件
        
        if "规整编码" in data.columns:
            data=data.rename(columns={"规整编码":"报告编码"})
        
        for item in tree.selection():
            selection = tree.item(item, "values")  # 返回的是该行所有值的列表，不包括目录名

            # 10086
            viewtable = Toplevel()

            sw = viewtable.winfo_screenwidth()
            # 得到屏幕宽度
            sh = viewtable.winfo_screenheight()
            # 得到屏幕高度
            ww = 800
            wh = 600
            # 窗口宽高为100
            x = (sw - ww) / 2
            y = (sh - wh) / 2
            viewtable.geometry("%dx%d+%d+%d" % (ww, wh, x, y))

            text_viewtable = ScrolledText(
                viewtable, height=1100, width=1100, bg="#FFFFFF"
            )
            text_viewtable.pack(padx=10, pady=10)
            def callback1(event=None):
                text_viewtable.event_generate('<<Copy>>')   
            def callback3(data,filename):
                TOOLS_savetxt(data,filename,1)
            menu = Menu(text_viewtable,tearoff=False,)
            menu.add_command(label="复制", command=callback1)
            menu.add_command(label="导出", command=lambda:PROGRAM_thread_it(callback3,text_viewtable.get(1.0,'end'),filedialog.asksaveasfilename(title=u"保存文件",initialfile=data.iloc[0,0],defaultextension="txt",filetypes=[("txt", "*.txt")])))

            def popup(event):
                menu.post(event.x_root, event.y_root)   # post在指定的位置显示弹出菜单
            text_viewtable.bind("<Button-3>", popup)                 # 绑定鼠标右键,执行popup函数
            
            try:
                viewtable.title(str(selection[0]))
                data["报告编码"] = data["报告编码"].astype("str")
                print_value = data[(data["报告编码"] == str(selection[0]))]
            except:
                pass
            #prinf(ori)  
            columns_list = data.columns.values.tolist()
            for i in range(len(columns_list)):  # 根据部分字段来分行

                try:
                    if columns_list[i] == "报告编码.1":
                        text_viewtable.insert(END, "\n\n")
                    if columns_list[i] == "产品名称":
                        text_viewtable.insert(END, "\n\n")
                    if columns_list[i] == "事件发生日期":
                        text_viewtable.insert(END, "\n\n")
                    if columns_list[i] == "是否开展了调查":
                        text_viewtable.insert(END, "\n\n")
                    if columns_list[i] == "市级监测机构":
                        text_viewtable.insert(END, "\n\n")
                    if columns_list[i] == "上报机构描述":
                        text_viewtable.insert(END, "\n\n")
                    if columns_list[i] == "持有人处理描述":
                        text_viewtable.insert(END, "\n\n")  
                    if i>1 and columns_list[i-1] == "持有人处理描述":
                        text_viewtable.insert(END, "\n\n") 
                                                                      
                except:
                    pass
                try:
                    if columns_list[i] in ["单位名称","产品名称ori","上报机构描述","持有人处理描述","产品名称","注册证编号/曾用注册证编号","型号","规格","产品批号","上市许可持有人名称ori","上市许可持有人名称","伤害","伤害表现","器械故障表现","使用过程","事件原因分析描述","初步处置情况","调查情况","关联性评价","事件原因分析.1","具体控制措施"]:
                        text_viewtable.insert(END, "●")
                except:
                    pass
                text_viewtable.insert(END, columns_list[i])
                text_viewtable.insert(END, "：")
                try:
                    text_viewtable.insert(END, print_value.iloc[0, i])
                except:
                    text_viewtable.insert(END,selection[i])
                text_viewtable.insert(END, "\n")
            text_viewtable.config(state=DISABLED)

    tree.pack()


def TOOLS_get_guize2(ori_owercount_easyread):
    """切换通用规则使用"""
    filename=peizhidir+"0（范例）比例失衡关键字库.xls"
    guize3= pd.read_excel(filename, header=0, sheet_name="器械")      
    auto_guize3=guize3[["适用范围列","适用范围"]].drop_duplicates("适用范围")
    text.insert(END,auto_guize3)
    text.see(END)
    se = Toplevel()
    se.title('切换通用规则')
    sw_se = se.winfo_screenwidth()
    #得到屏幕宽度
    sh_se = se.winfo_screenheight()
    #得到屏幕高度
    ww_se = 450
    wh_se = 100
    #窗口宽高为100  #
    x_se = (sw_se-ww_se) / 2
    y_se = (sh_se-wh_se) / 2
    se.geometry("%dx%d+%d+%d" %(ww_se,wh_se,x_se,y_se)) 
    import_se55=Label(se,text="查找位置：器械故障表现+伤害表现+使用过程+事件原因分析描述+初步处置情况")
    import_se55.pack()    
    import_se2=Label(se,text="请选择您所需要的通用规则关键字：")
    import_se2.pack()
    def xt11set(*arg):
        comvalue.set(comboxlist.get())
    comvalue = StringVar()
    comboxlist = ttk.Combobox(se, width=14, height=30, state="readonly", textvariable=comvalue )  # 初始化
    comboxlist["values"] = auto_guize3["适用范围"].to_list()
    comboxlist.current(0)  # 选择第一个
    comboxlist.bind("<<ComboboxSelected>>", xt11set)  # 绑定事件,(下拉列表框被选中时，绑定XT11SET函数)
    comboxlist.pack()


    labFrame_Button_se=LabelFrame(se)
    btn_se=Button(labFrame_Button_se,text="确定",width=10,command=lambda:get_guize2(guize3,comvalue.get()))
    btn_se.pack(side=LEFT,padx=1,pady=1)
    labFrame_Button_se.pack()    
    
    def get_guize2(guize3,covn):
        msdd=guize3.loc[guize3["适用范围"].str.contains(covn, na=False)].copy().reset_index(drop=True)
        TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_psur("特定品种作为通用关键字",msdd),1,ori_owercount_easyread)
def TOOLS_findin(data,ori):
    """根据公式查找"""
    se = Toplevel()
    se.title('高级查找')
    sw_se = se.winfo_screenwidth()
    #得到屏幕宽度
    sh_se = se.winfo_screenheight()
    #得到屏幕高度
    ww_se = 400
    wh_se = 120
    #窗口宽高为100
    x_se = (sw_se-ww_se) / 2
    y_se = (sh_se-wh_se) / 2
    se.geometry("%dx%d+%d+%d" %(ww_se,wh_se,x_se,y_se)) 
    import_se=Label(se,text="需要查找的关键字（用|隔开）：")
    import_se.pack()
    import_se2=Label(se,text="在哪些列查找（用|隔开）：")
    
    import_se_entry=Entry(se, width = 80)
    import_se_entry.insert(0,"破裂|断裂")
    import_se2_entry=Entry(se, width = 80)
    import_se2_entry.insert(0,"器械故障表现|伤害表现")    
    import_se_entry.pack()
    import_se2.pack()
    import_se2_entry.pack()
    labFrame_Button_se=LabelFrame(se)
    btn_se=Button(labFrame_Button_se,text="确定",width=10,command=lambda:PROGRAM_thread_it(TABLE_tree_Level_2,plok(import_se_entry.get(),import_se2_entry.get(),data),1,ori))
    btn_se.pack(side=LEFT,padx=1,pady=1)
    labFrame_Button_se.pack()    
       
    
    def plok(lst2,lst1,data):
        data["关键字查找列10"]="######"
        for i in TOOLS_get_list(lst1):
            data["关键字查找列10"]=data["关键字查找列10"].astype(str)+data[i].astype(str)    
        data = data.loc[data["关键字查找列10"].str.contains(lst2, na=False)]  
        del data["关键字查找列10"]
        return data

def PROGRAM_about():
    """-关于"""
    about = " 佛山市食品药品检验检测中心 \n(佛山市药品不良反应监测中心)\n蔡权周（QQ或微信411703730）\n仅供政府设立的不良反应监测机构使用。"
    showinfo(title="关于", message=about)


def PROGRAM_thread_it(func, *args):
    """将函数打包进线程"""
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()
def PROGRAM_Menubar(win,ori_owercount_easyread, methon, ori):
    """创建菜单栏"""

    MenuBar = Menu(win)
    # 将菜单栏放到主窗口
    win.config(menu=MenuBar)

    TOOLS_Bar = Menu(MenuBar, tearoff=0)
    MenuBar.add_cascade(label="实用工具", menu=TOOLS_Bar)
    TOOLS_Bar.add_command(        
        label="统计工具箱", command=lambda: TABLE_tree_Level_2(ori_owercount_easyread, 1,ori,"tools_x"))  
 
    
    TOOLS_Bar.add_separator()     
    TOOLS_Bar.add_command(        
        label="原始导入", command=TOOLS_fileopen)
    TOOLS_Bar.add_separator() 
    if ini["模式"]=="器械":    
        TOOLS_Bar.add_command(        
        label="预警（单日）", command=lambda: TOOLS_keti(ori_owercount_easyread))    
        TOOLS_Bar.add_separator()     
        TOOLS_Bar.add_command(        
        label="规整查看", command=lambda: TABLE_tree_Level_2(easyread_sz(ori_owercount_easyread), 1, ori_owercount_easyread))    

    if ini["模式"]=="药品":    
        TOOLS_Bar.add_command(label="新的不良反应检测(证号)", command=lambda: PROGRAM_thread_it(TOOLS_get_new, ori,"证号")) 
        TOOLS_Bar.add_command(label="新的不良反应检测(品种)", command=lambda: PROGRAM_thread_it(TOOLS_get_new, ori,"品种"))   
    TOOLS_Bar.add_separator()     
    TOOLS_Bar.add_command(        
        label="数据规整（报告单位-配置表）", command=lambda: TOOL_guizheng(ori_owercount_easyread,2,False))    
    TOOLS_Bar.add_command(        
        label="数据规整（批准文号加产品名称-众数法）", command=lambda: TOOL_guizheng(ori_owercount_easyread,3,False))
    TOOLS_Bar.add_command(        
        label="数据规整（品类规整-配置表）", command=lambda: TOOL_guizheng(ori_owercount_easyread,'课题',False))    
    TOOLS_Bar.add_command(        
        label="数据规整（自定义）", command=lambda: TOOL_guizheng(ori_owercount_easyread,0,False))    
    TOOLS_Bar.add_command(        
        label="批量筛选（自定义）", command=lambda: TOOLS_xuanze(ori_owercount_easyread,0))                
    TOOLS_Bar.add_command(        
        label="脱敏保存（配置表）", command=lambda: TOOLS_data_masking(ori_owercount_easyread))
    #控制功能
    if ini["模式"]=="其他":
        return 0    

    if (ini["模式"]=="药品" or  ini["模式"]=="器械") and 1==2 :
        treadBar = Menu(MenuBar, tearoff=0)
        MenuBar.add_cascade(label="信号检测", menu=treadBar)
        treadBar.add_separator() 
        treadBar.add_command(        
            label="数量比例失衡监测-证号内批号", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_findrisk("产品批号"), 1,ori)         )    
        treadBar.add_command(        
            label="数量比例失衡监测-证号内季度", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_findrisk("事件发生季度"), 1,ori)         )
        treadBar.add_command(            
            label="数量比例失衡监测-证号内月份", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_findrisk("事件发生月份"), 1,ori)         )         
        treadBar.add_command(        
            label="数量比例失衡监测-证号内性别", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_findrisk("性别"), 1,ori)         )
        treadBar.add_command(            
            label="数量比例失衡监测-证号内年龄段", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_findrisk("年龄段"), 1,ori)         )         

        treadBar.add_separator() 
        treadBar.add_command(
            label="关键字检测（同证号内不同批号比对）", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_find_all_keword_risk("产品批号"), 1,ori)         )    
        treadBar.add_command(
            label="关键字检测（同证号内不同月份比对）", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_find_all_keword_risk("事件发生月份"), 1,ori)         )    
        treadBar.add_command(
            label="关键字检测（同证号内不同季度比对）", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_find_all_keword_risk("事件发生季度"), 1,ori)         )    
        treadBar.add_command(
            label="关键字检测（同证号内不同性别比对）", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_find_all_keword_risk("性别"), 1,ori)         )    
        treadBar.add_command(
            label="关键字检测（同证号内不同年龄段比对）", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_find_all_keword_risk("年龄段"), 1,ori)         )    

        treadBar.add_separator() 
        treadBar.add_command(
            label="关键字ROR-页面内同证号的批号间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号","产品批号"]), 1,ori)         )    
        treadBar.add_command(
            label="关键字ROR-页面内同证号的月份间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号","事件发生月份"]), 1,ori)         )    
        treadBar.add_command(
            label="关键字ROR-页面内同证号的季度间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号","事件发生季度"]), 1,ori)         )     
        treadBar.add_command(
            label="关键字ROR-页面内同证号的年龄段间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号","年龄段"]), 1,ori)         )     
        treadBar.add_command(
            label="关键字ROR-页面内同证号的性别间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号","性别"]), 1,ori)         )     

        treadBar.add_separator() 
        treadBar.add_command(
            label="关键字ROR-页面内同品名的证号间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"]), 1,ori)         )        
        treadBar.add_command(
            label="关键字ROR-页面内同品名的年龄段间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["产品类别","规整后品类","产品名称","年龄段"]), 1,ori)         )        
        treadBar.add_command(
            label="关键字ROR-页面内同品名的性别间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["产品类别","规整后品类","产品名称","性别"]), 1,ori)         )        

        treadBar.add_separator() 
        treadBar.add_command(
            label="关键字ROR-页面内同类别的名称间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["产品类别","产品名称"]), 1,ori)         )    
        treadBar.add_command(
            label="关键字ROR-页面内同类别的年龄段间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["产品类别","年龄段"]), 1,ori)         )    
        treadBar.add_command(
            label="关键字ROR-页面内同类别的性别间比对", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_ror(["产品类别","性别"]), 1,ori)         )    

        

    report_Bar = Menu(MenuBar, tearoff=0)
    MenuBar.add_cascade(label="简报制作", menu=report_Bar)
         
    report_Bar.add_command(        
        label="药品简报", command=lambda: TOOLS_autocount(ori_owercount_easyread,"药品"))    
    report_Bar.add_command(        
        label="器械简报", command=lambda: TOOLS_autocount(ori_owercount_easyread,"器械"))    
    report_Bar.add_command(        
        label="化妆品简报", command=lambda: TOOLS_autocount(ori_owercount_easyread,"化妆品"))    



    pinzhong_Bar = Menu(MenuBar, tearoff=0)
    MenuBar.add_cascade(label="品种评价", menu=pinzhong_Bar)
    pinzhong_Bar.add_command(        
        label="报告年份", command=lambda: STAT_pinzhong(ori_owercount_easyread,"报告年份",-1))    
    pinzhong_Bar.add_command(        
        label="发生年份", command=lambda: STAT_pinzhong(ori_owercount_easyread,"事件发生年份",-1))    
    pinzhong_Bar.add_separator()         

    pinzhong_Bar.add_command(        
        label="涉及企业", command=lambda: STAT_pinzhong(ori_owercount_easyread,"上市许可持有人名称",1))            
    pinzhong_Bar.add_command(        
        label="产品名称", command=lambda: STAT_pinzhong(ori_owercount_easyread,"产品名称",1))        
    pinzhong_Bar.add_command(        
        label="注册证号", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_zhenghao(),1, ori))        
    pinzhong_Bar.add_separator()         
    pinzhong_Bar.add_command(        
        label="年龄段分布", command=lambda: STAT_pinzhong(ori_owercount_easyread,"年龄段",1))    
    pinzhong_Bar.add_command(        
        label="性别分布", command=lambda: STAT_pinzhong(ori_owercount_easyread,"性别",1))    
    pinzhong_Bar.add_command(        
        label="年龄性别分布", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_age(),1, ori, )    )    
    pinzhong_Bar.add_separator()                         
    pinzhong_Bar.add_command(        
        label="事件发生时间", command=lambda: STAT_pinzhong(ori_owercount_easyread,"时隔",1))    
    if ini["模式"]=="器械":                    
        pinzhong_Bar.add_command(        
            label="事件分布（故障表现）", command=lambda: STAT_pinzhong(ori_owercount_easyread,"器械故障表现",0))    
        pinzhong_Bar.add_command(        
            label="事件分布（关键词）", command=lambda: TOOLS_get_guize2(ori_owercount_easyread))        
    if ini["模式"]=="药品":        
        pinzhong_Bar.add_command(        
            label="怀疑/并用", command=lambda: STAT_pinzhong(ori_owercount_easyread,"怀疑/并用",1))
        pinzhong_Bar.add_command(        
            label="报告类型-严重程度", command=lambda: STAT_pinzhong(ori_owercount_easyread,"报告类型-严重程度",1))
        pinzhong_Bar.add_command(        
            label="停药减药后反应是否减轻或消失", command=lambda: STAT_pinzhong(ori_owercount_easyread,"停药减药后反应是否减轻或消失",1))
        pinzhong_Bar.add_command(        
            label="再次使用可疑药是否出现同样反应", command=lambda: STAT_pinzhong(ori_owercount_easyread,"再次使用可疑药是否出现同样反应",1))                
        pinzhong_Bar.add_command(        
            label="对原患疾病影响", command=lambda: STAT_pinzhong(ori_owercount_easyread,"对原患疾病影响",1))
        pinzhong_Bar.add_command(        
            label="不良反应结果", command=lambda: STAT_pinzhong(ori_owercount_easyread,"不良反应结果",1))
        pinzhong_Bar.add_command(        
            label="报告单位关联性评价", command=lambda: STAT_pinzhong(ori_owercount_easyread,"关联性评价",1))
        pinzhong_Bar.add_separator()         
        pinzhong_Bar.add_command(        
            label="不良反应转归情况", command=lambda: STAT_pinzhong(ori_owercount_easyread,"不良反应结果2",4))                                    
        pinzhong_Bar.add_command(        
            label="品种评价-关联性评价汇总", command=lambda: STAT_pinzhong(ori_owercount_easyread,"关联性评价汇总",5))    
            
                
            
        pinzhong_Bar.add_separator()                 
        pinzhong_Bar.add_command(        
            label="不良反应-术语", command=lambda: STAT_pinzhong(ori_owercount_easyread,"器械故障表现",0))    
        pinzhong_Bar.add_command(        
            label="不良反应器官系统-术语", command=lambda: TABLE_tree_Level_2(Countall(ori_owercount_easyread).df_psur(), 1, ori))    
        if "不良反应-code" in ori_owercount_easyread.columns:    
            pinzhong_Bar.add_command(        
                label="不良反应-由code转化", command=lambda: STAT_pinzhong(ori_owercount_easyread,"不良反应-code",2))    
            pinzhong_Bar.add_command(        
                label="不良反应器官系统-由code转化", command=lambda: STAT_pinzhong(ori_owercount_easyread,"不良反应-code",3))            
            pinzhong_Bar.add_separator()             
        pinzhong_Bar.add_command(        
            label="疾病名称-术语", command=lambda: STAT_pinzhong(ori_owercount_easyread,"相关疾病信息[疾病名称]-术语",0))    
        if "不良反应-code" in ori_owercount_easyread.columns:    
            pinzhong_Bar.add_command(        
                label="疾病名称-由code转化", command=lambda: STAT_pinzhong(ori_owercount_easyread,"相关疾病信息[疾病名称]-code",2))    
            pinzhong_Bar.add_command(        
                label="疾病器官系统-由code转化", command=lambda: STAT_pinzhong(ori_owercount_easyread,"相关疾病信息[疾病名称]-code",3))            
            pinzhong_Bar.add_separator()        
        pinzhong_Bar.add_command(        
            label="适应症-术语", command=lambda: STAT_pinzhong(ori_owercount_easyread,"治疗适应症-术语",0))    
        if "不良反应-code" in ori_owercount_easyread.columns:    
            pinzhong_Bar.add_command(        
                label="适应症-由code转化", command=lambda: STAT_pinzhong(ori_owercount_easyread,"治疗适应症-code",2))    
            pinzhong_Bar.add_command(        
                label="适应症器官系统-由code转化", command=lambda: STAT_pinzhong(ori_owercount_easyread,"治疗适应症-code",3))

    if ini["模式"]=="药品" and 1==2:
        keti_Bar = Menu(MenuBar, tearoff=0)
        MenuBar.add_cascade(label="药品探索", menu=keti_Bar)    
  
        keti_Bar.add_separator()
        keti_Bar.add_command(        
            label="基础信息批量操作（品名）", command=lambda: TOOLS_ror_mode1(ori_owercount_easyread,"产品名称"))
        keti_Bar.add_command(        
            label="器官系统分类批量操作（品名）", command=lambda: TOOLS_ror_mode4(ori_owercount_easyread,"产品名称"))
        keti_Bar.add_command(        
            label="器官系统ROR批量操作（品名）", command=lambda: TOOLS_ror_mode2(ori_owercount_easyread,"产品名称"))
        keti_Bar.add_command(        
            label="ADR-ROR批量操作（品名）", command=lambda: TOOLS_ror_mode3(ori_owercount_easyread,"产品名称"))
        keti_Bar.add_separator()     
        keti_Bar.add_command(        
            label="基础信息批量操作（批准文号）", command=lambda: TOOLS_ror_mode1(ori_owercount_easyread,"注册证编号/曾用注册证编号"))
        keti_Bar.add_command(        
            label="器官系统分类批量操作（批准文号）", command=lambda: TOOLS_ror_mode4(ori_owercount_easyread,"注册证编号/曾用注册证编号"))
        keti_Bar.add_command(        
            label="器官系统ROR批量操作（批准文号）", command=lambda: TOOLS_ror_mode2(ori_owercount_easyread,"注册证编号/曾用注册证编号"))
        keti_Bar.add_command(        
            label="ADR-ROR批量操作（批准文号）", command=lambda: TOOLS_ror_mode3(ori_owercount_easyread,"注册证编号/曾用注册证编号"))        
        






    #药物滥用专用
    #lanyong_Bar = Menu(MenuBar, tearoff=0)
    #MenuBar.add_cascade(label="药物滥用", menu=lanyong_Bar)

    #真实世界
    #std_Bar = Menu(MenuBar, tearoff=0)
    #MenuBar.add_cascade(label="真实世界", menu=std_Bar)


    TOOL_Bar = Menu(MenuBar, tearoff=0)
    MenuBar.add_cascade(label="其他", menu=TOOL_Bar)
         
         
    
    TOOL_Bar.add_command(        
        label="评价人员", command=lambda: TOOL_person(ori_owercount_easyread))        
    TOOL_Bar.add_command(    
        label="问题和建议", command=lambda: PROGRAM_helper(["","  药械妆不良反应报表统计分析工作站","  开发者：蔡权周","  邮箱：411703730@qq.com","  微信号：sysucai","  手机号：18575757461"]))    
    #TOOL_Bar.add_command(    
    #    label="更改用户组", command=lambda: PROGRAM_thread_it(display_random_number))    

        
        
def PROGRAM_helper(mytext):
    """-信息查看，传入一个可迭代对象"""
    helper = Toplevel()
    helper.title("信息查看")
    helper.geometry("700x500")

    yscrollbar = Scrollbar(helper)
    text_helper = Text(helper, height=80, width=150, bg="#FFFFFF", font="微软雅黑")
    yscrollbar.pack(side=RIGHT, fill=Y)
    text_helper.pack()
    yscrollbar.config(command=text_helper.yview)
    text_helper.config(yscrollcommand=yscrollbar.set)
    # text_helper.insert(END,"\n\n")
    for i in mytext:
        text_helper.insert(END,i)
        text_helper.insert(END,"\n")
        
        
    def callback1(event=None):
        text_helper.event_generate('<<Copy>>')   


    menu = Menu(text_helper,tearoff=False,)
    menu.add_command(label="复制", command=callback1)
    def popup(event):
         menu.post(event.x_root, event.y_root)   # post在指定的位置显示弹出菜单
    text_helper.bind("<Button-3>", popup)  
    
    text_helper.config(state=DISABLED)

def PROGRAM_change_schedule(now_schedule, all_schedule):
    """更新进度条"""
    # canvas.coords(fill_rec, (5, 5, 6 + (now_schedule/all_schedule)*100, 25))
    canvas.coords(fill_rec, (5, 5, (now_schedule / all_schedule) * 680, 25))
    root.update()
    x.set(str(round(now_schedule / all_schedule * 100, 2)) + "%")
    if round(now_schedule / all_schedule * 100, 2) == 100.00:
        x.set("完成")

    
############################################################
#类部分
############################################################
#第一部分：数据清洗
        



def calculate_average_score(df,cdr):
    # 确保DataFrame包含“报告分数”和“报告数量”两列
    if '报告分数' not in df.columns or '报告数量' not in df.columns:
        raise ValueError("DataFrame必须包含'报告分数'和'报告数量'两列")
    
    # 找到不是合计行的行
    non_total_rows = df[df[cdr] != '合计']
    
    # 确保报告数量和报告分数列的数据类型正确
    non_total_rows['报告数量'] = pd.to_numeric(non_total_rows['报告数量'], errors='coerce')
    non_total_rows['报告分数'] = pd.to_numeric(non_total_rows['报告分数'], errors='coerce')
    
    # 过滤掉任何包含NaN的行（这些行在计算总分和数量时应该被忽略）
    valid_rows = non_total_rows.dropna(subset=['报告数量', '报告分数'])
    
    # 计算加权总分和总报告数量
    weighted_total = (valid_rows['报告分数'] * valid_rows['报告数量']).sum()
    total_quantity = valid_rows['报告数量'].sum()
    
    # 防止除以零的情况
    if total_quantity == 0:
        average_score = np.nan  # 或者你可以选择一个默认值，比如0
    else:
        average_score = weighted_total / total_quantity
    
    # 找到合计行的索引
    total_index = df[df[cdr] == '合计'].index[0]
    
    # 更新合计行的“报告分数”列，并保留两位小数
    df.at[total_index, '报告分数'] = round(average_score, 2)
    
    return df
 

    
class Countall():
    """通用的统计模块"""    
    def __init__(self,data):
        """通用的统计模块"""            
        self.df=data
        self.mode=ini["模式"]



    def df_org(self,target):
        """县区统计模块""" 
        dfx_org=self.df.drop_duplicates(["报告编码"]).groupby([target]).agg(
            报告数量=("注册证编号/曾用注册证编号","count"),
            审核通过数=("有效报告","sum"),
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),                
            超时报告数=("超时标记",lambda x: STAT_countpx(x.values,1)),    
            有源=("产品类别",lambda x: STAT_countpx(x.values,"有源")),
            无源=("产品类别",lambda x: STAT_countpx(x.values,"无源")),
            体外诊断试剂=("产品类别",lambda x: STAT_countpx(x.values,"体外诊断试剂")),        
            三类数量=("管理类别",lambda x: STAT_countpx(x.values,"Ⅲ类")),                        
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),    
            报告季度=("报告季度",STAT_countx),    
            报告月份=("报告月份",STAT_countx),    
            报告分数=("报告分数",'mean')                            
            ).sort_values(by="报告数量", ascending=[False], na_position="last").reset_index()
        #计算总数
        a=["报告数量","审核通过数","严重伤害数","死亡数量","超时报告数","有源","无源","体外诊断试剂","三类数量","单位个数"]
        dfx_org.loc["合计"] = dfx_org[a].apply(lambda x: x.sum())
        dfx_org[a] = dfx_org[a].apply(lambda x: x.astype(int) )        
        dfx_org.iloc[-1, 0] = "合计"
        dfx_org["报告分数"]=round(dfx_org["报告分数"],2)
        dfx_org["严重比"]=round((dfx_org["严重伤害数"]+dfx_org["死亡数量"])/dfx_org["报告数量"]*100,2)

        dfx_org["Ⅲ类比"]=round((dfx_org["三类数量"])/dfx_org["报告数量"]*100,2)    
        dfx_org["超时比"]=round((dfx_org["超时报告数"])/dfx_org["报告数量"]*100,2)    
        if ini["模式"]=="器械":
            dfx_org["超时比"]=round(dfx_org["超时报告数"]/(dfx_org["严重伤害数"]+dfx_org["死亡数量"])*100,2)                                    
        dfx_org["报表类型"]="dfx_org"+target
        
        dfx_org= calculate_average_score(dfx_org,target)
        if ini["模式"]=="药品":
            #del dfx_org["审核通过数"]
            del dfx_org["有源"]
            del dfx_org["无源"]    
            del dfx_org["体外诊断试剂"]    
            dfx_org=dfx_org.rename(columns={"三类数量": "新的和严重的数量"})                                            
            dfx_org=dfx_org.rename(columns={"Ⅲ类比": "新严比"})
            
        return dfx_org



    def df_user(self):
        """监测机构统计模块""" 
        self.df["医疗机构类别"]=    self.df["医疗机构类别"].fillna("未填写")        
        dfx_user=self.df.drop_duplicates(["报告编码"]).groupby(["监测机构","单位名称","医疗机构类别"]).agg(
            报告数量=("注册证编号/曾用注册证编号","count"),
            审核通过数=("有效报告","sum"),
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),                    
            超时报告数=("超时标记",lambda x: STAT_countpx(x.values,1)),                        
            有源=("产品类别",lambda x: STAT_countpx(x.values,"有源")),
            无源=("产品类别",lambda x: STAT_countpx(x.values,"无源")),
            体外诊断试剂=("产品类别",lambda x: STAT_countpx(x.values,"体外诊断试剂")),    
            三类数量=("管理类别",lambda x: STAT_countpx(x.values,"Ⅲ类")),    
            产品数量=("产品名称","nunique"),
            产品清单=("产品名称",STAT_countx),                        
            报告季度=("报告季度",STAT_countx),    
            报告月份=("报告月份",STAT_countx),    
            报告分数=("报告分数",'mean')            
            ).sort_values(by="报告数量", ascending=[False], na_position="last").reset_index()
            
        #计算总数
        a=["报告数量","审核通过数","严重伤害数","死亡数量","超时报告数","有源","无源","体外诊断试剂","三类数量"]
        dfx_user.loc["合计"] = dfx_user[a].apply(lambda x: x.sum())
        dfx_user[a] = dfx_user[a].apply(lambda x: x.astype(int) )        
        dfx_user.iloc[-1, 0] = "合计"
        dfx_user["报告分数"]=round(dfx_user["报告分数"],2)    
        dfx_user["严重比"]=round((dfx_user["严重伤害数"]+dfx_user["死亡数量"])/dfx_user["报告数量"]*100,2)
        dfx_user["Ⅲ类比"]=round((dfx_user["三类数量"])/dfx_user["报告数量"]*100,2)    
        dfx_user["超时比"]=round((dfx_user["超时报告数"])/dfx_user["报告数量"]*100,2)    
        if ini["模式"]=="器械":
            dfx_user["超时比"]=round(dfx_user["超时报告数"]/(dfx_user["严重伤害数"]+dfx_user["死亡数量"])*100,2)                        
        dfx_user["报表类型"]="dfx_user"
        
        if ini["模式"]=="药品":
            #del dfx_user["审核通过数"]
            del dfx_user["有源"]
            del dfx_user["无源"]    
            del dfx_user["体外诊断试剂"]    
            dfx_user=dfx_user.rename(columns={"三类数量": "新的和严重的数量"})                                            
            dfx_user=dfx_user.rename(columns={"Ⅲ类比": "新严比"})
        dfx_user= calculate_average_score(dfx_user,"监测机构")
        return dfx_user
        


        
    def df_zhenghao(self):
        """注册证号统计模块，含评分，评分针对注册证号"""     
        #这些是不能去重处理的        
        dfx_zhenghao1=self.df.groupby(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"]).agg(
            证号计数=("报告编码","nunique"),
            批号个数=("产品批号","nunique"),
            批号列表=("产品批号",STAT_countx),    
            型号个数=("型号","nunique"),
            型号列表=("型号",STAT_countx),        
            规格个数=("规格","nunique"),    
            规格列表=("规格",STAT_countx),                        
            ).sort_values(by="证号计数", ascending=[False], na_position="last").reset_index()    
        #这些是需要去重处理的
        dfx_zhenghao2=self.df.drop_duplicates(["报告编码"]).groupby(["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"]).agg(
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),                    
            待评价数=("持有人报告状态",lambda x: STAT_countpx(x.values,"待评价")),
            严重伤害待评价数=("伤害与评价",lambda x: STAT_countpx(x.values,"严重伤害待评价")),
            ).reset_index()    
            
        dfx_zhenghao=pd.merge(dfx_zhenghao1,  dfx_zhenghao2,on=["上市许可持有人名称","产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"], how="left")    
        dfx_zhenghao=STAT_basic_risk(dfx_zhenghao,"证号计数","严重伤害数","死亡数量","单位个数")
        
        dfx_zhenghao=pd.merge(dfx_zhenghao,  STAT_recent30(self.df,["注册证编号/曾用注册证编号"]),on=["注册证编号/曾用注册证编号"], how="left")
        dfx_zhenghao["最近30天报告数"]=dfx_zhenghao["最近30天报告数"].fillna(0).astype(int)        
        dfx_zhenghao["最近30天报告严重伤害数"]=dfx_zhenghao["最近30天报告严重伤害数"].fillna(0).astype(int)    
        dfx_zhenghao["最近30天报告死亡数量"]=dfx_zhenghao["最近30天报告死亡数量"].fillna(0).astype(int)    
        dfx_zhenghao["最近30天报告单位个数"]=dfx_zhenghao["最近30天报告单位个数"].fillna(0).astype(int)        
        dfx_zhenghao["最近30天风险评分"]=dfx_zhenghao["最近30天风险评分"].fillna(0).astype(int)            
        
        dfx_zhenghao["报表类型"]="dfx_zhenghao"
        
        if ini["模式"]=="药品":
            dfx_zhenghao=dfx_zhenghao.rename(columns={"待评价数": "新的数量"})                                            
            dfx_zhenghao=dfx_zhenghao.rename(columns={"严重伤害待评价数": "新的严重的数量"})
        
        return dfx_zhenghao

    def df_pihao(self):    
        """批号统计模块""" 
        dfx_pihao1=self.df.groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","产品批号"]).agg(
            批号计数=("报告编码","nunique"),    
            型号个数=("型号","nunique"),
            型号列表=("型号",STAT_countx),        
            规格个数=("规格","nunique"),    
            规格列表=("规格",STAT_countx),        
            ).sort_values(by="批号计数", ascending=[False], na_position="last").reset_index()
                
        dfx_pihao2=self.df.drop_duplicates(["报告编码"]).groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","产品批号"]).agg(
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),                    
            待评价数=("持有人报告状态",lambda x: STAT_countpx(x.values,"待评价")),
            严重伤害待评价数=("伤害与评价",lambda x: STAT_countpx(x.values,"严重伤害待评价")),
            ).reset_index()    

        dfx_pihao=pd.merge(dfx_pihao1,  dfx_pihao2,on=["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","产品批号"], how="left")    

        dfx_pihao=STAT_basic_risk(dfx_pihao,"批号计数","严重伤害数","死亡数量","单位个数")    
        
        dfx_pihao=pd.merge(dfx_pihao,  STAT_recent30(self.df,["注册证编号/曾用注册证编号","产品批号"]),on=["注册证编号/曾用注册证编号","产品批号"], how="left")
        dfx_pihao["最近30天报告数"]=dfx_pihao["最近30天报告数"].fillna(0).astype(int)        
        dfx_pihao["最近30天报告严重伤害数"]=dfx_pihao["最近30天报告严重伤害数"].fillna(0).astype(int)    
        dfx_pihao["最近30天报告死亡数量"]=dfx_pihao["最近30天报告死亡数量"].fillna(0).astype(int)    
        dfx_pihao["最近30天报告单位个数"]=dfx_pihao["最近30天报告单位个数"].fillna(0).astype(int)        
        dfx_pihao["最近30天风险评分"]=dfx_pihao["最近30天风险评分"].fillna(0).astype(int)

        dfx_pihao["报表类型"]="dfx_pihao"
        if ini["模式"]=="药品":
            dfx_pihao=dfx_pihao.rename(columns={"待评价数": "新的数量"})                                            
            dfx_pihao=dfx_pihao.rename(columns={"严重伤害待评价数": "新的严重的数量"})        
        return dfx_pihao

    def df_xinghao(self):
        """型号统计模块""" 
        dfx_xinghao1=self.df.groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","型号"]).agg(
            型号计数=("报告编码","nunique"),    
            批号个数=("产品批号","nunique"),
            批号列表=("产品批号",STAT_countx),        
            规格个数=("规格","nunique"),    
            规格列表=("规格",STAT_countx),        
            ).sort_values(by="型号计数", ascending=[False], na_position="last").reset_index()
            
        dfx_xinghao2=self.df.drop_duplicates(["报告编码"]).groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","型号"]).agg(
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),                    
            待评价数=("持有人报告状态",lambda x: STAT_countpx(x.values,"待评价")),
            严重伤害待评价数=("伤害与评价",lambda x: STAT_countpx(x.values,"严重伤害待评价")),
            ).reset_index()            
            
        dfx_xinghao=pd.merge(dfx_xinghao1,  dfx_xinghao2,on=["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","型号"], how="left")    
            
            
        dfx_xinghao["报表类型"]="dfx_xinghao"
        if ini["模式"]=="药品":
            dfx_xinghao=dfx_xinghao.rename(columns={"待评价数": "新的数量"})                                            
            dfx_xinghao=dfx_xinghao.rename(columns={"严重伤害待评价数": "新的严重的数量"})            
        
        return dfx_xinghao

    def df_guige(self):    
        """规格统计模块""" 
        dfx_guige1=self.df.groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","规格"]).agg(
            规格计数=("报告编码","nunique"),    
            批号个数=("产品批号","nunique"),
            批号列表=("产品批号",STAT_countx),        
            型号个数=("型号","nunique"),    
            型号列表=("型号",STAT_countx),        
            ).sort_values(by="规格计数", ascending=[False], na_position="last").reset_index()
            
        dfx_guige2=self.df.drop_duplicates(["报告编码"]).groupby(["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","规格"]).agg(
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),                    
            待评价数=("持有人报告状态",lambda x: STAT_countpx(x.values,"待评价")),
            严重伤害待评价数=("伤害与评价",lambda x: STAT_countpx(x.values,"严重伤害待评价")),
            ).reset_index()            
            
        dfx_guige=pd.merge(dfx_guige1,  dfx_guige2,on=["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","规格"], how="left")    
            
        dfx_guige["报表类型"]="dfx_guige"
        if ini["模式"]=="药品":
            dfx_guige=dfx_guige.rename(columns={"待评价数": "新的数量"})                                            
            dfx_guige=dfx_guige.rename(columns={"严重伤害待评价数": "新的严重的数量"})            
        
        return dfx_guige

    def df_findrisk(self,target):    
        """预警模块,针对批号、月份、季度""" 
        if target=="产品批号":
            return STAT_find_risk(self.df[(self.df["产品类别"]!="有源")],["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号"],"注册证编号/曾用注册证编号",target)
        else:
            return STAT_find_risk(self.df,["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号"],"注册证编号/曾用注册证编号",target)
            
    def df_find_all_keword_risk(self,methon,*gn):
        """关键字评分及预警模块主模块"""     
        #以后这几项作为参数传入
        df=self.df.copy()
        df=df.drop_duplicates(["报告编码"]).reset_index(drop=True)
        time1=time.time()
        filename=peizhidir+"0（范例）比例失衡关键字库.xls"
        if "报告类型-新的" in df.columns:
            guize_num="药品"
        else:
            guize_num="器械"    
        guize = pd.read_excel(filename, header=0, sheet_name=guize_num).reset_index(drop=True)
        
        #为四个品种做一些兼容
        try:
            if len(gn[0])>0:
                guize = guize.loc[guize["适用范围"].str.contains(gn[0], na=False)].copy().reset_index(drop=True)
        except:
            pass
            
        cols_list=["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号"]
        maincol=cols_list[-1]
        work_table=df.groupby(cols_list).agg(
                总数量=(maincol,"count"),
                严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
                死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),
        )
        maincol=cols_list[-1]
        
        col_listttt=cols_list.copy()
        col_listttt.append(methon)
        work_table2=df.groupby(col_listttt).agg(
                该元素总数量=(maincol,"count"),
        ).reset_index()
                
        #work_table=work_table[(work_table["总数量"]>=5)|((work_table["总数量"]>=3)&(work_table["严重伤害数"]>=1))&(work_table["死亡数量"]>=1)].reset_index()    
        work_table=work_table[(work_table["总数量"]>=3)].reset_index()    
        result_list=[]
        
        #writer = pd.ExcelWriter("Twhat.xls",engine="xlsxwriter") #########
        
        counterxx=0
        counterxx_all=int(len(work_table))
        for name_product,name_lb,name_maincol,num in zip(work_table["产品名称"].values,work_table["产品类别"].values,work_table[maincol].values,work_table["总数量"].values):
            counterxx+=1
            #print(counterxx)
            if (time.time()-time1)>3:
                root.attributes("-topmost", True)
                PROGRAM_change_schedule(counterxx,counterxx_all)
                root.attributes("-topmost", False)
            df1=df[(df[maincol]==name_maincol)].copy()    
            guize["SELECT"]=guize.apply(lambda row:(row["适用范围"] in name_product) or (row["适用范围"] in name_lb) or (row["适用范围"]=="通用") ,axis=1)
            guize1=guize[(guize["SELECT"]==True)].reset_index()
            if len(guize1)>0:
                
                for key_value,key_site,key_out in zip(guize1["值"].values,guize1["查找位置"].values,guize1["排除值"].values):
                    df2=df1.copy()
                    keyword=TOOLS_get_list(key_value)[0]
                    
                    df2["关键字查找列"] = ""
                    for x in TOOLS_get_list(key_site):
                        df2["关键字查找列"] = df2["关键字查找列"] + df2[x].astype("str")
                
                    df2.loc[df2["关键字查找列"].str.contains(key_value, na=False),"关键字"]=keyword
                    
                    #排除值
                    if str(key_out)!="nan":  # 需要排除的
                        df2 = df2.loc[~df2["关键字查找列"].str.contains(key_out, na=False)].copy()
                    
                    if(len(df2))<1:
                        continue 

                    result_temp=STAT_find_keyword_risk(df2,["上市许可持有人名称","产品类别","产品名称","注册证编号/曾用注册证编号","关键字"],"关键字",methon,int(num)) ######key
                    if len(result_temp)>0:
                        result_temp["关键字组合"]=key_value
                        result_temp["排除值"]=key_out
                        result_temp["关键字查找列"]=key_site                        
                        result_list.append(result_temp) 
                        #result_temp.to_excel(writer, sheet_name=keyword)##############
                        
        #writer.close()                
        result=pd.concat(result_list)
        
        #增加比例的预警
        result=pd.merge(result,work_table2,on=col_listttt, how="left")#.reset_index(drop)    
        result["关键字数量比例"]=round(result["计数"]/result["该元素总数量"],2)
        
        result=result.reset_index(drop=True)
        if len(result)>0:
            result["风险评分"]=0
            result["报表类型"]="keyword_findrisk"+methon
            result.loc[(result["计数"]>=3), "风险评分"] = result["风险评分"]+3    
            result.loc[(result["计数"]>=(result["数量均值"]+result["数量标准差"])), "风险评分"] = result["风险评分"]+1            
            result.loc[(result["计数"]>=result["数量CI"]), "风险评分"] = result["风险评分"]+1    
            result.loc[(result["关键字数量比例"]>0.5)&(result["计数"]>=3), "风险评分"] = result["风险评分"]+1            
            result.loc[(result["严重伤害数"]>=3), "风险评分"] = result["风险评分"]+1
            result.loc[(result["单位个数"]>=3), "风险评分"] = result["风险评分"]+1                
            result.loc[(result["死亡数量"]>=1), "风险评分"] = result["风险评分"]+10        
            result["风险评分"] = result["风险评分"]+result["单位个数"]/100    
            result =result.sort_values(by="风险评分", ascending=[False], na_position="last").reset_index(drop=True)    


            #writer = pd.ExcelWriter("Tall.xls",engine="xlsxwriter")  # 
            #result.to_excel(writer, sheet_name="字典数据")
            #writer.close()    
        print("耗时：",(time.time()-time1))
        return result


    def df_ror(self,cols_list,*gn):
        """关键字评分及预警模块主模块(ROR方法)"""     
        #以后这几项作为参数传入
        df=self.df.copy()
        time1=time.time()
        filename=peizhidir+"0（范例）比例失衡关键字库.xls"
        if "报告类型-新的" in df.columns:
            guize_num="药品"

        else:
            guize_num="器械"    
        guize = pd.read_excel(filename, header=0, sheet_name=guize_num).reset_index(drop=True)


        if "css" in df.columns: #为药品ror课题传入的
            data=df.copy()
            data["器械故障表现"]=data["器械故障表现"].fillna("未填写")
            data["器械故障表现"]=data["器械故障表现"].str.replace("*","",regex=False)
            msdd="use("+str("器械故障表现")+").file"    
            rm=str(Counter(TOOLS_get_list_r0(msdd,data,1000))).replace("Counter({", "{")
            rm=rm.replace("})", "}")
            rm = ast.literal_eval(rm)
            guize=pd.DataFrame.from_dict(rm, orient="index",columns=["计数"]).reset_index()
            guize["适用范围列"]="产品类别"
            guize["适用范围"]="无源"            
            guize["查找位置"]="伤害表现"    
            guize["值"]=guize["index"]
            guize["排除值"]="-没有排除值-"
            del guize["index"]
            
                
        maincol=cols_list[-2]
        target_col=cols_list[-1]
        cols_list2=cols_list[:-1]

        #四个品种课题右键弹出框的兼容性
        try:
            if len(gn[0])>0:
                maincol=cols_list[-3]
                guize = guize.loc[guize["适用范围"].str.contains(gn[0], na=False)].copy().reset_index(drop=True)
                work_table_mer=df.groupby(["产品类别","规整后品类","产品名称","注册证编号/曾用注册证编号"]).agg(
                        该元素总数量=(target_col,"count"),
                        该元素严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
                        该元素死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),
                        该元素单位个数=("单位名称","nunique"),    
                        该元素单位列表=("单位名称",STAT_countx),    
                ).reset_index()

                work_table=df.groupby(["产品类别","规整后品类"]).agg(
                        所有元素总数量=(maincol,"count"),
                        所有元素严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
                        所有元素死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    )
                if len(work_table)>1:
                    text.insert(END,"注意，产品类别有两种，产品名称规整疑似不正确！")
                #TABLE_tree_Level_2(work_table,1,df)
                work_table_mer = pd.merge(work_table_mer,  work_table,on=["产品类别","规整后品类"], how="left").reset_index()        
                            
        except:    
            text.insert(END,"\n目前结果为未进行名称规整的结果！\n")
            work_table_mer=df.groupby(cols_list).agg(
                    该元素总数量=(target_col,"count"),
                    该元素严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
                    该元素死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),
                    该元素单位个数=("单位名称","nunique"),    
                    该元素单位列表=("单位名称",STAT_countx),    
            ).reset_index()

            work_table=df.groupby(cols_list2).agg(
                    所有元素总数量=(maincol,"count"),
                    所有元素严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
                    所有元素死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),
            )
            
        #work_table=work_table[(work_table["总数量"]>=5)|((work_table["总数量"]>=3)&(work_table["严重伤害数"]>=1))&(work_table["死亡数量"]>=1)].reset_index()    
        
            work_table_mer = pd.merge(work_table_mer,  work_table,on=cols_list2, how="left").reset_index()    
        
        work_table=work_table[(work_table["所有元素总数量"]>=3)].reset_index()    
        result_list=[]
        
        if ("产品名称" not in work_table.columns) and  ("规整后品类" not in work_table.columns) :#对页面同类型不同名称方法做一个兼容
            work_table["产品名称"]=work_table["产品类别"]

        #writer = pd.ExcelWriter("Twhat.xls",engine="xlsxwriter") #########
        
        
        #为同类别不同名之间比较做一个兼容
        if "规整后品类" not in work_table.columns:
            work_table["规整后品类"]="不适用"

    
        counterxx=0
        counterxx_all=int(len(work_table))
        for name_product,name_lb,name_maincol,num in zip(work_table["规整后品类"],work_table["产品类别"],work_table[maincol],work_table["所有元素总数量"]):
            counterxx+=1
            if (time.time()-time1)>3:
                root.attributes("-topmost", True)
                PROGRAM_change_schedule(counterxx,counterxx_all)
                root.attributes("-topmost", False)
            df1=df[(df[maincol]==name_maincol)].copy()    
            guize["SELECT"]=guize.apply(lambda row:((name_product in row["适用范围"]) or (row["适用范围"] in name_lb)),axis=1)
            guize1=guize[(guize["SELECT"]==True)].reset_index()
            if len(guize1)>0:
                
                for key_value,key_site,key_out in zip(guize1["值"].values,guize1["查找位置"].values,guize1["排除值"].values):
                    df2=df1.copy()
                    keyword=TOOLS_get_list(key_value)[0]
                    where_to_find="关键字查找列"
                    df2[where_to_find] = ""
                    for x in TOOLS_get_list(key_site):
                        df2[where_to_find] = df2[where_to_find] + df2[x].astype("str")
                    
                    df2.loc[df2[where_to_find].str.contains(key_value, na=False),"关键字"]=keyword

                    #排除值
                    if str(key_out)!="nan":  # 需要排除的
                        df2 = df2.loc[~df2["关键字查找列"].str.contains(key_out, na=False)].copy()
                    
                    #print(df2)
                    if(len(df2))<1:
                        continue 
                    #列内的元素循环，逐一作为目标产品
                    for target in zip(df2[target_col].drop_duplicates()):

                        #为四个品种课题提提速,只计算目标证号
                        try:
                            if target[0]!=gn[1]:
                                continue
                        except:
                            pass
                                    
                        find_ori={
                        "合并列":{where_to_find:key_site},
                        "等于":{maincol:name_maincol,target_col:target[0]},
                        "不等于":{},
                        "包含":{where_to_find:key_value},
                        "不包含":{where_to_find:key_out}
                        }
                        
                        infomations=STAT_PPR_ROR_1(target_col, str(target[0]), "关键字查找列", key_value, df2)+(key_value,key_out,key_site,name_maincol,target[0],str(find_ori))

                        if infomations[1]>0:

                            result_temp = pd.DataFrame(columns= ["特定关键字","出现频次","占比","ROR值","ROR值的95%CI下限","PRR值","PRR值的95%CI下限","卡方值","四分表","关键字组合","排除值","关键字查找列",maincol,target_col,"报表定位"])
                            result_temp.loc[0]= infomations
                            result_list.append(result_temp) 
                            #result_temp.to_excel(writer, sheet_name=keyword)##############

        #writer.close()            
        result=pd.concat(result_list)


        
        result = pd.merge( work_table_mer,result, on=[maincol,target_col], how="right")
        result=result.reset_index(drop=True)
        del result["index"]
        if len(result)>0:
            result["风险评分"]=0
            result["报表类型"]="ROR"
            result.loc[(result["出现频次"]>=3), "风险评分"] = result["风险评分"]+3    
            result.loc[(result["ROR值的95%CI下限"]>1), "风险评分"] = result["风险评分"]+1            
            result.loc[(result["PRR值的95%CI下限"]>1), "风险评分"] = result["风险评分"]+1            
            result["风险评分"] = result["风险评分"]+result["该元素单位个数"]/100    
            result =result.sort_values(by="风险评分", ascending=[False], na_position="last").reset_index(drop=True)    


            #writer = pd.ExcelWriter("Tall.xls",engine="xlsxwriter")  # 
            #result.to_excel(writer, sheet_name="字典数据")
            #writer.close()    
        print("耗时：",(time.time()-time1))
        return result





    def df_chiyouren(self):
        """构建持有人情况一览表"""
        data_ori=self.df.copy().reset_index(drop=True)
        data_ori["总报告数"] =data["报告编码"].copy()
        data_ori.loc[(data_ori["持有人报告状态"] == "待评价"), "总待评价数量"] = data["报告编码"]
        data_ori.loc[(data_ori["伤害"] == "严重伤害"), "严重伤害报告数"] = data["报告编码"]
        data_ori.loc[(data_ori["持有人报告状态"] == "待评价") & (data_ori["伤害"] == "严重伤害"), "严重伤害待评价数量"] = data["报告编码"]
        data_ori.loc[(data_ori["持有人报告状态"] == "待评价") & (data_ori["伤害"] == "其他"), "其他待评价数量"] = data["报告编码"]
        groupby = data_ori.groupby(["上市许可持有人名称"]).aggregate(
            {"总报告数": "nunique", "总待评价数量": "nunique", "严重伤害报告数": "nunique", "严重伤害待评价数量": "nunique", "其他待评价数量": "nunique"}
        )
            
        
        groupby["严重伤害待评价比例"] = round(
            groupby["严重伤害待评价数量"] / groupby["严重伤害报告数"] * 100, 2
        )  # 转为百分比并保留2位小数
        groupby["总待评价比例"] = round(
            groupby["总待评价数量"] / groupby["总报告数"]* 100, 2
        )  # 转为百分比并保留2位小数
        groupby["总报告数"] = groupby["总报告数"].fillna(0)
        groupby["总待评价比例"] = groupby["总待评价比例"].fillna(0)
        groupby["严重伤害报告数"] = groupby["严重伤害报告数"].fillna(0)
        groupby["严重伤害待评价比例"] = groupby["严重伤害待评价比例"].fillna(0)
        groupby["总报告数"] = groupby["总报告数"].astype(int)
        groupby["总待评价比例"] = groupby["总待评价比例"].astype(int)
        groupby["严重伤害报告数"] = groupby["严重伤害报告数"].astype(int)
        groupby["严重伤害待评价比例"] = groupby["严重伤害待评价比例"].astype(int)
        groupby = groupby.sort_values(
            by=["总报告数", "总待评价比例"], ascending=[False, False], na_position="last"
        )
       
        if "场所名称" in data_ori.columns:
            data_ori.loc[(data_ori["审核日期"] == "未填写"), "审核日期"] = 3000-12-12  
            data_ori["报告时限"] = pd.Timestamp.today()- pd.to_datetime(data_ori["审核日期"])
            data_ori["报告时限2"] = 45-(pd.Timestamp.today()- pd.to_datetime(data_ori["审核日期"])).dt.days
            data_ori["报告时限"] = data_ori["报告时限"].dt.days
            data_ori.loc[(data_ori["报告时限"]>45)&(data_ori["伤害"]=="严重伤害")&(data_ori["持有人报告状态"] == "待评价"), "待评价且超出当前日期45天（严重）"] = 1
            data_ori.loc[(data_ori["报告时限"]>45)&(data_ori["伤害"]=="其他")&(data_ori["持有人报告状态"] == "待评价"), "待评价且超出当前日期45天（其他）"] = 1
            data_ori.loc[(data_ori["报告时限"]>30)&(data_ori["伤害"]=="死亡")&(data_ori["持有人报告状态"] == "待评价"), "待评价且超出当前日期30天（死亡）"] = 1  
            
            data_ori.loc[(data_ori["报告时限2"]<=1)&(data_ori["伤害"]=="严重伤害")&(data_ori["报告时限2"]>0)&(data_ori["持有人报告状态"] == "待评价"), "严重待评价且只剩1天"] = 1        
            data_ori.loc[(data_ori["报告时限2"]>1)&(data_ori["报告时限2"]<=3)&(data_ori["伤害"]=="严重伤害")&(data_ori["持有人报告状态"] == "待评价"), "严重待评价且只剩1-3天"] = 1   
            data_ori.loc[(data_ori["报告时限2"]>3)&(data_ori["报告时限2"]<=5)&(data_ori["伤害"]=="严重伤害")&(data_ori["持有人报告状态"] == "待评价"), "严重待评价且只剩3-5天"] = 1         
            data_ori.loc[(data_ori["报告时限2"]>5)&(data_ori["报告时限2"]<=10)&(data_ori["伤害"]=="严重伤害")&(data_ori["持有人报告状态"] == "待评价"), "严重待评价且只剩5-10天"] = 1 
            data_ori.loc[(data_ori["报告时限2"]>10)&(data_ori["报告时限2"]<=20)&(data_ori["伤害"]=="严重伤害")&(data_ori["持有人报告状态"] == "待评价"), "严重待评价且只剩10-20天"] = 1         
            data_ori.loc[(data_ori["报告时限2"]>20)&(data_ori["报告时限2"]<=30)&(data_ori["伤害"]=="严重伤害")&(data_ori["持有人报告状态"] == "待评价"), "严重待评价且只剩20-30天"] = 1                         
            data_ori.loc[(data_ori["报告时限2"]>30)&(data_ori["报告时限2"]<=45)&(data_ori["伤害"]=="严重伤害")&(data_ori["持有人报告状态"] == "待评价"), "严重待评价且只剩30-45天"] = 1
            del data_ori["报告时限2"]  
       
            search_result_all_chaoqi2 = (data_ori.groupby(["上市许可持有人名称"]).aggregate({"待评价且超出当前日期45天（严重）": "sum","待评价且超出当前日期45天（其他）": "sum","待评价且超出当前日期30天（死亡）": "sum","严重待评价且只剩1天": "sum","严重待评价且只剩1-3天": "sum","严重待评价且只剩3-5天": "sum","严重待评价且只剩5-10天": "sum","严重待评价且只剩10-20天": "sum","严重待评价且只剩20-30天": "sum","严重待评价且只剩30-45天": "sum"}).reset_index() ) 
            groupby = pd.merge(groupby,search_result_all_chaoqi2, on=["上市许可持有人名称"],how="outer",)  
            groupby["待评价且超出当前日期45天（严重）"]=groupby["待评价且超出当前日期45天（严重）"].fillna(0)  
            groupby["待评价且超出当前日期45天（严重）"]=groupby["待评价且超出当前日期45天（严重）"].astype(int)           
            groupby["待评价且超出当前日期45天（其他）"]=groupby["待评价且超出当前日期45天（其他）"].fillna(0)  
            groupby["待评价且超出当前日期45天（其他）"]=groupby["待评价且超出当前日期45天（其他）"].astype(int) 
            groupby["待评价且超出当前日期30天（死亡）"]=groupby["待评价且超出当前日期30天（死亡）"].fillna(0)  
            groupby["待评价且超出当前日期30天（死亡）"]=groupby["待评价且超出当前日期30天（死亡）"].astype(int) 
            
            groupby["严重待评价且只剩1天"]=groupby["严重待评价且只剩1天"].fillna(0)  
            groupby["严重待评价且只剩1天"]=groupby["严重待评价且只剩1天"].astype(int) 
            groupby["严重待评价且只剩1-3天"]=groupby["严重待评价且只剩1-3天"].fillna(0)  
            groupby["严重待评价且只剩1-3天"]=groupby["严重待评价且只剩1-3天"].astype(int) 
            groupby["严重待评价且只剩3-5天"]=groupby["严重待评价且只剩3-5天"].fillna(0)  
            groupby["严重待评价且只剩3-5天"]=groupby["严重待评价且只剩3-5天"].astype(int) 
            groupby["严重待评价且只剩5-10天"]=groupby["严重待评价且只剩5-10天"].fillna(0)  
            groupby["严重待评价且只剩5-10天"]=groupby["严重待评价且只剩5-10天"].astype(int) 
            groupby["严重待评价且只剩10-20天"]=groupby["严重待评价且只剩10-20天"].fillna(0)  
            groupby["严重待评价且只剩10-20天"]=groupby["严重待评价且只剩10-20天"].astype(int) 
            groupby["严重待评价且只剩20-30天"]=groupby["严重待评价且只剩20-30天"].fillna(0)  
            groupby["严重待评价且只剩20-30天"]=groupby["严重待评价且只剩20-30天"].astype(int) 
            groupby["严重待评价且只剩30-45天"]=groupby["严重待评价且只剩30-45天"].fillna(0)  
            groupby["严重待评价且只剩30-45天"]=groupby["严重待评价且只剩30-45天"].astype(int) 
                            
        groupby["总待评价数量"]=groupby["总待评价数量"].fillna(0)  
        groupby["总待评价数量"]=groupby["总待评价数量"].astype(int)  
        groupby["严重伤害待评价数量"]=groupby["严重伤害待评价数量"].fillna(0)  
        groupby["严重伤害待评价数量"]=groupby["严重伤害待评价数量"].astype(int)      
        groupby["其他待评价数量"]=groupby["其他待评价数量"].fillna(0)  
        groupby["其他待评价数量"]=groupby["其他待评价数量"].astype(int)  
        
        #计算总数
        a=["总报告数","总待评价数量","严重伤害报告数","严重伤害待评价数量","其他待评价数量"]
        groupby.loc["合计"] = groupby[a].apply(lambda x: x.sum())
        groupby[a] = groupby[a].apply(lambda x: x.astype(int) )        
        groupby.iloc[-1, 0] = "合计"
        
        if "场所名称" in data_ori.columns:             
            groupby = groupby.reset_index(drop=True)
        else:
            groupby = groupby.reset_index()
            
        if ini["模式"]=="药品":#  
            groupby=groupby.rename(columns={"总待评价数量": "新的数量"})                
            groupby=groupby.rename(columns={"严重伤害待评价数量": "新的严重的数量"})        
            groupby=groupby.rename(columns={"严重伤害待评价比例": "新的严重的比例"})                    
            groupby=groupby.rename(columns={"总待评价比例": "新的比例"})                    
                    
            del    groupby["其他待评价数量"]                    
        groupby["报表类型"]="dfx_chiyouren"
        return groupby

    def df_age(self):
        """统计年龄性别"""
        data=self.df.copy()
        data=data.drop_duplicates("报告编码").copy()
        data_temp_x2 = pd.pivot_table( data.drop_duplicates("报告编码"), values=["报告编码"],index="年龄段",columns="性别",aggfunc={"报告编码": "nunique"},fill_value="0",margins=True,dropna=False,            ).rename(columns={"报告编码": "数量"}).reset_index()
        data_temp_x2.columns = data_temp_x2.columns.droplevel(0)
        data_temp_x2["构成比(%)"]=round(100*data_temp_x2["All"]/len(data),2)
        data_temp_x2["累计构成比(%)"]=data_temp_x2["构成比(%)"].cumsum()#/data_tps.sum()*100
        data_temp_x2["报表类型"]="年龄性别表"
        return data_temp_x2

    def df_psur(self, *methon):
        """药品PSUR要求的一个表格"""
        data_temp=self.df.copy()
        filename=peizhidir+"0（范例）比例失衡关键字库.xls"
        allnumber=len(data_temp.drop_duplicates("报告编码"))
    
        
        #载入规则
        if "报告类型-新的" in data_temp.columns:
            guize_num="药品"
        elif  "皮损形态" in data_temp.columns:
            guize_num="化妆品"
        else:
            guize_num="器械"    
        guize = pd.read_excel(
            filename, header=0, sheet_name=guize_num
        )  
        guize2 = (
            guize.loc[guize["适用范围"].str.contains("通用监测关键字|无源|有源", na=False)].copy().reset_index(drop=True)
        )
        
        #四个品种课题右键弹出框
        try:
            if methon[0] in ["特定品种","通用无源","通用有源"]:
                guizex=""
                if methon[0]=="特定品种":
                    guizex = guize.loc[guize["适用范围"].str.contains(methon[1], na=False)].copy().reset_index(drop=True)
                    
                if methon[0]=="通用无源":
                    guizex = guize.loc[guize["适用范围"].str.contains("通用监测关键字|无源", na=False)].copy().reset_index(drop=True)                
                if methon[0]=="通用有源":
                    guizex = guize.loc[guize["适用范围"].str.contains("通用监测关键字|有源", na=False)].copy().reset_index(drop=True)    
                if methon[0]=="体外诊断试剂":
                    guizex = guize.loc[guize["适用范围"].str.contains("体外诊断试剂", na=False)].copy().reset_index(drop=True)                                                        
                if len(guizex)<1:
                    showinfo(title="提示", message="未找到相应的自定义规则，任务结束。")
                    return 0
                else:
                    guize2=guizex

        except:
            pass    
        
        
        #特定品种作为通用关键字
        try:
            if guize_num=="器械" and methon[0]=="特定品种作为通用关键字":
                guize2=methon[1]

        except:
            pass
                
        #追加其他关键字
        result_all = ""
        allkeyword = "-其他关键字-不含："
        for ids, cols in guize2.iterrows():
            allkeyword = allkeyword + "|" + str(cols["值"])
            mute=cols    
        mute[2]="通用监测关键字"    
        mute[4]=allkeyword
        guize2.loc[len(guize2)]= mute
        guize2 = guize2.reset_index(drop=True)
        #return guize2
        #定义关键字查找列的改造
        #data_temp["关键字查找列"] = data_temp["器械故障表现"]
        if ini["模式"]=="器械":
            data_temp["关键字查找列"] = data_temp["器械故障表现"].astype(str)+data_temp["伤害表现"].astype(str)+data_temp["使用过程"].astype(str)+data_temp["事件原因分析描述"].astype(str)+data_temp["初步处置情况"].astype(str)#器械故障表现|伤害表现|使用过程|事件原因分析描述|初步处置情况
        else:
            data_temp["关键字查找列"] = data_temp["器械故障表现"]
        text.insert(END,"\n药品查找列默认为不良反应表现,药品规则默认为通用规则。\n器械默认查找列为器械故障表现+伤害表现+使用过程+事件原因分析描述+初步处置情况，器械默认规则为无源通用规则+有源通用规则。\n")
        # 进入到单一的关键字环节
        result_all_list=[]
        
        for ids,cols in guize2.iterrows(): 
            keyword_value = cols["值"]    
     
            if "-其他关键字-" not in keyword_value:
                data_temp_x = data_temp.loc[
                    data_temp["关键字查找列"].str.contains(keyword_value, na=False)
                ].copy()
                if  str(cols["排除值"])!="nan":  # 需要排除的if not cols["排除值"]:  
                    #print(str(cols["排除值"]))
                    data_temp_x = data_temp_x.loc[~data_temp_x["关键字查找列"].str.contains(str(cols["排除值"]), na=False)].copy()
                    #print(data_temp_x)
            else:
                data_temp_x = data_temp.loc[
                    ~data_temp["关键字查找列"].str.contains(keyword_value, na=False)
                ].copy()                
            data_temp_x["关键字标记"] = str(keyword_value)
            data_temp_x["关键字计数"] = 1    




                                
            if len(data_temp_x) > 0:
                try:
                    data_temp_x2 = pd.pivot_table(
                        data_temp_x.drop_duplicates("报告编码"),
                        values=["关键字计数"],
                        index="关键字标记",
                        columns="伤害PSUR",
                        aggfunc={"关键字计数": "count"},
                        fill_value="0",
                        margins=True,
                        dropna=False,
                    ) 

                except:
                    data_temp_x2 = pd.pivot_table(
                        data_temp_x.drop_duplicates("报告编码"),
                        values=["关键字计数"],
                        index="关键字标记",
                        columns="伤害",
                        aggfunc={"关键字计数": "count"},
                        fill_value="0",
                        margins=True,
                        dropna=False,
                    )  
                data_temp_x2 = data_temp_x2[:-1]
                data_temp_x2.columns = data_temp_x2.columns.droplevel(0)
                data_temp_x2=data_temp_x2.reset_index()

                #统计不良事件表现1和2
                if len(data_temp_x2)> 0:
                    rm=str(Counter(TOOLS_get_list_r0("use(器械故障表现).file",data_temp_x,1000))).replace("Counter({", "{")
                    rm=rm.replace("})", "}")
                    rm = ast.literal_eval(rm)
                    
                    data_temp_x2.loc[0,"事件分类"]=str(TOOLS_get_list(data_temp_x2.loc[0,"关键字标记"])[0])
                    rmvb1={k:v for k, v in rm.items() if STAT_judge_x(str(k),TOOLS_get_list(keyword_value))==1 }
            
                    data_temp_x2.loc[0,"该类别不良事件计数"]=str(rmvb1)
                    rmvb2={k:v for k, v in rm.items() if STAT_judge_x(str(k),TOOLS_get_list(keyword_value))!=1 }
                    data_temp_x2.loc[0,"同时存在的其他类别不良事件计数"]=str(rmvb2)    
                    
                    if "-其他关键字-" in str(keyword_value):
                        rmvb1=rmvb2
                        data_temp_x2.loc[0,"该类别不良事件计数"]=    data_temp_x2.loc[0,"同时存在的其他类别不良事件计数"]
                                        
                    data_temp_x2.loc[0,"不良事件总例次"]=str(sum(rmvb1.values()))
                                        
                    #result_all["【国-代码】"] = result_all['关键字标记'].str.extract(r"[【](.*?)[】]", expand=False)
                    #result_all["「国-术语」"] = result_all['关键字标记'].str.extract(r"[「](.*?)[」]", expand=False)
                    #result_all["{IMDRF-代码}"] = result_all['关键字标记'].str.extract("[{](.*?)[}]", expand=False)
                    #result_all["（IMDRF-术语）"] = result_all['关键字标记'].str.extract("[（](.*?)[）]", expand=False)
                    

                    
                    #增加HLT PT等 #器械做了课题的兼容性
                    if ini["模式"]=="药品":
                        for men in ["SOC","HLGT","HLT","PT"]:
                            data_temp_x2[men]=cols[men]
                    if ini["模式"]=="器械":
                        for men in ["国家故障术语集（大类）","国家故障术语集（小类）","IMDRF有关术语（故障）","国家伤害术语集（大类）","国家伤害术语集（小类）","IMDRF有关术语（伤害）"]:
                            data_temp_x2[men]=cols[men]
                    
                    
                    result_all_list.append(data_temp_x2)    
        result_all = pd.concat(result_all_list)
        


        #以下是做一些排版
        result_all=result_all.sort_values(by=["All"], ascending=[False], na_position="last")
        result_all=result_all.reset_index() 

        result_all["All占比"]=round(result_all["All"]/allnumber * 100, 2)
        result_all=result_all.rename(columns={"All": "总数量","All占比": "总数量占比"})
        try:
            result_all=result_all.rename(columns={"其他": "一般"})
        except:
            pass
            
        try:
            result_all=result_all.rename(columns={" 一般": "一般"})
        except:
            pass        
        try:
            result_all=result_all.rename(columns={" 严重": "严重"})
        except:
            pass        
        try:
            result_all=result_all.rename(columns={"严重伤害": "严重"})
        except:
            pass
        try:
            result_all=result_all.rename(columns={"死亡": "死亡(仅支持器械)"})
        except:
            pass

       
        for i in ["一般","新的一般","严重","新的严重"]:
            if i not in result_all.columns:
                result_all[i]=0
        
        try:
            result_all["严重比"]=round((result_all["严重"].fillna(0)+result_all["死亡(仅支持器械)"].fillna(0))/result_all["总数量"] * 100, 2)    
        except:
            result_all["严重比"]=round((result_all["严重"].fillna(0)+result_all["新的严重"].fillna(0))/result_all["总数量"] * 100, 2)     
        
        result_all["构成比"]=round((result_all["不良事件总例次"].astype(float).fillna(0))/result_all["不良事件总例次"].astype(float).sum() * 100, 2)     
        
        if ini["模式"]=="药品":
            try:
                result_all=result_all[["关键字标记","一般","新的一般","严重","新的严重","总数量","总数量占比","严重比","事件分类","不良事件总例次","构成比","该类别不良事件计数","同时存在的其他类别不良事件计数","死亡(仅支持器械)","SOC","HLGT","HLT","PT"]]
            except:
                result_all=result_all[["关键字标记","一般","新的一般","严重","新的严重","总数量","总数量占比","严重比","事件分类","不良事件总例次","构成比","该类别不良事件计数","同时存在的其他类别不良事件计数","SOC","HLGT","HLT","PT"]]
        elif ini["模式"]=="器械":    
            try:
                result_all=result_all[["关键字标记","一般","新的一般","严重","新的严重","总数量","总数量占比","严重比","事件分类","不良事件总例次","构成比","该类别不良事件计数","同时存在的其他类别不良事件计数","死亡(仅支持器械)","国家故障术语集（大类）","国家故障术语集（小类）","IMDRF有关术语（故障）","国家伤害术语集（大类）","国家伤害术语集（小类）","IMDRF有关术语（伤害）"]]
            except:
                result_all=result_all[["关键字标记","一般","新的一般","严重","新的严重","总数量","总数量占比","严重比","事件分类","不良事件总例次","构成比","该类别不良事件计数","同时存在的其他类别不良事件计数","国家故障术语集（大类）","国家故障术语集（小类）","IMDRF有关术语（故障）","国家伤害术语集（大类）","国家伤害术语集（小类）","IMDRF有关术语（伤害）"]]
            
        else:
            try:
                result_all=result_all[["关键字标记","一般","新的一般","严重","新的严重","总数量","总数量占比","严重比","事件分类","不良事件总例次","构成比","该类别不良事件计数","同时存在的其他类别不良事件计数","死亡(仅支持器械)"]]
            except:
                result_all=result_all[["关键字标记","一般","新的一般","严重","新的严重","总数量","总数量占比","严重比","事件分类","不良事件总例次","构成比","该类别不良事件计数","同时存在的其他类别不良事件计数"]]
        
        for idp,cpl in guize2.iterrows():
            result_all.loc[(result_all["关键字标记"].astype(str)==str(cpl["值"])), "排除值"] = cpl["排除值"]  

        result_all["排除值"]=result_all["排除值"].fillna("没有排除值")

        #将有关数字的列转为int

        for x in ["一般","新的一般","严重","新的严重","总数量","总数量占比","严重比"]:
            result_all[x]=result_all[x].fillna(0)
    
        for x in ["一般","新的一般","严重","新的严重","总数量"]:
            result_all[x]=result_all[x].astype(int)


        result_all["RPN"]="未定义"    
        result_all["故障原因"]="未定义"
        result_all["可造成的伤害"]="未定义"
        result_all["应采取的措施"]="未定义"        
        result_all["发生率"]="未定义"        
        
        result_all["报表类型"]="PSUR"    
        return result_all
        




##########################################################$
#深圳中心要求的功能
def threat_class(ori, a, b):
    """完全版的汇总统计，包括分级预警模块核心规则，输入源文件，分级依据a(一般为注册证号），b（批号/型号/规格等），返回ori（处理后的源文件）,groupby（分级预警表格）"""
    # text.insert(END,"\nA级：①死亡报告；②医用耗材和诊断试剂：同一批号的产品严重报告大于3例；③医疗设备：同一注册证号的产品严重报告大于3例。\nB级：①医用耗材和诊断试剂：同一批号的产品3例以上（含）并且有1-2例严重报告；②医疗设备：同一注册证号的产品3例以上（含）并且有1-2例严重报告。\nC级：①医用耗材和诊断试剂：同一批号的产品3例以上（含），但无严重报告；②医疗设备：同一注册证号的产品5例以上（含），但无严重报告。")
    if "证号待评价(药品新的）比例" in ori.columns:
        pass
    else:
        ori[b] = ori[b].fillna("未填写")
        ori["计数项目"] = ori[a].astype(str) + ori[b].astype(str)
        ori["计数"] = "标记"
        ori["该批号报告计数"] = "标记"
        ori["该注册证号报告计数"] = "标记"
        ori.loc[(ori["伤害"] == "严重伤害"), "严重伤害-批号"] = "标记"
        # ori.loc[(ori['单位名称']=="佛山市第一人民医院"),'单位名称']=1
        ori.loc[(ori["伤害"] == "严重伤害"), "严重伤害-证号"] = "标记"
        ori.loc[(ori["伤害"] == "死亡"), "死亡-批号"] = "标记"
        ori.loc[(ori["伤害"] == "死亡"), "死亡-证号"] = "标记"
        ori.loc[(ori["持有人报告状态"] == "待评价"), "证号待评价(药品新的）比例"] = "标记"
        ori.loc[(ori["持有人报告状态"] == "待评价"), "批号待评价(药品新的）比例"] = "标记"

    # 计算与合并
    groupby_pihao = ori.groupby(["计数项目", "上市许可持有人名称", "产品类别", "产品名称", a, b]).aggregate(
        {
            "该批号报告计数": "count",
            "严重伤害-批号": "count",
            "死亡-批号": "count",
            "批号待评价(药品新的）比例": "count",
            "计数": "count",
        }
    )
    # 这里有问题
    groupby_zhenghao = ori.groupby(["上市许可持有人名称", "产品类别", "产品名称", a]).aggregate(
        {
            "该注册证号报告计数": "count",
            "证号待评价(药品新的）比例": "count",
            "严重伤害-证号": "count",
            "死亡-证号": "count",
        }
    )
    # 这里有问题
    groupby_pihao = groupby_pihao.reset_index()
    groupby_zhenghao = groupby_zhenghao.reset_index()
    groupby = pd.merge(
        groupby_pihao,
        groupby_zhenghao,
        on=["上市许可持有人名称", "产品类别", "产品名称", a],
        how="outer",
    )
    groupby["预警分级"] = "E"

    groupby["证号待评价(药品新的）比例"] = round(
        groupby["证号待评价(药品新的）比例"] / groupby["该注册证号报告计数"] * 100, 0
    )
    groupby["批号待评价(药品新的）比例"] = round(
        groupby["批号待评价(药品新的）比例"] / groupby["该批号报告计数"] * 100, 0
    )
    groupby = groupby[
        [
            "预警分级",
            "该注册证号报告计数",
            "该批号报告计数",
            "证号待评价(药品新的）比例",
            "批号待评价(药品新的）比例",
            "上市许可持有人名称",
            "产品类别",
            "产品名称",
            a,
            b,
            "严重伤害-证号",
            "严重伤害-批号",
            "死亡-批号",
            "死亡-证号",
            "计数",
            "计数项目",
        ]
    ]
    groupby["计数"] = groupby["计数"].fillna(0)
    groupby["严重伤害-批号"] = groupby["严重伤害-批号"].fillna(0)
    groupby["严重伤害-证号"] = groupby["严重伤害-证号"].fillna(0)
    groupby["死亡-批号"] = groupby["死亡-批号"].fillna(0)
    groupby["死亡-证号"] = groupby["死亡-证号"].fillna(0)
    groupby["该注册证号报告计数"] = groupby["该注册证号报告计数"].fillna(0)
    groupby["该批号报告计数"] = groupby["该批号报告计数"].fillna(0)
    groupby["计数"] = groupby["计数"].astype(int)
    groupby["严重伤害-批号"] = groupby["严重伤害-批号"].astype(int)
    groupby["严重伤害-证号"] = groupby["严重伤害-证号"].astype(int)
    groupby["该注册证号报告计数"] = groupby["该注册证号报告计数"].astype(int)
    groupby["死亡-批号"] = groupby["死亡-批号"].astype(int)
    groupby["死亡-证号"] = groupby["死亡-证号"].astype(int)
    groupby["证号待评价(药品新的）比例"] = groupby["证号待评价(药品新的）比例"].astype(int)
    groupby["批号待评价(药品新的）比例"] = groupby["批号待评价(药品新的）比例"].astype(int)

    for index, columns in groupby.iterrows():

        # 无源产品
        if columns["产品类别"] == "无源" and columns["严重伤害-批号"] >= 3:
            groupby.loc[index, "预警分级"] = "A"

        elif (
            columns["产品类别"] == "无源"
            and columns["计数"] >= 3
            and columns["严重伤害-批号"] < 3
            and columns["严重伤害-批号"] >= 1
        ):
            groupby.loc[index, "预警分级"] = "B"

        elif columns["产品类别"] == "无源" and columns["计数"] >= 5:
            groupby.loc[index, "预警分级"] = "C"
            
        elif columns["产品类别"] == "无源" and columns["计数"] >= 3:
            groupby.loc[index, "预警分级"] = "D"
                        
        # 诊断试剂
        elif columns["产品类别"] == "体外诊断试剂" and columns["严重伤害-批号"] >= 3:
            groupby.loc[index, "预警分级"] = "A"

        elif (
            columns["产品类别"] == "体外诊断试剂"
            and columns["计数"] >= 3
            and columns["严重伤害-批号"] < 3
            and columns["严重伤害-批号"] >= 1
        ):
            groupby.loc[index, "预警分级"] = "B"

        elif columns["产品类别"] == "体外诊断试剂" and columns["计数"] >= 5:
            groupby.loc[index, "预警分级"] = "C"
            
        elif columns["产品类别"] == "体外诊断试剂" and columns["计数"] >= 3:
            groupby.loc[index, "预警分级"] = "D"            
            
        # 有源产品
        elif columns["产品类别"] == "有源" and columns["严重伤害-证号"] >= 3:
            groupby.loc[index, "预警分级"] = "A"

        elif (
            columns["产品类别"] == "有源"
            and columns["该注册证号报告计数"] >= 3
            and columns["严重伤害-证号"] < 3
            and columns["严重伤害-证号"] >= 1
        ):
            groupby.loc[index, "预警分级"] = "B"

        elif columns["产品类别"] == "有源" and columns["该注册证号报告计数"] >= 5:
            groupby.loc[index, "预警分级"] = "C"
            

        elif columns["产品类别"] == "有源" and columns["该注册证号报告计数"] >= 3:
            groupby.loc[index, "预警分级"] = "D"
            
            # print(groupby.loc[index,"预警分级"],"ccccccccccccccccccccccccccccccccc")
        elif columns["死亡-批号"] > 0:  ####
            groupby.loc[index, "预警分级"] = "!A"  ####
    groupby = groupby.sort_values(
        by=["预警分级", "该注册证号报告计数", "计数"],
        ascending=[True, False, False],
        na_position="last",
    ).reset_index(drop=True)
    ori = ori.reset_index()

    return [ori, groupby]


def easyread_sz(ori):
    """规整查看：易读格式预警"""
    try:
        kdxxx = len(ori["报告编码"])
    except:
        showinfo(title="错误信息", message="未选择文件或文件数据读取错误。")
        return 0

    groupby_zhenghao = threat_class(ori, "注册证编号/曾用注册证编号", "产品批号")[1].reset_index()
    xs = [
        "死亡-批号",
        "批号待评价(药品新的）比例",
        "死亡-证号",
        "该批号报告计数",
        "证号待评价(药品新的）比例",
        "该注册证号报告计数",
        "严重伤害-批号",
        "严重伤害-证号",
    ]
    for x in xs:
        try:
            ori.drop(x, axis=1, inplace=True)
        except:
            pass
    ori_owercount_all = pd.merge(
        ori,
        groupby_zhenghao,
        on=["上市许可持有人名称", "产品类别", "产品名称", "注册证编号/曾用注册证编号", "产品批号"],
        how="outer",
    )
    ori_owercount_all["分隔符"] = "●"
    ori_owercount_all["上报机构描述"] = (
        ori_owercount_all["使用过程"].astype("str")
        + ori_owercount_all["分隔符"]
        + ori_owercount_all["事件原因分析"].astype("str")
        + ori_owercount_all["分隔符"]
        + ori_owercount_all["事件原因分析描述"].astype("str")
        + ori_owercount_all["分隔符"]
        + ori_owercount_all["初步处置情况"].astype("str")
    )
    ori_owercount_all["持有人处理描述"] = (
        ori_owercount_all["关联性评价"].astype("str")
        + ori_owercount_all["分隔符"]
        + ori_owercount_all["调查情况"].astype("str")
        + ori_owercount_all["分隔符"]
        + ori_owercount_all["事件原因分析"].astype("str")
        + ori_owercount_all["分隔符"]
        + ori_owercount_all["具体控制措施"].astype("str")
        + ori_owercount_all["分隔符"]
        + ori_owercount_all["未采取控制措施原因"].astype("str")
    )
    ori_owercount_easyread = ori_owercount_all[
        [
            "报告编码",
            "预警分级",
            "事件发生日期",
            "报告日期",
            "单位名称",
            "产品名称",
            "注册证编号/曾用注册证编号",
            "该注册证号报告计数",
            "产品批号",
            "该批号报告计数",
            "型号",
            "规格",
            "上市许可持有人名称",
            "管理类别",
            "伤害",
            "伤害表现",
            "器械故障表现",
            "上报机构描述",
            "持有人处理描述",
            "经营企业使用单位报告状态",
            "监测机构",
            "产品类别",
            "医疗机构类别",
            "年龄",
            "年龄类型",
            "性别",
            "证号待评价(药品新的）比例",
            "批号待评价(药品新的）比例",
            "严重伤害-证号",
            "严重伤害-批号",
            "死亡-批号",
            "死亡-证号",
        ]
    ]  # 证号风险
    ori_owercount_easyread = ori_owercount_easyread.sort_values(
        by=["该注册证号报告计数", "注册证编号/曾用注册证编号", "该批号报告计数"],
        ascending=[False, False, False],
        na_position="last",
    )
    ori_owercount_easyread["该注册证号报告计数"] = ori_owercount_easyread["该注册证号报告计数"].fillna(0)
    ori_owercount_easyread["该批号报告计数"] = ori_owercount_easyread["该批号报告计数"].fillna(0)
    ori_owercount_easyread["该注册证号报告计数"] = ori_owercount_easyread["该注册证号报告计数"].astype(
        int
    )
    ori_owercount_easyread["该批号报告计数"] = ori_owercount_easyread["该批号报告计数"].astype(int)
    ori_owercount_easyread = ori_owercount_easyread.reset_index(drop=True)

    # 深圳中心要求的：
    ori_owercount_easyread["深圳规则"] = 3
    ori_owercount_easyread["产品名称"] = ori_owercount_easyread["产品名称"].astype(str)
    for index, columns in ori_owercount_easyread.iterrows():
        # print(columns["该注册证号报告计数"])
        # 无源产品
        if (
            columns["产品类别"] == "无源"
            and columns["严重伤害-批号"] >= 1
            and columns["该批号报告计数"] >= 3
        ):
            ori_owercount_easyread.loc[index, "深圳规则"] = 1

        elif columns["产品类别"] == "体外诊断试剂" and columns["该批号报告计数"] >= 3:
            ori_owercount_easyread.loc[index, "深圳规则"] = 1

        elif columns["产品类别"] == "有源" and columns["严重伤害-证号"] >= 3:
            ori_owercount_easyread.loc[index, "深圳规则"] = 1

        if (
            "宫内节育" in ori_owercount_easyread.loc[index, "产品名称"]
            and ori_owercount_easyread.loc[index, "深圳规则"] == 1
        ):
            ori_owercount_easyread.loc[index, "深圳规则"] = 2
        if columns["死亡-批号"] >= 1:
            ori_owercount_easyread.loc[index, "深圳规则"] = 1
    ori_owercount_easyread = ori_owercount_easyread.sort_values(by=['预警分级', '注册证编号/曾用注册证编号'], ascending=[True, True])

    return ori_owercount_easyread

###########################################################
      
#####第四部分：主界面 ########################################################################





def A0000_Main():
    print("")

if 1==1:
    

    root = Tk.Tk()
    root.title(title_all)
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
    #root.configure(bg="steelblue")#royalblue

    
    # 进度条以及完成程度
    framecanvas = Frame(root)  # .grid(row = 0,column = 0)#使用时将框架根据情况选择新的位置
    canvas = Canvas(framecanvas, width=680, height=30)  # ,bg = "white")
    canvas.pack()
    x = StringVar()
    out_rec = canvas.create_rectangle(5, 5, 680, 25, outline="silver", width=1)
    fill_rec = canvas.create_rectangle(5, 5, 5, 25, outline="", width=0, fill="silver")
    canvas.create_text(350, 15, text="总执行进度")
    framecanvas.pack()




    #sysu = ttk.Style()
    ##############窗口按钮########################
    try:
        frame0 = ttk.Frame(root, width=90, height=20)
        frame0.pack(side=LEFT)
        B_open_files1 = Button(
            frame0,
            text="导入数据",
            bg="white",
            height=2,
            width=12,
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=TOOLS_allfileopen,
        )
        B_open_files1.pack()
            
        
        

        B_open_files3 = Button(
            frame0,
            text="数据查看",
            bg="white",
            height=2,
            width=12,
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TABLE_tree_Level_2(ori, 0, ori),
        )
        B_open_files3.pack()
        

    except:
        pass


    ##############提示框########################
    text = ScrolledText(root, height=400, width=400, bg="#FFFFFF")
    text.pack(padx=5, pady=5)
    text.insert(
        END, "\n 本程序适用于整理和分析国家医疗器械不良事件信息系统、国家药品不良反应监测系统和国家化妆品不良反应监测系统中导出的监测数据。\n\n 20240306 增加了国家药品新系统的兼容性。\n\n 20240329 修复了初始打开文件看不到xlsx格式的问题。\n\n 20240402 修改药品超时报告统计规则为国家中心接收时间-报告日期。"
    )
    text.insert(END, "\n\n")

    #序列好验证、配置表生成与自动更新。
    setting_cfg=read_setting_cfg()
    generate_random_file()
    setting_cfg=open_setting_cfg()
    if setting_cfg["settingdir"]==0:
        showinfo(title="提示", message="未发现默认配置文件夹，请选择一个。如该配置文件夹中并无配置文件，将生成默认配置文件。")
        filepathu=filedialog.askdirectory()
        path=get_directory_path(filepathu)
        
        filepathu=os.path.normpath(filepathu)

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
    
    

    
    ##############启动界面#######################
    #root_x0 = Toplevel()
    #tMain = threading.Thread(target=PROGRAM_showWelcome)
    #tMain.start()
    #t1 = threading.Thread(target=PROGRAM_closeWelcome)
    #t1.start()

    #root.lift()
    #root.attributes("-topmost", True)
    #root.attributes("-topmost", False)


    #root.deiconify() # show lab window
    root.mainloop()
    print("done.")

    

