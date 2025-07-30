#!/usr/bin/env python3
# start_web_config.py

import os
import sys
import webbrowser
import time
from threading import Timer
from web_config import app

def open_browser():
    """延迟打开浏览器"""
    webbrowser.open('http://localhost:5000')

def main():
    print("="*60)
    print("🎮 Minecraft MCP 服务器配置工具")
    print("="*60)
    print("")
    print("🚀 正在启动Web配置界面...")
    print("📍 访问地址: http://localhost:5000")
    print("")
    print("💡 提示:")
    print("   - 在浏览器中配置您的Minecraft服务器连接参数")
    print("   - 配置完成后，环境变量将自动保存")
    print("   - 按 Ctrl+C 停止服务")
    print("")
    print("="*60)
    
    # 延迟3秒后自动打开浏览器
    timer = Timer(3.0, open_browser)
    timer.start()
    
    try:
        # 启动Flask应用
        app.run(
            debug=False,
            host='0.0.0.0',
            port=5000,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n👋 感谢使用 Minecraft MCP 配置工具！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n🔧 请检查:")
        print("   1. 端口5000是否被占用")
        print("   2. 是否安装了所需依赖 (pip install -r requirements.txt)")
        sys.exit(1)

if __name__ == '__main__':
    main()