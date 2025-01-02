from app import create_app, db
import os
import cv2

def check_camera():
    """检查摄像头是否可用"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("警告：无法访问摄像头，请检查摄像头是否正确连接")
        return False
    cap.release()
    return True

app = create_app()

# 确保必要的目录存在
with app.app_context():
    # 创建数据库目录
    os.makedirs('instance', exist_ok=True)
    
    # 创建图片保存目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 创建数据库表
    db.create_all()
    
    # 检查摄像头
    check_camera()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 