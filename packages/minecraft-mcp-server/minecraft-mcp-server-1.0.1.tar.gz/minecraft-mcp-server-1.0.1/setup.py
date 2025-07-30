#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README_PYPI.md作为长描述
with open("README_PYPI.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt作为依赖列表
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="minecraft-mcp-server",
    version="1.0.1",
    author="haishen668",
    author_email="2821396723@qq.com", 
    description="Minecraft MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haishen668/minecraft_mcp_server",  
    packages=find_packages(include=['tools']),  # 移除对不存在的resources目录的引用
    include_package_data=True,
    package_data={
        "": ["templates/*", "static/*", "icon.ico"],
    },
    py_modules=["main", "web_config", "start_web_config", "config"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "minecraft-mcp-server=main:run_main",
            "minecraft-web-config=start_web_config:main",
        ],
    },
)