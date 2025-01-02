import cv2
import face_recognition
import threading
import queue
import time
import os
import pickle

import RPi.GPIO as GPIO

# 禁用GPIO警告
GPIO.setwarnings(False)

# 定义LED引脚
LED_PIN = 17
beep_PIN = 12

# 设置GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(beep_PIN, GPIO.OUT)

class FaceCamera:
    def __init__(self):
        """初始化相机类"""
        self.frame_queue = queue.Queue(maxsize=2)
        self.face_locations = []
        self.face_names = []
        self.stop_thread = False
        self.skip_frames = 2  # 每隔几帧进行一次人脸检测
        self.frame_count = 0
        self.tolerance = 0.4  # 默认阈值
        
        # 设置路径
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.cache_file = os.path.join(self.base_dir, 'face_encodings_cache.pkl')
        
        # 加载已知人脸
        self.known_face_encodings = []
        self.known_face_names = []
        print("正在加载人脸特征...")
        start_time = time.time()
        self.load_known_faces()
        print(f"加载完成，用时: {time.time() - start_time:.2f}秒")
        
        # 启动检测线程
        self.detection_thread = threading.Thread(target=self._detect_face_thread)
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def load_known_faces(self, faces_dir="./authorized_faces"):
        """加载已知���脸特征，优先使用缓存"""
        # 检查缓存是否存在且有效
        cache_valid = False
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    cache_time = os.path.getmtime(self.cache_file)
                    
                    # 检查缓存文件是否比所有人脸图片新
                    cache_valid = all(
                        os.path.getmtime(os.path.join(faces_dir, f)) <= cache_time
                        for f in os.listdir(faces_dir)
                        if f.endswith(('.jpg', '.jpeg', '.png'))
                    )
                    
                    if cache_valid:
                        self.known_face_encodings = cache_data['encodings']
                        self.known_face_names = cache_data['names']
                        print("从缓存加载人脸特征成功")
                        return
            except Exception as e:
                print(f"读取缓存失败: {e}")

        # 如果缓存无效，重新加载人脸特征
        print("重新加载人脸特征...")
        encodings = []
        names = []
        
        for filename in os.listdir(faces_dir):
            if filename.endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(faces_dir, filename)
                try:
                    image = cv2.imread(image_path)
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    face_locations = face_recognition.face_locations(rgb_image, model="hog")
                    if face_locations:
                        face_encoding = face_recognition.face_encodings(rgb_image, [face_locations[0]])[0]
                        encodings.append(face_encoding)
                        names.append(os.path.splitext(filename)[0])
                        print(f"已加载: {filename}")
                except Exception as e:
                    print(f"处理 {filename} 时出错: {e}")
        
        self.known_face_encodings = encodings
        self.known_face_names = names
        
        # 保存缓存
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump({
                    'encodings': encodings,
                    'names': names
                }, f)
            print("已保存人脸特征缓存")
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def set_tolerance(self, tolerance):
        """设置人脸识别阈值"""
        self.tolerance = tolerance

    def _detect_face_thread(self):
        """人脸检测线程"""
        while not self.stop_thread:
            try:
                frame = self.frame_queue.get(timeout=1)
                self.frame_count += 1

                # 每隔几帧才进行人脸检测
                if self.frame_count % self.skip_frames != 0:
                    continue

                # 缩小尺寸以加快处理速度
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # 使用 CNN 模型在 GPU 上运行，或使用 HOG 在 CPU 上运行
                face_locations = face_recognition.face_locations(rgb_small_frame, 
                                                              model="hog",
                                                              number_of_times_to_upsample=1)
                
                self.face_locations = [(top*4, right*4, bottom*4, left*4)
                                     for (top, right, bottom, left) in face_locations]
                
                if face_locations:
                    # 批量处理人脸编码
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, 
                                                                   face_locations,
                                                                   num_jitters=0)
                    names = []
                    for face_encoding in face_encodings:
                        # 使用实例变量的阈值
                        matches = face_recognition.compare_faces(self.known_face_encodings, 
                                                              face_encoding,
                                                              tolerance=self.tolerance)
                        name = "Unknown"
                        
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = self.known_face_names[first_match_index]

                            # 如果匹配到已知人脸，点亮LED
                            GPIO.output(LED_PIN, GPIO.HIGH)
                        elif name == "Unknown":
                            # 关闭LED
                            GPIO.output(LED_PIN, GPIO.LOW)
                            # 激活蜂鸣器
                            GPIO.output(beep_PIN, GPIO.HIGH)
                            time.sleep(1)
                            GPIO.output(beep_PIN, GPIO.LOW)
                        
                        names.append(name)
                    
                    self.face_names = names
                else:
                    # 如果未检测到人脸，关闭LED
                    GPIO.output(LED_PIN, GPIO.LOW)
                    self.face_names = []
                    
            except queue.Empty:
                continue

    def get_frame(self):
        """获取处理后的视频帧"""
        if not hasattr(self, 'cap') or self.cap is None:
            return None
        
        try:
            success, frame = self.cap.read()
            if not success:
                return None
        
            try:
                if self.frame_queue.full():
                    self.frame_queue.get_nowait()
                self.frame_queue.put_nowait(frame.copy())
            except queue.Full:
                pass
        
            # 在图像上绘制人脸框和名字
            if self.face_locations and self.face_names:
                for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                    top, right, bottom, left = map(int, (top, right, bottom, left))
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 0), cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6), 
                              cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
            
            return frame
        
        except Exception as e:
            print(f"处理视频帧时出错: {str(e)}")
            return None

    def __enter__(self):
        """上下文管理器入口"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError("无法打开摄像头")
            
            # 设置更高的摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 60)  # 提高帧率
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲
            
            # 设置摄像头的其他参数
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # 禁用自动对焦
            self.cap.set(cv2.CAP_PROP_EXPOSURE, -7)  # 降低曝光时间
            
            return self
                
        except Exception as e:
            print(f"摄像头初始化失败: {str(e)}")
            if hasattr(self, 'cap') and self.cap is not None:
                self.cap.release()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop_thread = True
        if hasattr(self, 'detection_thread'):
            self.detection_thread.join()
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()