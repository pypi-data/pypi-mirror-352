import os
import time
import threading
import argparse
import json
import base64
import asyncio
from flask import Flask, session, request, jsonify, send_file, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import ImageGrab
import cv2
import numpy as np
from datetime import datetime
from io import BytesIO
import websockets

# 切换到当前文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.urandom(24)

# 全局变量
TEACHER_PASSWORD = "123456"  # 默认密码，可以通过命令行参数修改
client_images = {}         # {client_id: [(timestamp, image_bytes), ...]}
client_last_active = {}    # {client_id: last_active_time}
upload_history = {}        # {ip: [(timestamp, filename), ...]}
is_broadcasting = False    # 是否正在广播
current_broadcast_folder = None  # 当前广播保存的文件夹
use_camera = False
active_websockets = set()  # 活跃的WebSocket连接
ws_server = None  # WebSocket服务器实例
connected_clients = set()
broadcast_task = None
broadcast_history = []       # [(timestamp, image_data), ...]
MAX_HISTORY_SIZE = 1000     # 最大历史记录数量
broadcast_packages = {}      # {package_id: {'name': name, 'timestamp': timestamp, 'frames': frames}}

# 文件存储路径（使用相对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "saved_images")
FILES_DIR = os.path.join(BASE_DIR, "shared_files")
ASSIGNMENTS_DIR = os.path.join(BASE_DIR, "assignments")
TRANSFER_FOLDER = os.path.join(BASE_DIR, "transfer_files")
BROADCAST_PACKAGES_DIR = os.path.join(BASE_DIR, "broadcast_packages")

# 创建必要的目录
for directory in [SAVE_DIR, FILES_DIR, ASSIGNMENTS_DIR, TRANSFER_FOLDER, BROADCAST_PACKAGES_DIR]:
    os.makedirs(directory, exist_ok=True)
    print(f"确保目录存在: {directory}")

# 初始化摄像头
cap = cv2.VideoCapture(0)
has_camera = cap.isOpened()
if not has_camera:
    print("警告：未检测到摄像头")
    cap.release()

def capture_screen():
    """捕获屏幕画面"""
    screenshot = ImageGrab.grab()
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return frame

def capture_camera():
    """捕获摄像头画面"""
    if not has_camera:
        print("摄像头不可用")
        return None
    ret, frame = cap.read()
    if not ret:
        print("摄像头读取失败")
        return None
    return frame

def is_teacher():
    """检查当前用户是否为教师"""
    return session.get('is_teacher', False)

def check_upload_limit(ip):
    """检查上传频率限制"""
    now = time.time()
    if ip not in upload_history:
        upload_history[ip] = []
    
    # 清理30秒前的记录
    upload_history[ip] = [(t, f) for t, f in upload_history[ip] if now - t < 30]
    
    # 检查30秒内是否超过5次上传
    if len(upload_history[ip]) >= 5:
        return False
    return True

def add_upload_record(ip, filename):
    """添加上传记录"""
    if ip not in upload_history:
        upload_history[ip] = []
    upload_history[ip].append((time.time(), filename))

def get_folder_size(folder):
    """获取文件夹大小"""
    total = 0
    for root, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            total += os.path.getsize(fp)
    return total

def cleanup_folder(folder, max_size=500*1024*1024):
    """清理文件夹，保持大小在限制内"""
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.jpg')]
    files = [(f, os.path.getmtime(f)) for f in files]
    files.sort(key=lambda x: x[1])  # 按修改时间升序
    while get_folder_size(folder) > max_size and files:
        os.remove(files[0][0])
        files.pop(0)

def cleanup_inactive_clients():
    """清理不活跃的客户端"""
    while True:
        now = time.time()
        for client_id in list(client_last_active):
            if now - client_last_active[client_id] > 3600:
                client_images.pop(client_id, None)
                client_last_active.pop(client_id, None)
        time.sleep(600)

def get_folder_by_type(file_type):
    """根据文件类型获取对应的文件夹路径"""
    if file_type == 'transfer':
        return TRANSFER_FOLDER
    elif file_type == 'assignment':
        return ASSIGNMENTS_DIR
    else:
        return FILES_DIR

# Flask路由
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/assignments')
def assignments():
    if not session.get('is_teacher'):
        return redirect(url_for('index'))
    return render_template('assignments.html')

@app.route('/login', methods=['POST'])
def login():
    """教师登录"""
    password = request.form.get('password')
    if password == TEACHER_PASSWORD:
        session['is_teacher'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '密码错误'})

@app.route('/logout')
def logout():
    """教师登出"""
    session.pop('is_teacher', None)
    return redirect(url_for('index'))

@app.route('/api/files')
def list_files():
    """获取文件列表"""
    files = []
    for filename in os.listdir(FILES_DIR):
        path = os.path.join(FILES_DIR, filename)
        files.append({
            'name': filename,
            'size': os.path.getsize(path),
            'upload_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(path)))
        })
    return jsonify(files)

@app.route('/api/transfer_files')
def list_transfer_files():
    files = []
    for filename in os.listdir(TRANSFER_FOLDER):
        filepath = os.path.join(TRANSFER_FOLDER, filename)
        if os.path.isfile(filepath):
            files.append({
                'name': filename,
                'size': os.path.getsize(filepath),
                'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(files)

@app.route('/api/assignments')
def list_assignments():
    if not session.get('is_teacher'):
        return jsonify({'error': '未授权'}), 403
    
    assignments = []
    for filename in os.listdir(ASSIGNMENTS_DIR):
        filepath = os.path.join(ASSIGNMENTS_DIR, filename)
        if os.path.isfile(filepath):
            assignments.append({
                'name': filename,
                'size': os.path.getsize(filepath),
                'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(assignments)

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'})
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 1024 * 1024 * 1024:  # 1GB
        return jsonify({'error': '文件大小超过1GB限制'}), 400
    
    filename = secure_filename(file.filename)
    file_type = request.form.get('type', 'shared')
    
    if file_type == 'transfer':
        save_path = os.path.join(TRANSFER_FOLDER, filename)
    elif file_type == 'assignment':
        save_path = os.path.join(ASSIGNMENTS_DIR, filename)
    else:
        save_path = os.path.join(FILES_DIR, filename)
    
    file.save(save_path)
    return jsonify({'success': True})

@app.route('/delete_file/<path:filename>')
def delete_file(filename):
    try:
        file_type = request.args.get('type', 'shared')
        if file_type == 'shared' and not session.get('is_teacher'):
            return jsonify({'error': '无权限删除共享文件'}), 403
            
        folder = get_folder_by_type(file_type)
        file_path = os.path.join(folder, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': '文件删除成功'})
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        print(f"删除文件时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_file/<path:filename>')
def download_file(filename):
    try:
        file_type = request.args.get('type', 'shared')
        if file_type == 'shared' and not session.get('is_teacher'):
            return jsonify({'error': '无权限下载共享文件'}), 403
            
        folder = get_folder_by_type(file_type)
        file_path = os.path.join(folder, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        print(f"下载文件时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/broadcast_packages')
def list_broadcast_packages():
    """获取广播数据包列表"""
    packages = []
    for filename in os.listdir(BROADCAST_PACKAGES_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(BROADCAST_PACKAGES_DIR, filename), 'r', encoding='utf-8') as f:
                    package_info = json.load(f)
                    packages.append({
                        'id': package_info['id'],
                        'name': package_info['name'],
                        'timestamp': package_info['timestamp'],
                        'frame_count': len(package_info['frames'])
                    })
            except Exception as e:
                print(f"读取广播数据包失败: {e}")
    
    # 按时间戳降序排序
    packages.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(packages)

@app.route('/api/broadcast_package/<package_id>')
def get_broadcast_package(package_id):
    """获取指定广播数据包的内容"""
    try:
        package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
        if os.path.exists(package_file):
            with open(package_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        return jsonify({'error': '数据包不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_broadcast_package/<package_id>')
def delete_broadcast_package(package_id):
    """删除广播数据包"""
    if not session.get('is_teacher'):
        return jsonify({'error': '无权限删除广播数据包'}), 403
        
    try:
        package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
        if os.path.exists(package_file):
            os.remove(package_file)
            if package_id in broadcast_packages:
                del broadcast_packages[package_id]
            return jsonify({'success': True})
        return jsonify({'error': '数据包不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket处理
class WebSocketHandler:
    def __init__(self):
        self.clients = set()
        self.broadcast_task = None
        self.current_package_id = None
        self.has_camera = has_camera
        self.teacher_clients = set()  # 存储教师客户端的WebSocket连接
        print("WebSocket处理器已初始化")
        # 加载所有广播数据包
        self.load_all_packages()

    def load_all_packages(self):
        """加载所有广播数据包"""
        print("开始加载所有广播数据包")
        broadcast_packages.clear()  # 清空现有包
        
        for filename in os.listdir(BROADCAST_PACKAGES_DIR):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(BROADCAST_PACKAGES_DIR, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        package_info = json.load(f)
                        broadcast_packages[package_info['id']] = package_info
                        print(f"已加载广播包: {package_info['name']}")
                except Exception as e:
                    print(f"加载广播数据包失败 {filename}: {e}")
        
        print(f"广播包加载完成，共 {len(broadcast_packages)} 个包")

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"新客户端连接，当前连接数: {len(self.clients)}")
        try:
            # 发送当前广播状态和摄像头状态
            await websocket.send(json.dumps({
                'type': 'broadcast_status',
                'status': 'started' if is_broadcasting else 'stopped',
                'has_camera': self.has_camera
            }))
            
            # 发送所有广播数据包列表
            await websocket.send(json.dumps({
                'type': 'packages_list',
                'packages': list(broadcast_packages.values())
            }))
            
            # 发送当前广播的历史记录
            if broadcast_history:
                await websocket.send(json.dumps({
                    'type': 'history',
                    'history': broadcast_history
                }))
                print("已发送历史记录")
        except Exception as e:
            print(f"发送状态和历史记录失败: {e}")

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"客户端断开连接，当前连接数: {len(self.clients)}")

    async def broadcast_images(self):
        global is_broadcasting, use_camera
        print("开始广播任务")
        while is_broadcasting:
            try:
                # 捕获图像
                if use_camera:
                    print("使用摄像头捕获")
                    frame = capture_camera()
                else:
                    print("使用屏幕捕获")
                    frame = capture_screen()
                
                if frame is not None:
                    # 压缩图片
                    frame = cv2.resize(frame, (1280, 720))
                    _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    img_b64 = base64.b64encode(buf).decode()
                    timestamp = int(time.time() * 1000)
                    
                    # 添加到历史记录
                    broadcast_history.append({
                        'timestamp': timestamp,
                        'image': img_b64
                    })
                    if len(broadcast_history) > MAX_HISTORY_SIZE:
                        broadcast_history.pop(0)
                    
                    # 广播给所有客户端
                    message = json.dumps({
                        'type': 'image',
                        'image': img_b64,
                        'timestamp': timestamp
                    })
                    websockets_to_remove = set()
                    for client in self.clients:
                        try:
                            await client.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            print(f"客户端连接已关闭，准备移除")
                            websockets_to_remove.add(client)
                        except Exception as e:
                            print(f"发送消息失败: {e}")
                            websockets_to_remove.add(client)
                    
                    # 移除断开的连接
                    for client in websockets_to_remove:
                        await self.unregister(client)
                else:
                    print("图像捕获失败")
                
                await asyncio.sleep(0.1)  # 10 FPS
            except Exception as e:
                print(f"广播错误: {e}")
                await asyncio.sleep(1)
        print("广播任务结束")

    async def save_broadcast_package(self):
        """保存当前广播数据包"""
        if not broadcast_history:
            print("没有广播历史记录，不保存数据包")
            return None
            
        package_id = str(int(time.time()))
        package_name = f"广播_{time.strftime('%Y%m%d_%H%M%S')}"
        
        print(f"开始保存广播数据包: {package_name}")
        print(f"历史记录长度: {len(broadcast_history)}")
        
        # 保存数据包信息
        package_info = {
            'id': package_id,
            'name': package_name,
            'timestamp': int(time.time() * 1000),
            'frames': broadcast_history.copy()
        }
        
        # 保存到文件
        package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
        try:
            with open(package_file, 'w', encoding='utf-8') as f:
                json.dump(package_info, f, ensure_ascii=False)
            print(f"广播数据包已保存: {package_file}")
            
            # 更新内存中的包列表
            broadcast_packages[package_id] = package_info
            print(f"当前广播包数量: {len(broadcast_packages)}")
            
            # 重新加载所有包
            self.load_all_packages()
            print("已重新加载所有广播包")
            
            return package_id
        except Exception as e:
            print(f"保存广播数据包失败: {e}")
            return None

    async def handle_client(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"收到消息: {data['type']}")
                    
                    # 处理教师登录
                    if data['type'] == 'teacher_login':
                        if data['password'] == TEACHER_PASSWORD:
                            self.teacher_clients.add(websocket)
                            await websocket.send(json.dumps({
                                'type': 'login_result',
                                'success': True
                            }))
                        else:
                            await websocket.send(json.dumps({
                                'type': 'login_result',
                                'success': False,
                                'message': '密码错误'
                            }))
                    
                    # 处理教师登出
                    elif data['type'] == 'teacher_logout':
                        self.teacher_clients.discard(websocket)
                        await websocket.send(json.dumps({
                            'type': 'logout_result',
                            'success': True
                        }))
                    
                    # 处理广播相关操作
                    elif data['type'] == 'start_broadcast':
                        if websocket in self.teacher_clients:
                            global is_broadcasting, broadcast_history
                            if not is_broadcasting:
                                is_broadcasting = True
                                broadcast_history = []
                                print("开始广播，清空历史记录")
                                if self.broadcast_task is None:
                                    self.broadcast_task = asyncio.create_task(self.broadcast_images())
                                await self.broadcast_status_change('started')
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限开始广播'
                            }))
                    
                    elif data['type'] == 'stop_broadcast':
                        if websocket in self.teacher_clients:
                            if is_broadcasting:
                                is_broadcasting = False
                                print("停止广播")
                                if self.broadcast_task:
                                    self.broadcast_task.cancel()
                                    self.broadcast_task = None
                                package_id = await self.save_broadcast_package()
                                if package_id:
                                    await self.broadcast_package_saved(package_id)
                                await self.broadcast_status_change('stopped')
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限停止广播'
                            }))
                    
                    elif data['type'] == 'switch_source':
                        if websocket in self.teacher_clients:
                            global use_camera
                            if data['use_camera'] and not self.has_camera:
                                await websocket.send(json.dumps({
                                    'type': 'error',
                                    'message': '摄像头不可用'
                                }))
                                continue
                            use_camera = data['use_camera']
                            print(f"切换视频源: {'摄像头' if use_camera else '屏幕'}")
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限切换视频源'
                            }))
                    
                    elif data['type'] == 'rename_package':
                        if websocket in self.teacher_clients:
                            package_id = data['package_id']
                            new_name = data['new_name']
                            if package_id in broadcast_packages:
                                broadcast_packages[package_id]['name'] = new_name
                                package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
                                with open(package_file, 'w', encoding='utf-8') as f:
                                    json.dump(broadcast_packages[package_id], f, ensure_ascii=False)
                                await self.broadcast_package_renamed(package_id, new_name)
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限重命名广播数据包'
                            }))
                    
                    elif data['type'] == 'delete_package':
                        if websocket in self.teacher_clients:
                            package_id = data['package_id']
                            package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
                            if os.path.exists(package_file):
                                os.remove(package_file)
                                if package_id in broadcast_packages:
                                    del broadcast_packages[package_id]
                                await self.broadcast_package_deleted(package_id)
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限删除广播数据包'
                            }))
                    
                except json.JSONDecodeError:
                    print("无效的JSON消息")
                except Exception as e:
                    print(f"处理消息错误: {e}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
        finally:
            self.teacher_clients.discard(websocket)  # 确保在断开连接时移除教师权限
            await self.unregister(websocket)

    async def broadcast_package_saved(self, package_id):
        """通知所有客户端广播数据包已保存"""
        message = json.dumps({
            'type': 'package_saved',
            'package_id': package_id,
            'package_info': broadcast_packages[package_id]
        })
        await self.broadcast_to_all(message)

    async def broadcast_package_renamed(self, package_id, new_name):
        """通知所有客户端广播数据包已重命名"""
        message = json.dumps({
            'type': 'package_renamed',
            'package_id': package_id,
            'new_name': new_name
        })
        await self.broadcast_to_all(message)

    async def broadcast_package_deleted(self, package_id):
        """通知所有客户端广播数据包已删除"""
        message = json.dumps({
            'type': 'package_deleted',
            'package_id': package_id
        })
        await self.broadcast_to_all(message)

    async def broadcast_to_all(self, message):
        """向所有客户端广播消息"""
        websockets_to_remove = set()
        for client in self.clients:
            try:
                await client.send(message)
            except Exception as e:
                print(f"发送消息失败: {e}")
                websockets_to_remove.add(client)
        
        # 移除断开的连接
        for client in websockets_to_remove:
            await self.unregister(client)

    async def broadcast_status_change(self, status):
        """广播状态变化给所有客户端"""
        message = json.dumps({
            'type': 'broadcast_status',
            'status': status
        })
        websockets_to_remove = set()
        for client in self.clients:
            try:
                await client.send(message)
            except Exception as e:
                print(f"发送状态变化失败: {e}")
                websockets_to_remove.add(client)
        
        # 移除断开的连接
        for client in websockets_to_remove:
            await self.unregister(client)

# 创建WebSocket处理器实例
handler = WebSocketHandler()

async def websocket_handler(websocket, path):
    await handler.handle_client(websocket, path)

async def broadcast_thread():
    """广播线程"""
    while True:
        if is_broadcasting and active_websockets:
            # 根据模式选择捕获方式
            if use_camera:
                frame = capture_camera()
            else:
                frame = capture_screen()
            
            if frame is not None:
                # 压缩图片
                frame = cv2.resize(frame, (1280, 720))
                _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                img_b64 = base64.b64encode(buf).decode()
                
                # 保存到本地
                if current_broadcast_folder:
                    filename = f"{SAVE_DIR}/{current_broadcast_folder}/{int(time.time())}.jpg"
                    with open(filename, "wb") as f:
                        f.write(buf)
                
                # 广播给所有客户端
                message = {
                    'type': 'image',
                    'image': img_b64
                }
                for ws in active_websockets.copy():
                    try:
                        await ws.send_message(message)
                    except:
                        active_websockets.discard(ws)
        
        await asyncio.sleep(1)  # 控制发送频率

async def start_websocket_server(host, port):
    """启动WebSocket服务器"""
    print(f"启动WebSocket服务器: ws://{host}:{port}")
    server = await websockets.serve(handler.handle_client, host, port)
    await server.wait_closed()

def run_flask_server(host, port):
    """运行Flask服务器"""
    app.run(host=host, port=port)

def run_server(host='0.0.0.0', port=5000, password=None):
    """运行服务器"""
    global TEACHER_PASSWORD
    if password:
        TEACHER_PASSWORD = password
    
    # 启动WebSocket服务器
    ws_port = port + 1
    print(f"WebSocket服务器端口: {ws_port}")
    
    # 创建事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 在新线程中运行WebSocket服务器
    ws_thread = threading.Thread(target=lambda: loop.run_until_complete(start_websocket_server(host, ws_port)))
    ws_thread.daemon = True
    ws_thread.start()
    
    try:
        # 在主线程中运行Flask服务器
        run_flask_server(host, port)
    finally:
        # 清理资源
        loop.close()
        cap.release()

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='Classmate - 教室管理系统')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口')
    parser.add_argument('--password', type=str, help='教师模式密码')
    args = parser.parse_args()
    
    run_server(args.host, args.port, args.password)

if __name__ == '__main__':
    main() 