#!/usr/bin/env python
# coding: utf-8
import os
import json
import xml.etree.ElementTree as ET
import random
import datetime
import time
from tkinter import Tk, Toplevel, ttk, Button, Label, Entry, filedialog, messagebox, LEFT, END, GROOVE
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog  # 导入 simpledialog
import requests
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import xml.etree.ElementTree as ET
import os
import tempfile
import re
# 全局变量
global version_now
global usergroup
global setting_cfg
global csdir
global userxml
global pandas_ver
import webbrowser
import platform
import subprocess
import sys
import shutil
import pandas as pd
version_now = "3.6.6 信创兼容版本"
usergroup = "用户组=0"
setting_cfg = {}
userxml=os.path.join(os.path.dirname(__file__), 'user.xml')

# 获取当前脚本所在目录
csdir = os.path.dirname(os.path.abspath(__file__))
python_executable = shutil.which('python3') or shutil.which('python')
#print(python_executable)
def run_apps():
    print('done.')


def check_pandas_version():
    """检查pandas版本是否为1.0.0以上"""
    try:
        from packaging import version
    except ImportError:
        raise ImportError(
            "缺少依赖: 需要 'packaging' 包来比较版本\n"
            "请使用命令安装: pip install packaging"
        )
    
    min_version = '1.0.0'
    current_version = pd.__version__
    
    if version.parse(current_version) < version.parse(min_version):
        print(f"pandas版本较低(要求1.0.0以上），部分功能无法加载: {current_version}")
        return 0
    else:
        print(f"pandas版本兼容，加载所有功能: {current_version}")
        return 1       
pandas_ver=check_pandas_version()
   

def run_encrypted_client_app():
    global aaaa
    aaaa = {'group': '用户未登录', 'username': '用户未登录'}
    
    # AES加密配置
    AES_KEY = b'your_aes_key_32bytes_1234567890abcdef'[:32]

    def aes_encrypt(data):
        cipher = AES.new(AES_KEY, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv, ct

    def aes_decrypt(iv, ct):
        try:
            iv = base64.b64decode(iv)
            ct = base64.b64decode(ct)
            cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode('utf-8')
        except:
            return None

    def get_csrf_token():
        try:
            response = requests.get("http://159.75.253.250:5000/", timeout=3)
            return response.cookies.get('csrf_token')
        except:
            return ""

    def call_api(username_iv, username_ct, password_iv, password_ct):
        url = "http://159.75.253.250:5000/api/get_user_group"
        payload = {
            "username_iv": username_iv,
            "username_ct": username_ct,
            "password_iv": password_iv,
            "password_ct": password_ct
        }
        headers = {
            "Content-Type": "application/json",
            "X-CSRFToken": get_csrf_token()
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=3)
            if response.status_code == 200:
                global aaaa
                aaaa = response.json()
                return True
            return False
        except:
            return False

    def check_server_available():
        """检查服务器是否可用"""
        try:
            requests.get("http://159.75.253.250:5000/", timeout=3)
            return True
        except:
            return False

    def save_to_xml(username_iv, username_ct, password_iv, password_ct):
        """保存加密后的凭据到XML"""
        root = ET.Element("user")
        ET.SubElement(root, "username_iv").text = username_iv
        ET.SubElement(root, "username_ct").text = username_ct
        ET.SubElement(root, "password_iv").text = password_iv
        ET.SubElement(root, "password_ct").text = password_ct
        tree = ET.ElementTree(root)
        tree.write(userxml, encoding='utf-8', xml_declaration=True)

    def read_from_xml():
        """从XML读取加密凭据"""
        if not os.path.exists(userxml):
            return None, None, None, None
        try:
            tree = ET.parse(userxml)
            root = tree.getroot()
            username_iv = root.find("username_iv").text
            username_ct = root.find("username_ct").text
            password_iv = root.find("password_iv").text
            password_ct = root.find("password_ct").text
            return username_iv, username_ct, password_iv, password_ct
        except:
            return None, None, None, None

    def open_register_page():
        webbrowser.open("http://159.75.253.250:5000/register")

    def create_login_window():
        """创建登录窗口"""
        root = tk.Tk()
        root.title("用户登录")
        root.configure(bg='steelblue')
        
        # 窗口样式设置
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='steelblue')
        style.configure('TLabel', background='steelblue', foreground='white', font=('微软雅黑', 10))
        style.configure('TButton', font=('微软雅黑', 10), padding=5)
        style.map('TButton', 
                background=[('active', 'dodgerblue'), ('!active', 'lightsteelblue')],
                foreground=[('active', 'white'), ('!active', 'black')])

        # 窗口居中
        window_width = 450
        window_height = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(expand=True, fill='both')

        # 标题
        title_label = ttk.Label(main_frame, text="用户登录", font=('微软雅黑', 14, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # 输入框框架
        entry_frame = ttk.Frame(main_frame)
        entry_frame.grid(row=1, column=0, pady=10)

        # 用户名输入
        ttk.Label(entry_frame, text="用户名:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        entry_username = ttk.Entry(entry_frame, width=25)
        entry_username.grid(row=0, column=1, padx=5, pady=5)

        # 密码输入
        ttk.Label(entry_frame, text="密码:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        entry_password = ttk.Entry(entry_frame, show="*", width=25)
        entry_password.grid(row=1, column=1, padx=5, pady=5)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        def create_register_window_2():
            root.destroy()
            create_register_window()
        def on_submit():
            username = entry_username.get()
            password = entry_password.get()

            if not username or not password:
                messagebox.showerror("错误", "用户名和密码不能为空")
                return

            # 加密用户凭据
            username_iv, username_ct = aes_encrypt(username)
            password_iv, password_ct = aes_encrypt(password)

            if call_api(username_iv, username_ct, password_iv, password_ct):
                # 验证成功才保存凭据
                save_to_xml(username_iv, username_ct, password_iv, password_ct)
                root.destroy()
                load_ui(aaaa)
            else:
                messagebox.showerror("错误", "登录失败，请检查用户名和密码")

        ttk.Button(button_frame, text="登录", command=on_submit).pack(side='left', padx=5)
        ttk.Button(button_frame, text="注册", command=create_register_window_2).pack(side='left', padx=5)

        # 登录说明
        info_text = "您需要使用账号登录，以进行用户登记和自动获取对应的更新。\n如无账号请点击注册，之后使用注册的账号和密码登录。"
        ttk.Label(main_frame, text=info_text, wraplength=400, justify='center').grid(row=3, column=0, pady=(20, 0))

        root.mainloop()

    # 主逻辑
    server_available = check_server_available()
    
    if not server_available:
        # 服务器不可用，直接进入离线模式
        aaaa.update({'group': '离线模式', 'username': '离线用户'})
        load_ui(aaaa)
        return
    
    # 服务器可用，继续正常流程
    credentials = read_from_xml()
    
    if all(credentials):
        # 有保存的凭据，尝试验证
        username_iv, username_ct, password_iv, password_ct = credentials
        if call_api(username_iv, username_ct, password_iv, password_ct):
            load_ui(aaaa)
        else:
            # 验证失败，弹出登录框
            create_login_window()
    else:
        # 没有保存的凭据，弹出登录框
        create_login_window()
def update_database_local():
    import zipfile
    import os
    from tkinter import messagebox, filedialog
    import xml.etree.ElementTree as ET
    import random
    from datetime import datetime
    
    # 获取工作目录从setting.xml
    def get_work_dir():
        try:
            setting_file = os.path.join(os.path.dirname(__file__), 'setting.xml')
            if os.path.exists(setting_file):
                tree = ET.parse(setting_file)
                root = tree.getroot()
                work_dir = root.find('work_dir').text
                return work_dir
            return os.path.dirname(__file__)  # 默认返回程序目录
        except Exception as e:
            print(f"读取setting.xml失败: {str(e)}")
            return os.path.dirname(__file__)
    
    # 创建备份函数
    def create_backup(work_dir):
        try:
            # 创建backup目录
            backup_dir = os.path.join(work_dir, 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名: 日期+两位随机数
            now = datetime.now()
            random_num = random.randint(10, 99)
            backup_filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{random_num}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 创建ZIP文件
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(work_dir):
                    # 跳过backup目录
                    if 'backup' in dirs:
                        dirs.remove('backup')
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 跳过备份文件本身（如果存在）
                        if file_path == backup_path:
                            continue
                        # 计算相对路径
                        arcname = os.path.relpath(file_path, work_dir)
                        try:
                            zipf.write(file_path, arcname)
                        except Exception as e:
                            print(f"无法备份文件 {file_path}: {str(e)}")
                            continue
            
            return backup_path
        except Exception as e:
            print(f"创建备份失败: {str(e)}")
            return None

    # 让用户选择ZIP文件
    def select_zip_file():
        filetypes = [('ZIP压缩包', '*.zip'), ('所有文件', '*.*')]
        zip_path = filedialog.askopenfilename(
            title='选择资源库更新包',
            initialdir=os.path.expanduser('~'),
            filetypes=filetypes
        )
        return zip_path if zip_path else None

    # 获取工作目录
    work_dir = get_work_dir()

    # 让用户选择ZIP文件
    zip_path = select_zip_file()
    if not zip_path:
        return  # 用户取消了选择

    try:
        # 首先创建备份
        backup_path = create_backup(work_dir)
        if backup_path:
            print("正在更新资源库...\n已创建备份文件:", os.path.basename(backup_path))
        else:
            if messagebox.askyesno("备份失败", "正在更新资源库，但创建备份失败，是否继续更新？") == False:
                return
        
        # 解压ZIP文件到工作目录（支持中文文件名）
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 先获取所有文件列表
            for file_info in zip_ref.infolist():
                try:
                    # 正确解码文件名（支持中文）
                    original_filename = file_info.filename
                    try:
                        # 尝试UTF-8解码
                        file_info.filename = original_filename.encode('cp437').decode('gbk')
                    except:
                        try:
                            # 尝试其他编码方式
                            file_info.filename = original_filename.encode('cp437').decode('utf-8')
                        except:
                            # 如果还是失败，保持原样
                            file_info.filename = original_filename
                    
                    # 解压文件
                    zip_ref.extract(file_info, work_dir)
                    print(f"已解压文件: {file_info.filename} 到 {work_dir}")
                except Exception as e:
                    messagebox.showwarning("警告", f"解压文件 {file_info.filename} 时出错: {str(e)}")
                    continue
        
        messagebox.showinfo("成功", "资源库已成功更新！")
        
    except zipfile.BadZipFile:
        messagebox.showerror("错误", "选择的文件不是有效的ZIP压缩包")
    except Exception as e:
        messagebox.showerror("错误", f"更新资源库时出错: {str(e)}")         
def update_database(filename):
    import zipfile
    import shutil
    import requests
    import tempfile
    import os
    from tkinter import messagebox
    import xml.etree.ElementTree as ET
    import random
    from datetime import datetime
    
    # 检查服务器连通性
    def check_server_connection():
        try:
            response = requests.get("http://159.75.253.250:5000/", timeout=3)
            print('资源库更新检查中...')
            return response.status_code == 200
        except:
            return False
    
    # 获取工作目录从setting.xml
    def get_work_dir():
        try:
            setting_file = os.path.join(os.path.dirname(__file__), 'setting.xml')
            if os.path.exists(setting_file):
                tree = ET.parse(setting_file)
                root = tree.getroot()
                work_dir = root.find('work_dir').text
                return work_dir
            return os.path.dirname(__file__)  # 默认返回程序目录
        except Exception as e:
            print(f"读取setting.xml失败: {str(e)}")
            return os.path.dirname(__file__)
    
    # 创建备份函数
    def create_backup(work_dir):
        try:
            # 创建backup目录
            backup_dir = os.path.join(work_dir, 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名: 日期+两位随机数
            now = datetime.now()
            random_num = random.randint(10, 99)
            backup_filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{random_num}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 创建ZIP文件
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(work_dir):
                    # 跳过backup目录
                    if 'backup' in dirs:
                        dirs.remove('backup')
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 跳过备份文件本身（如果存在）
                        if file_path == backup_path:
                            continue
                        # 计算相对路径
                        arcname = os.path.relpath(file_path, work_dir)
                        try:
                            zipf.write(file_path, arcname)
                        except Exception as e:
                            print(f"无法备份文件 {file_path}: {str(e)}")
                            continue
            
            return backup_path
        except Exception as e:
            print(f"创建备份失败: {str(e)}")
            return None

    # 获取本地版本号（从work_dir/version.txt读取）
    def get_local_version():
        work_dir = get_work_dir()
        version_file = os.path.join(work_dir, 'version.txt')
        try:
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            return "0.0.0"  # 默认版本号
        except Exception as e:
            print(f"读取版本文件失败: {str(e)}")
            return "0.0.0"

    # 首先检查服务器连通性
    if not check_server_connection():
        work_dir = get_work_dir()
        db_file = os.path.join(work_dir, '0（范例）比例失衡关键字库.xls')
        
        if not os.path.exists(db_file):
            messagebox.showerror("错误", "未配置资源库，网络不通，请手动离线配置。")
        else:
            print("网络不通，无法自动更新资源库")
        return  # 无论是否存在db文件，都直接返回

    # 如果服务器可连接，继续原有流程
    version_url = "http://159.75.253.250:5000/api/download_file"
    version_payload = {
        "username_iv": 'NheVgRrBk8hl0qe0/bf6AA==',
        "username_ct": 't7TaVtUIUHWACMhphF3cZg==',
        "password_iv": 'wl0nvIIYwto+aC/lH8fUwg==',
        "password_ct": 'rTJ8uG9iMUYgtJotz83clQ==',
        "filename": "easypvver.txt",
    }
    
    try:
        # 获取本地版本
        local_version = get_local_version()
        
        # 获取服务器版本
        response = requests.post(version_url, json=version_payload)
        if response.status_code != 200:
            messagebox.showerror("错误", f"无法获取服务器版本: {response.text}")
            return
            
        server_version = response.text.strip()
        if not server_version:
            messagebox.showerror("错误", "服务器版本号无效")
            return
            
        # 比较版本
        from packaging import version
        if version.parse(server_version) <= version.parse(local_version):
            print(f"当前资源库版本 {local_version} 已经是最新版本，无需更新。")
            return
            
        # 如果服务器版本较新，则进行更新
        # 首先创建备份
        work_dir = get_work_dir()
        backup_path = create_backup(work_dir)
        if backup_path:
            print("检测到资源库有更新版本,正在更新资源库。\n正在创建原来的资源库备份...", f"已创建备份文件: {os.path.basename(backup_path)}")
        else:
            if messagebox.askyesno("备份失败", "检测到资源库有更新版本,正在更新资源库。但原来的资源库创建备份失败，是否继续更新？") == False:
                return
        
        url = "http://159.75.253.250:5000/api/download_file"
        payload = {
            "username_iv": 'NheVgRrBk8hl0qe0/bf6AA==',
            "username_ct": 't7TaVtUIUHWACMhphF3cZg==',
            "password_iv": 'wl0nvIIYwto+aC/lH8fUwg==',
            "password_ct": 'rTJ8uG9iMUYgtJotz83clQ==',
            "filename": filename,
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            # 保存ZIP到临时文件
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
                temp_zip.write(response.content)
                zip_path = temp_zip.name
            
            # 创建目标目录（如果不存在）
            os.makedirs(work_dir, exist_ok=True)
            
            # 解压ZIP文件到工作目录（支持中文文件名）
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 先获取所有文件列表
                for file_info in zip_ref.infolist():
                    try:
                        # 正确解码文件名（支持中文）
                        original_filename = file_info.filename
                        try:
                            # 尝试UTF-8解码
                            file_info.filename = original_filename.encode('cp437').decode('gbk')
                        except:
                            try:
                                # 尝试其他编码方式
                                file_info.filename = original_filename.encode('cp437').decode('utf-8')
                            except:
                                # 如果还是失败，保持原样
                                file_info.filename = original_filename
                        
                        # 解压文件
                        zip_ref.extract(file_info, work_dir)
                        print(f"已解压文件: {file_info.filename} 到 {work_dir}")
                    except Exception as e:
                        messagebox.showwarning("警告", f"解压文件 {file_info.filename} 时出错: {str(e)}")
                        continue
            
            messagebox.showinfo("资源库更新成功", f"检测到资源库有更新版本。成功从版本 {local_version} 更新到 {server_version}！")
        else:
            messagebox.showerror("错误", f"文件下载失败: {response.text}")
    except Exception as e:
        print(f"处理文件时出现异常: {str(e)}")
    finally:
        # 确保删除临时ZIP文件
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.unlink(zip_path)
            
def create_register_window():
    """创建蓝色主题的注册窗口"""
    # 加密相关函数定义
    AES_KEY = b'your_aes_key_32bytes_1234567890abcdef'[:32]
    
    def is_valid_password(password):
        if len(password) < 6:
            return False
        if not re.search(r'[A-Za-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

    def aes_encrypt(data):
        cipher = AES.new(AES_KEY, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv, ct

    def save_to_xml(username_iv, username_ct, password_iv, password_ct):
        root = ET.Element("user")
        ET.SubElement(root, "username_iv").text = username_iv
        ET.SubElement(root, "username_ct").text = username_ct
        ET.SubElement(root, "password_iv").text = password_iv
        ET.SubElement(root, "password_ct").text = password_ct
        tree = ET.ElementTree(root)
        tree.write(userxml, encoding='utf-8', xml_declaration=True)

    # 创建主窗口
    root = tk.Tk()
    root.title("用户注册")
    
    # 设置全局蓝色主题
    root.configure(bg='steelblue')
    style = ttk.Style()
    
    # 使用clam主题作为基础，然后自定义蓝色风格
    style.theme_use('clam')
    
    # 配置各种蓝色风格的组件
    style.configure('.', background='steelblue', foreground='white')
    style.configure('TFrame', background='steelblue')
    style.configure('TLabel', background='steelblue', foreground='white', font=('微软雅黑', 10))
    style.configure('TButton', font=('微软雅黑', 10), padding=5, 
                  background='lightsteelblue', foreground='black')
    style.map('TButton',
             background=[('active', 'dodgerblue'), ('pressed', 'dodgerblue')],
             foreground=[('active', 'white')])
    # 配置蓝色风格（关键修改：输入框样式）
    style.configure('TEntry', 
                  fieldbackground='aliceblue',  # 输入框背景色
                  foreground='black',           # 字体颜色设为黑色
                  font=('微软雅黑', 10),
                  padding=5,
                  insertcolor='black')          # 光标颜色
    
    # 确保获得焦点时保持黑色文字
    style.map('TEntry',
             foreground=[('active', 'black')],
             fieldbackground=[('active', 'aliceblue')])
    # 窗口居中
    window_width = 400
    window_height = 450
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 主框架 - 使用Frame而不是TTK Frame以获得更好的背景控制
    main_frame = tk.Frame(root, bg='steelblue', padx=20, pady=20)
    main_frame.pack(expand=True, fill='both')

    # 标题
    title_label = tk.Label(main_frame, text="用户注册", 
                         font=('微软雅黑', 16, 'bold'),
                         bg='steelblue', fg='white')
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # 输入字段
    fields = [
        ("用户名*", "username"),
        ("密码*", "password"),
        ("组织机构*", "organization"),
        ("联系人*", "contact_person"),
        ("电话*", "phone"),
        ("邮箱*", "email")
    ]

    entries = {}
    for i, (label_text, field_name) in enumerate(fields, start=1):
        # 标签使用标准Label以保持蓝色背景
        tk.Label(main_frame, text=label_text, bg='steelblue', fg='white',
                font=('微软雅黑', 10)).grid(row=i, column=0, padx=5, pady=5, sticky='e')
        
        # 输入框使用ttk.Entry以保持风格一致
        entry = ttk.Entry(main_frame, width=25, font=('微软雅黑', 10))
        entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
        entries[field_name] = entry
        if field_name == "password":
            entry.config(show="*")

    # 密码强度提示
    tk.Label(main_frame, text="*密码需至少6位且包含字母和数字", 
            bg='steelblue', fg='white', font=('微软雅黑', 8)).grid(
            row=len(fields)+1, column=1, sticky='w', pady=(0, 10))

    # 按钮框架
    button_frame = tk.Frame(main_frame, bg='steelblue')
    button_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=15)

    def on_register():
        # 收集数据
        data = {
            'username': entries['username'].get(),
            'password': entries['password'].get(),
            'organization': entries['organization'].get(),
            'contact_person': entries['contact_person'].get(),
            'phone': entries['phone'].get(),
            'email': entries['email'].get()
        }

        # 验证必填字段
        if not all(data.values()):
            messagebox.showerror("错误", "请填写所有必填字段（标*的）")
            return

        if not is_valid_password(data['password']):
            messagebox.showerror("错误", "密码必须至少6位且包含字母和数字")
            return

        try:
            response = requests.post(
                "http://159.75.253.250:5000/api/register_user",
                json=data,
                timeout=3
            )
            
            if response.status_code == 201:
                username_iv, username_ct = aes_encrypt(data['username'])
                password_iv, password_ct = aes_encrypt(data['password'])
                save_to_xml(username_iv, username_ct, password_iv, password_ct)
                
                global aaaa
                aaaa.update({
                    'username': data['username'],
                    'group': response.json().get('group', 'vip')
                })
                
                messagebox.showinfo("成功", "注册成功！")
                root.destroy()
                load_ui(aaaa)
            else:
                error_msg = response.json().get('error', '注册失败')
                messagebox.showerror("错误", error_msg)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("错误", f"无法连接到服务器: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")

    # 使用ttk.Button以保持风格一致
    register_btn = ttk.Button(button_frame, text="注册并登录", command=on_register)
    register_btn.pack(side='left', padx=10, ipadx=10)
    
    cancel_btn = ttk.Button(button_frame, text="取消", command=root.destroy)
    cancel_btn.pack(side='left', padx=10, ipadx=10)

    root.mainloop()
           
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

def load_setting_cfg(file_path):
    """加载 setting.cfg 文件"""
    with open(file_path, 'r', encoding='gb18030') as file:
        content = file.read()
        setting_dict = eval(content)
        return setting_dict

def generate_setting_xml(setting_dict, output_path):
    """生成 setting.xml 文件"""
    settings = ET.Element("settings")
    python_command = ET.SubElement(settings, "python_command")
    python_command.text = "python"
    work_dir = ET.SubElement(settings, "work_dir")
    work_dir.text = setting_dict['settingdir']
    check_interval = ET.SubElement(settings, "check_interval")
    check_interval.text = "60000"
    tree = ET.ElementTree(settings)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
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
def check_and_generate_files():
    """检查并生成 setting.cfg 和 setting.xml 文件"""
    cfg_file_path = os.path.join(csdir, 'setting.cfg')
    xml_file_path = os.path.join(csdir, 'setting.xml')
    
    # 检查并生成 setting.cfg
    if not os.path.exists(cfg_file_path):
        default_setting_dir = os.path.join(os.path.expanduser('~'), 'easypv')
        if not os.path.exists(default_setting_dir):
            os.makedirs(default_setting_dir)
            extract_zip_file(def_path, default_setting_dir)
        setting_cfg_content = {'settingdir': default_setting_dir, 'sidori': random.randint(200000, 299999), 'sidfinal': '11111180000808'}
        with open(cfg_file_path, 'w', encoding='gb18030') as f:
            f.write(str(setting_cfg_content))
    
    # 检查并生成 setting.xml
    if not os.path.exists(xml_file_path):
        setting_dict = load_setting_cfg(cfg_file_path)
        generate_setting_xml(setting_dict, xml_file_path)

def read_setting_cfg():
    """读取 setting.cfg 文件"""
    global csdir
    cfg_file_path = os.path.join(csdir, 'setting.cfg')
    if os.path.exists(cfg_file_path):
        with open(cfg_file_path, 'r', encoding='gb18030') as f:
            setting_cfg = eval(f.read())
    else:
        setting_cfg = {'settingdir': 0, 'sidori': 0, 'sidfinal': '11111180000808'}
        with open(cfg_file_path, 'w', encoding='gb18030') as f:
            f.write(str(setting_cfg))
    return setting_cfg

def open_setting_cfg():
    """打开 setting.cfg 文件"""
    global csdir
    cfg_file_path = os.path.join(csdir, 'setting.cfg')
    with open(cfg_file_path, 'r', encoding='gb18030') as f:
        setting_cfg = eval(f.read())
    return setting_cfg

def update_setting_cfg(keys, values):
    """更新 setting.cfg 文件"""
    global csdir
    cfg_file_path = os.path.join(csdir, 'setting.cfg')
    with open(cfg_file_path, 'r', encoding='gb18030') as f:
        setting_cfg = eval(f.read())
    setting_cfg[keys] = values
    with open(cfg_file_path, 'w', encoding='gb18030') as f:
        f.write(str(setting_cfg))

def generate_random_file():
    """生成随机数并更新 setting.cfg"""
    global csdir
    random_number = random.randint(200000, 299999)
    update_setting_cfg("sidori", random_number)

def convert_and_compare_dates(date_str):
    """转换并比较日期"""
    current_date = datetime.datetime.now()
    try:
        date_obj = datetime.datetime.strptime(str(int(int(date_str) / 4)), "%Y%m%d")
    except:
        return "已过期"
    if date_obj > current_date:
        return "未过期"
    else:
        return "已过期"

def display_random_number():
    """显示随机数"""
    global csdir
    mroot = Toplevel()
    mroot.title("ID")
    sw = mroot.winfo_screenwidth()
    sh = mroot.winfo_screenheight()
    ww = 80
    wh = 70
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    mroot.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    with open(os.path.join(csdir, 'setting.cfg'), 'r', encoding='gb18030') as f:
        setting_cfg = eval(f.read())
    random_number = int(setting_cfg["sidori"])
    sid = random_number * 2 + 183576
    label = ttk.Label(mroot, text=f"机器码: {random_number}")
    entry = ttk.Entry(mroot)
    label.pack()
    entry.pack()
    ttk.Button(mroot, text="验证", command=lambda: check_input(entry.get(), sid)).pack()

def check_input(input_numbers, sid):
    """检查输入"""
    try:
        input_number = int(str(input_numbers)[0:6])
        day_end = convert_and_compare_dates(str(input_numbers)[6:14])
    except:
        messagebox.showinfo(title="提示", message="不匹配，注册失败。")
        return 0
    if input_number == sid and day_end == "未过期":
        update_setting_cfg("sidfinal", input_numbers)
        messagebox.showinfo(title="提示", message="注册成功,请重新启动程序。")
        quit()
    else:
        messagebox.showinfo(title="提示", message="不匹配，注册失败。")


def load_app(root, package_name):
    """加载应用程序"""
    global csdir
    # 使用 os.path.join 确保路径兼容 Windows/Linux
    package_path = os.path.join(csdir, f"{package_name}.py")
    return_pkg = os.path.join(csdir, 'easypv.py')
    
    # 关闭当前窗口
    root.destroy()
    
    # 执行脚本（兼容 Windows 和 Linux）
    if platform.system() == "Windows":
        # Windows 需要用引号包裹路径，防止空格问题
        os.system(f'python {package_path}')
        os.system(f'python {return_pkg}')		    
    else:
        # Linux/macOS 直接执行
        subprocess.run([python_executable, package_path])
        subprocess.run([python_executable, return_pkg])
        
def load_app2(root, package_name):
    """加载应用程序"""
    global csdir
    # 使用 os.path.join 确保路径兼容 Windows/Linux
    package_path = os.path.join(csdir, f"{package_name}.py")
    return_pkg = os.path.join(csdir, 'easypv.py')
    
    # 关闭当前窗口
    root.destroy()
    
    # 执行脚本（兼容 Windows 和 Linux）
    if platform.system() == "Windows":
        # Windows 需要用引号包裹路径，防止空格问题
        os.system(f'python -m easypymanager')
        os.system(f'python {return_pkg}')		    
    else:
        # Linux/macOS 直接执行
        subprocess.run([python_executable, '-m easypymanager'])
        subprocess.run([python_executable, return_pkg])
        
def load_ui(aaaa):
    root = Tk()
    root.title("药物警戒数据分析工作平台 EasyPV" + " " + version_now)
    sw_root = root.winfo_screenwidth()
    sh_root = root.winfo_screenheight()
    ww_root = 700
    wh_root = 620
    x_root = (sw_root - ww_root) / 2
    y_root = (sh_root - wh_root) / 2
    root.geometry("%dx%d+%d+%d" % (ww_root, wh_root, x_root, y_root))
    root.configure(bg="steelblue")

    try:
        frame0 = ttk.Frame(root, width=90, height=20)
        frame0.pack(side=LEFT)

        B_open_files1 = Button(
            frame0,
            text="基础统计分析\n（适用于药械妆全字段标准数据和固化统计）",
            bg="steelblue",
            fg="snow",
            height=2,
            width=30,
            font=("微软雅黑", 12),
            relief=GROOVE,
            activebackground="lightsteelblue",
            command=lambda: load_app(root,'adrmdr'),
        )
        if pandas_ver==1:
            B_open_files1.pack()

        B_open_files2 = Button(
            frame0,
            text="进阶统计分析\n（适用于所有表格数据和自定义分析）",
            bg="steelblue",
            fg="snow",
            height=2,
            width=30,
            font=("微软雅黑", 12),
            relief=GROOVE,
            activebackground="lightsteelblue",
            command=lambda: load_app(root,'easystat'),
        )
        B_open_files2.pack()

        B_open_files3 = Button(
            frame0,
            text="报告表质量评估\n（适用于药械全字段标准数据）",
            bg="steelblue",
            fg="snow",
            height=2,
            width=30,
            font=("微软雅黑", 12),
            relief=GROOVE,
            activebackground="lightsteelblue",
            command=lambda: load_app(root,'pinggutools'),
        )
        if pandas_ver==1:
            B_open_files3.pack()


        B_open_files5 = Button(
            frame0,
            text="工具箱\n（其他定制的小工具）",
            bg="steelblue",
            fg="snow",
            height=2,
            width=30,
            font=("微软雅黑", 12),
            relief=GROOVE,
            activebackground="lightsteelblue",
            command=lambda: load_app2(root,'easypymanager'),
        )
        B_open_files5.pack()

        B_open_files6 = Button(
            frame0,
            text="手动更新资源库",
            bg="steelblue",
            fg="snow",
            height=2,
            width=30,
            font=("微软雅黑", 12),
            relief=GROOVE,
            activebackground="lightsteelblue",
            command=lambda: update_database_local(),
        )
        B_open_files6.pack()


        B_open_files6 = Button(
            frame0,
            text="意见反馈",
            bg="steelblue",
            fg="snow",
            height=2,
            width=30,
            font=("微软雅黑", 12),
            relief=GROOVE,
            activebackground="lightsteelblue",
            command=lambda: messagebox.showinfo(title="联系我们", message="如有任何问题或建议，请联系蔡老师，411703730（微信或QQ）。"),
        )
        B_open_files6.pack()

    except Exception as e:
        print(f"Error: {e}")

    text = ScrolledText(root, height=400, width=400, bg="#FFFFFF")
    text.pack(padx=5, pady=5)
    text.insert(
        END, "\n\n\n\n\n\n\n\n\n\n\n本工作站适用于整理和分析国家医疗器械不良事件信息系统、国家药品不良反应监测系统和国家化妆品不良反应监测系统中导出的监测数据。\n\n"
    )
    text.insert(END, "\n\n")
    text.insert(END,'当前用户：'+str(aaaa['username'])+'\n\n')

    setting_cfg = read_setting_cfg()
    generate_random_file()
    setting_cfg = open_setting_cfg()
    if setting_cfg["settingdir"] == 0:
        messagebox.showinfo(title="提示", message="未发现默认配置文件夹，请选择一个。如该配置文件夹中并无配置文件，将生成默认配置文件。")
        filepathu = filedialog.askdirectory()
        filepathu = os.path.normpath(filepathu)
        #path = get_directory_path(filepathu)
        #update_setting_cfg("settingdir", path)
    setting_cfg = open_setting_cfg()
    random_number = int(setting_cfg["sidori"])
    input_number = int(str(setting_cfg["sidfinal"])[0:6])
    day_end = convert_and_compare_dates(str(setting_cfg["sidfinal"])[6:14])
    sid = random_number * 2 + 183576
    #if input_number == sid and day_end == "未过期":
    #    usergroup = "用户组=1"
    #    text.insert(END, usergroup + "   有效期至：")
    #    text.insert(END, datetime.datetime.strptime(str(int(int(str(setting_cfg["sidfinal"])[6:14]) / 4)), "%Y%m%d"))
    #else:
    #    text.insert(END, usergroup)
    text.insert(END, "\n配置文件路径：" + setting_cfg["settingdir"] + "\n")
    peizhidir = str(setting_cfg["settingdir"])
    peizhidir = os.path.join(peizhidir, 'fspsssdfpy')
    peizhidir = peizhidir.replace("fspsssdfpy", '')
    print('peizhidir:', peizhidir)
    try:
        update_database('epv.zip')
    except:
        print('资源库获取更新不成功。')
    root.mainloop()
    print("done.")
       
if __name__ == '__main__':
    # 检查并生成 setting.cfg 和 setting.xml 文件
    check_and_generate_files()
    run_encrypted_client_app()

