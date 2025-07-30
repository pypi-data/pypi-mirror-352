# web_config.py

import os
import sys
import json
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import get_minecraft_config

app = Flask(__name__, template_folder='templates', static_folder='static')

# Trae配置文件路径
TRAE_CONFIG_PATH = os.path.expanduser("~\\AppData\\Roaming\\Trae\\User\\mcp.json")

def get_trae_config():
    """获取Trae的MCP配置"""
    if os.path.exists(TRAE_CONFIG_PATH):
        try:
            with open(TRAE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取Trae配置失败: {e}")
    
    # 如果文件不存在或读取失败，返回默认配置
    server_path = get_mcp_server_path()
    
    if server_path.endswith('.exe'):
        return {
            "mcpServers": {
                "minecraft": {
                    "command": server_path,
                    "args": [],
                    "env": {
                        "MC_HOST": "localhost",
                        "MC_RCON_PORT": "25575",
                        "MC_RCON_PASSWORD": ""
                    }
                }
            }
        }
    else:
        # Python脚本模式
        return {
            "mcpServers": {
                "minecraft": {
                    "command": sys.executable,
                    "args": [server_path],
                    "env": {
                        "MC_HOST": "localhost",
                        "MC_RCON_PORT": "25575",
                        "MC_RCON_PASSWORD": ""
                    }
                }
            }
        }

def get_mcp_server_path():
    """获取MCP服务器的绝对路径"""
    # 检测是否运行在PyInstaller打包环境中
    if getattr(sys, 'frozen', False):
        # 运行在PyInstaller打包的EXE中，获取实际的EXE文件路径
        current_app_path = sys.executable
    else:
        # 运行在Python解释器中
        current_app_path = os.path.abspath(__file__)
    
    current_dir = os.path.dirname(current_app_path)
    
    # 判断当前运行的是否是web_config应用
    is_web_config = os.path.basename(current_app_path).lower().startswith('minecraft_web')
    
    # 如果当前运行的是web配置应用，查找同目录下的MCP服务器
    server_exe_name = 'minecraft_mcp_server.exe'
    server_paths = [
        os.path.join(os.path.dirname(current_dir), 'release', server_exe_name),
        os.path.join(current_dir, server_exe_name),
        os.path.join(os.path.dirname(current_dir), server_exe_name)
    ]
    
    for server_path in server_paths:
        if os.path.exists(server_path):
            return server_path
    
    # 如果没有找到EXE文件，返回Python脚本路径
    if getattr(sys, 'frozen', False):
        # 在打包环境中，如果找不到EXE，返回当前目录下的main.py
        return os.path.join(current_dir, 'main.py')
    else:
        # 在开发环境中，返回项目根目录下的main.py
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')

def save_to_trae_config(config):
    """保存配置到Trae的MCP配置文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(TRAE_CONFIG_PATH), exist_ok=True)
        
        # 读取现有配置或创建新配置
        trae_config = get_trae_config()
        
        # 获取MCP服务器路径
        server_path = get_mcp_server_path()
        
        # 更新MCP服务器配置
        if "mcpServers" not in trae_config:
            trae_config["mcpServers"] = {}
        
        if "minecraft" not in trae_config["mcpServers"]:
            trae_config["mcpServers"]["minecraft"] = {}
        
        # 判断是EXE文件还是Python脚本
        if server_path.endswith('.exe'):
            trae_config["mcpServers"]["minecraft"]["command"] = server_path
            trae_config["mcpServers"]["minecraft"]["args"] = []
        else:
            # Python脚本模式
            trae_config["mcpServers"]["minecraft"]["command"] = sys.executable
            trae_config["mcpServers"]["minecraft"]["args"] = [server_path]
        
        # 更新环境变量配置
        trae_config["mcpServers"]["minecraft"]["env"] = {
            "MC_HOST": config.get("MC_HOST", "localhost"),
            "MC_RCON_PORT": config.get("MC_RCON_PORT", "25575"),
            "MC_RCON_PASSWORD": config.get("MC_RCON_PASSWORD", "")
        }
        
        # 保存配置
        with open(TRAE_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(trae_config, f, indent=4)
        
        return True, f"配置已同步到Trae"
    except Exception as e:
        return False, f"同步到Trae失败: {e}"

@app.route('/')
def index():
    """主页 - 环境变量配置界面"""
    current_config = {
        'MC_HOST': os.getenv('MC_HOST', 'localhost'),
        'MC_RCON_PORT': os.getenv('MC_RCON_PORT', '25575'),
        'MC_RCON_PASSWORD': os.getenv('MC_RCON_PASSWORD', '')
    }
    
    # 尝试从Trae配置中读取
    trae_config = get_trae_config()
    if "mcpServers" in trae_config and "minecraft" in trae_config["mcpServers"] and "env" in trae_config["mcpServers"]["minecraft"]:
        env_config = trae_config["mcpServers"]["minecraft"]["env"]
        current_config = {
            'MC_HOST': env_config.get('MC_HOST', current_config['MC_HOST']),
            'MC_RCON_PORT': env_config.get('MC_RCON_PORT', current_config['MC_RCON_PORT']),
            'MC_RCON_PASSWORD': env_config.get('MC_RCON_PASSWORD', current_config['MC_RCON_PASSWORD'])
        }
    
    return render_template('config.html', config=current_config)

@app.route('/api/server-path', methods=['GET'])
def get_server_path():
    """获取当前检测到的服务器路径"""
    try:
        server_path = get_mcp_server_path()
        return jsonify({
            'success': True,
            'server_path': server_path,
            'is_exe': server_path.endswith('.exe')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        # 尝试从Trae配置中读取
        trae_config = get_trae_config()
        if "mcpServers" in trae_config and "minecraft" in trae_config["mcpServers"] and "env" in trae_config["mcpServers"]["minecraft"]:
            env_config = trae_config["mcpServers"]["minecraft"]["env"]
            config = {
                'MC_HOST': env_config.get('MC_HOST', 'localhost'),
                'MC_RCON_PORT': env_config.get('MC_RCON_PORT', '25575'),
                'MC_RCON_PASSWORD': env_config.get('MC_RCON_PASSWORD', '')
            }
        else:
            config = {
                'MC_HOST': os.getenv('MC_HOST', 'localhost'),
                'MC_RCON_PORT': os.getenv('MC_RCON_PORT', '25575'),
                'MC_RCON_PASSWORD': os.getenv('MC_RCON_PASSWORD', '')
            }
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新环境变量配置"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('MC_RCON_PASSWORD'):
            return jsonify({'success': False, 'error': 'RCON密码不能为空'})
        
        # 验证端口号
        try:
            port = int(data.get('MC_RCON_PORT', '25575'))
            if port < 1 or port > 65535:
                raise ValueError()
        except ValueError:
            return jsonify({'success': False, 'error': '端口号必须是1-65535之间的数字'})
        
        # 更新环境变量
        os.environ['MC_HOST'] = data.get('MC_HOST', 'localhost')
        os.environ['MC_RCON_PORT'] = str(port)
        os.environ['MC_RCON_PASSWORD'] = data.get('MC_RCON_PASSWORD')
        
        # 同步到Trae配置
        success, message = save_to_trae_config({
            'MC_HOST': data.get('MC_HOST', 'localhost'),
            'MC_RCON_PORT': str(port),
            'MC_RCON_PASSWORD': data.get('MC_RCON_PASSWORD')
        })
        
        # 测试连接
        try:
            test_config = get_minecraft_config()
            return jsonify({
                'success': True, 
                'message': f'配置已保存并验证成功。{message}',
                'config': {
                    'MC_HOST': test_config['host'],
                    'MC_RCON_PORT': str(test_config['port']),
                    'MC_RCON_PASSWORD': '***'
                }
            })
        except Exception as e:
            return jsonify({
                'success': False, 
                'error': f'配置验证失败: {str(e)}'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """测试Minecraft服务器连接"""
    try:
        from mcrcon import MCRcon
        config = get_minecraft_config()
        
        with MCRcon(config['host'], config['password'], port=config['port']) as mcr:
            response = mcr.command('list')
            return jsonify({
                'success': True, 
                'message': '连接成功',
                'server_response': response
            })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'连接失败: {str(e)},请检查Rcon信息是否正确'
        })

@app.route('/api/trae-config', methods=['GET'])
def get_trae_config_api():
    """获取Trae配置信息"""
    try:
        config = get_trae_config()
        return jsonify({
            'success': True,
            'config': config,
            'config_path': TRAE_CONFIG_PATH
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    import sys
    app.run(debug=True, host='0.0.0.0', port=5000)