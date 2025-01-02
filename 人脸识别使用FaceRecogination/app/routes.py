from flask import Blueprint, render_template, Response, current_app, jsonify, request, session, redirect, url_for
from app.camera import FaceCamera
from app.models import UnknownFace
from app import db, create_app
import cv2
import numpy as np
import threading
from datetime import datetime, date, timedelta
from sqlalchemy import and_
import os
from functools import wraps
import psutil
import time
import socket
import requests

# 创建蓝图
main = Blueprint('main', __name__)

# 全局相机对象和锁
camera = None
camera_lock = threading.Lock()

# 记录系统启动时间
SYSTEM_START_TIME = time.time()

# 添加全局变量存储当前阈值
FACE_TOLERANCE = 0.4

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
@login_required
def index():
    """主页路由"""
    return render_template('index.html')

@main.route('/video_feed')
@login_required
def video_feed():
    """视频流路由"""
    global camera
    
    def generate():
        global camera
        try:
            if camera is None:
                camera = FaceCamera()
                camera.__enter__()
                
            while True:
                frame = camera.get_frame()
                if frame is None:
                    print("无法获取视频帧，结束流")
                    break
                
                ret, buffer = cv2.imencode('.jpg', frame, 
                    [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                
                if not ret:
                    print("编码视频帧失败")
                    break
                
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"视频流发生错误: {str(e)}")
            error_frame = create_error_frame("摄像头初始化失败，请刷新页面重试")
            ret, buffer = cv2.imencode('.jpg', error_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def create_error_frame(message):
    """创建一个显示错误信息的图像"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, message,
                (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (255, 255, 255), 2)
    return frame

@main.route('/history')
@login_required
def history():
    """历史记录页面路由"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)  # 每页显示12张图片
    capture_type = request.args.get('type', 'all')  # all, manual, auto
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # 构建查询
    query = UnknownFace.query

    # 根据类型筛选
    if capture_type == 'manual':
        query = query.filter(UnknownFace.duration == 0)
    elif capture_type == 'auto':
        query = query.filter(UnknownFace.duration > 0)

    # 日期筛选
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(UnknownFace.timestamp >= date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(UnknownFace.timestamp <= date_to)
        except ValueError:
            pass

    # 按时间倒序排序并分页
    pagination = query.order_by(UnknownFace.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('history.html', 
                         pagination=pagination,
                         capture_type=capture_type,
                         date_from=date_from,
                         date_to=date_to)

@main.route('/capture', methods=['POST'])
@login_required
def capture():
    """手动截图接口"""
    global camera
    
    try:
        with camera_lock:  # 使用锁来确保线程安全
            if camera is None:
                return jsonify({
                    'success': False,
                    'message': '摄像头未初始化，请先打开视频流'
                })
            
            if not camera.cap or not camera.cap.isOpened():
                return jsonify({
                    'success': False,
                    'message': '摄像头未正常打开，请刷新页面重试'
                })
            
            success, message = camera.capture_manual()
            return jsonify({
                'success': success,
                'message': message
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'截图失败: {str(e)}'
        })

@main.route('/delete_records', methods=['POST'])
@login_required
def delete_records():
    """删除记录接口"""
    try:
        data = request.get_json()
        delete_type = data.get('type')
        record_id = data.get('id')

        if delete_type == 'single' and record_id:
            # 删除单条记录
            record = UnknownFace.query.get(record_id)
            if record:
                # 删除对应的图片文件
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], record.image_path))
                except OSError:
                    pass  # 如果文件不存在则忽略
                db.session.delete(record)
                
        elif delete_type == 'today':
            # 删除今天的记录
            today = date.today()
            records = UnknownFace.query.filter(
                and_(
                    UnknownFace.timestamp >= today,
                    UnknownFace.timestamp < today + timedelta(days=1)
                )
            ).all()
            for record in records:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], record.image_path))
                except OSError:
                    pass
                db.session.delete(record)
                
        elif delete_type == 'all':
            # 删除所有记录
            records = UnknownFace.query.all()
            for record in records:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], record.image_path))
                except OSError:
                    pass
                db.session.delete(record)
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })

@main.route('/login', methods=['GET', 'POST'])
def login():
    """登录路由"""
    # 如果用户已登录直接重定向到主页
    if session.get('logged_in'):
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 这里添加你的用户验证逻辑
        if username == 'root' and password == '123456':  # 示例验证
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            })
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    """登出路由"""
    session.clear()
    return redirect(url_for('main.login'))

@main.route('/monitor')
@login_required
def monitor():
    """外部监控页面"""
    return render_template('monitor.html')

def get_server_ips():
    """获取服务器IP地址"""
    # 获取本地IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"


    return {
        "local": local_ip + ":5000"
    }

@main.route('/system_status')
@login_required
def system_status():
    """获取系统状态信息"""
    try:
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_used = round(memory.used / (1024.0 * 1024.0 * 1024.0), 2)  # GB
        memory_total = round(memory.total / (1024.0 * 1024.0 * 1024.0), 2)  # GB
        memory_percent = memory.percent
        
        # 系统温度（树莓派特有）
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = round(float(f.read()) / 1000.0, 1)
        except:
            temp = 0
        
        # 系统运行时间
        uptime = time.time() - SYSTEM_START_TIME
        
        # 添加IP地址信息
        server_ips = get_server_ips()
        
        return jsonify({
            'success': True,
            'data': {
                'cpu_percent': cpu_percent,
                'memory_used': memory_used,
                'memory_total': memory_total,
                'memory_percent': memory_percent,
                'temperature': temp,
                'uptime': uptime,
                'server_ips': server_ips  # 添加IP地址信息
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@main.route('/set_tolerance', methods=['POST'])
@login_required
def set_tolerance():
    """设置人脸识别阈值"""
    global FACE_TOLERANCE
    try:
        tolerance = float(request.json.get('tolerance'))
        if tolerance not in [0.3, 0.4, 0.5, 0.6]:
            return jsonify({'success': False, 'message': '无效的阈值'})
        
        FACE_TOLERANCE = tolerance
        # 更新相机的阈值
        if camera:
            camera.set_tolerance(tolerance)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})