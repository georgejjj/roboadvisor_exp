#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
字体下载脚本 - 用于自动下载并安装中文字体到项目中
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path

# 思源黑体下载地址 (GitHub)
FONT_URL = "https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansCN.zip"

# 备用字体下载地址 (直接下载单个OTF文件)
BACKUP_FONT_URL = "https://github.com/Pal3love/Source-Han-TrueType/raw/master/SourceHanSansCN/TTF/SourceHanSansCN-Normal.ttf"

def download_direct_font():
    """
    直接下载单个字体文件 (更可靠的方法)
    """
    font_dir = Path("fonts")
    font_dir.mkdir(exist_ok=True)
    
    font_path = font_dir / "SourceHanSansCN-Normal.ttf"
    
    print(f"正在直接下载思源黑体单个文件...")
    try:
        response = requests.get(BACKUP_FONT_URL, stream=True)
        response.raise_for_status()
        
        with open(font_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"字体文件已保存到: {font_path}")
        return True
    except Exception as e:
        print(f"下载字体时出错: {e}")
        return False

def download_font():
    """
    下载思源黑体字体并安装到项目的fonts目录中
    """
    # 创建字体目录
    font_dir = Path("fonts")
    font_dir.mkdir(exist_ok=True)
    
    # 下载字体
    print(f"正在下载思源黑体字体ZIP包...")
    zip_path = Path("temp_fonts.zip")
    
    try:
        response = requests.get(FONT_URL, stream=True)
        response.raise_for_status()  # 确保请求成功
        
        # 保存ZIP文件
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # 解压缩字体文件
        print("正在解压字体文件...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 创建临时目录
            temp_dir = Path("temp_extract")
            temp_dir.mkdir(exist_ok=True)
            
            # 解压到临时目录
            zip_ref.extractall(temp_dir)
            
            # 查找OTF文件并复制到fonts目录
            otf_files = list(temp_dir.glob("**/SourceHanSansCN-Normal.otf"))
            if not otf_files:
                print("错误: 无法在ZIP文件中找到SourceHanSansCN-Normal.otf")
                return False
            
            # 复制找到的第一个文件
            shutil.copy2(otf_files[0], font_dir / "SourceHanSansCN-Normal.otf")
            print(f"字体文件已复制到 {font_dir}/SourceHanSansCN-Normal.otf")
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
        
        # 删除zip文件
        zip_path.unlink()
        
        print("字体安装完成!")
        return True
    
    except Exception as e:
        print(f"下载或安装字体时出错: {e}")
        
        # 清理临时文件
        if zip_path.exists():
            zip_path.unlink()
        
        return False

def download_font_manually():
    """
    提供手动下载字体的说明
    """
    print("\n如果自动下载失败，请按照以下步骤手动下载并安装字体:")
    print("1. 访问 https://github.com/adobe-fonts/source-han-sans/tree/release")
    print("2. 下载最新版本的思源黑体字体(SourceHanSansCN)")
    print("3. 解压文件，找到 SourceHanSansCN-Normal.otf 字体文件")
    print("4. 在项目根目录创建 'fonts' 文件夹(如果不存在)")
    print("5. 将字体文件复制到 'fonts' 文件夹中")
    print("完成上述步骤后，Streamlit应用将能正确显示中文字体。")

def create_dummy_font():
    """
    创建一个简单的字体文件，确保字体目录存在
    用于Streamlit Share等环境，防止找不到字体文件
    """
    font_dir = Path("fonts")
    font_dir.mkdir(exist_ok=True)
    
    # 确保字体目录被添加到Git仓库
    with open(font_dir / ".gitkeep", "w") as f:
        f.write("# This directory contains font files for Chinese text display\n")
    
    print("已创建字体占位符文件，确保fonts目录存在")
    return True

if __name__ == "__main__":
    print("=== 思源黑体字体下载工具 ===")
    
    # 先尝试直接下载单个字体文件 (最可靠的方法)
    if download_direct_font():
        print("已成功下载单个字体文件，您的项目已准备好显示中文字体!")
    # 如果失败，尝试ZIP包下载方式
    elif download_font():
        print("已成功下载并解压字体文件，您的项目已准备好显示中文字体!") 
    else:
        # 确保至少创建了fonts目录
        create_dummy_font()
        download_font_manually() 