# config.py

import os

def get_minecraft_config():
    config = {
        "host": os.getenv("MC_HOST", "localhost"),
        "port": int(os.getenv("MC_RCON_PORT", "25575")),
        "password": os.getenv("MC_RCON_PASSWORD")
    }

    if not config["password"]:
        raise ValueError("MC_RCON_PASSWORD 环境变量必须设置")

    return config