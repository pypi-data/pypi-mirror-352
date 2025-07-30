#!/usr/bin/env python3
"""
EchoMind - 播客转录与摘要工具 / Podcast Transcription and Summary Tool
支持 Apple Podcast 和 YouTube 平台，提供中英文双语界面
Supports Apple Podcast and YouTube platforms with bilingual Chinese/English interface
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 从requirements.txt读取所有依赖
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="echomind",
    version="1.0.0",
    author="EchoMind Team",
    author_email="contact@echomind.app",
    description="智能播客转录与摘要工具，支持 Apple Podcast 和 YouTube / Intelligent podcast transcription and summary tool for Apple Podcast and YouTube",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/henryzha/echomind",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: Chinese (Simplified)",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            # 双语命令入口点 / Bilingual command entry points
            "echomind-zh=echomind.cli_ch:main",     # 中文版 / Chinese version
            "echomind-en=echomind.cli_en:main",     # 英文版 / English version
            "echomind-ch=echomind.cli_ch:main",     # 中文版别名 / Chinese alias
            
            # 默认命令（英文版）/ Default command (English version)
            "echomind=echomind.cli_en:main",
        ],
    },
    keywords=[
        "podcast", "transcription", "summary", "youtube", "apple podcast", 
        "whisper", "ai", "bilingual", "chinese", "english", "播客", "转录", "摘要",
        "gemini", "groq", "mlx", "audio processing", "text generation"
    ],
    project_urls={
        "Bug Reports": "https://github.com/henryzha/echomind/issues",
        "Source": "https://github.com/henryzha/echomind",
        "Documentation": "https://github.com/henryzha/echomind#readme",
        "Homepage": "https://github.com/henryzha/echomind",
    },
    include_package_data=True,
    zip_safe=False,
) 