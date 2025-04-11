from picamera2 import Picamera2
import time

# 初始化相机
picam2 = Picamera2()

# 配置相机
camera_config = picam2.create_still_configuration()
picam2.configure(camera_config)

# 启动相机
picam2.start()

# 等待相机稳定
time.sleep(2)

# 拍照并保存为图片文件
picam2.capture_file("image.jpg")

# 关闭相机
picam2.close()

print("拍照完成，图片已保存为 image.jpg")
