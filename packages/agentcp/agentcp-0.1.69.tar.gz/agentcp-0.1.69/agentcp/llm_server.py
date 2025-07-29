# from agentcp import AgentID
from flask import Flask
import threading
import socket
import time

from .llm_agent_utils import LLMAgent
from flask import jsonify, make_response
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)
# app.logger.disabled = True
actual_port = 0

llm_aid_app_key_map = {}
llm_app_key_aid_map = {}
is_running = False

@app.route('/<llm_aid>/chat/completions', methods=['POST'])  # 添加methods参数指定POST方法
async def llm_request(llm_aid):
    # 获取请求头并打印
    from flask import request
    headers = dict(request.headers)
    if request.is_json:
        body = request.get_json()
    else:
        body = request.form.to_dict()
    global llm_app_key_aid_map
    auth_str:str = headers.get("Authorization")
    llm_app_key = auth_str.replace("Bearer ","")
    aid = llm_app_key_aid_map.get(llm_app_key)
    if aid is None:
        return make_response(jsonify({"error": "Unauthorized"}), 401)
    llm_agent = LLMAgent(llm_agent=llm_aid, aid = aid)
    response = await llm_agent.chat_create(body)
    return response

def add_llm_aid(aid):
    global llm_aid_app_key_map, llm_app_key_aid_map
    import hashlib
    if aid.id in llm_aid_app_key_map:
        llm_app_key = llm_aid_app_key_map[aid.id]
    else:
        llm_app_key = str(int(time.time())+actual_port)
        llm_app_key = hashlib.sha256(llm_app_key.encode()).hexdigest()
        llm_aid_app_key_map[aid.id] = llm_app_key
    llm_app_key_aid_map[llm_app_key] = aid

def get_base_url(agentId,llm_aid):
    global aid
    aid = agentId
    global actual_port
    # 获取实际分配的端口号
    return "http://127.0.0.1:"+str(actual_port)+"/"+llm_aid

def get_llm_api_key(aid_str):
    # 获取实际分配的端口号
    global llm_aid_app_key_map
    if aid_str not in llm_aid_app_key_map:
        import secrets,hashlib
        llm_app_key = secrets.token_hex(16)
        llm_app_key = hashlib.sha256(llm_app_key.encode()).hexdigest()
        llm_aid_app_key_map[aid_str] = llm_app_key
    return llm_aid_app_key_map[aid_str]

def llm_server_is_running():
    global is_running
    return is_running

def __run_server():
    # 端口设为0让系统自动分配
    try:
        global actual_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        actual_port = sock.getsockname()[1]
        sock.close()
        app.run(host='127.0.0.1', port=actual_port, debug=False)
        global is_running
        #print("大模型代理服务已启动，端口号为：", actual_port,"，请不要关闭此窗口")
        is_running = True
        # llm_app_key = str(int(time.time())+actual_port)
        # import hashlib
        # llm_app_key = hashlib.sha256(llm_app_key.encode()).hexdigest()
    except Exception as e:
        is_running = False
        #print(f"Flask服务启动失败,请检查端口占用后，重启服务")

def run_server(debug:bool = False):
    # 创建并启动子线程运行Flask服务
    app.logger.disabled = (not debug)
    server_thread = threading.Thread(target=__run_server)
    server_thread.daemon = True  # 设置为守护线程，主线程退出时会自动结束
    server_thread.start()
    # 主线程可以继续执行其他任务