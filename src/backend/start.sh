#!/bin/bash
# 启动 Flask 后端服务

cd "$(dirname "$0")"
source ../../venv/bin/activate
python app.py
