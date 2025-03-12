#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
字体下载脚本 - 用于自动下载并安装思源黑体字体到项目中
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path

# 思源黑体下载地址 (GitHub)
FONT_URL = "https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSansCN.zip"

def download_font():
    """
    下载思源黑体字体并安装到项目的fonts目录中
    """
    # 创建字体目录
    font_dir = Path("fonts")
    font_dir.mkdir(exist_ok=True)
    
    # 下载字体
    print(f"正在下载思源黑体字体...")
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

if __name__ == "__main__":
    print("=== 思源黑体字体下载工具 ===")
    if not download_font():
        download_font_manually()
    else:
        print("现在您的项目已经准备好在Streamlit Share上显示中文字体!") 