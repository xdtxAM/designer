from PIL import Image, ImageDraw, ImageFont
import pyperclip

def create_font_bitmap(text, font_size=12, font_path="simsun.ttc"):
    """
    创建单个汉字的点阵数据
    采用逐行式，每行16位，高位在前
    """
    # 创建图像
    width = font_size
    height = font_size
    image = Image.new('1', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # 加载字体
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        print(f"无法加载字体文件 {font_path}")
        font = ImageFont.load_default()
    
    # 计算文字位置使其居中
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 1  # 稍微上移一点
    
    # 绘制文字
    draw.text((x, y), text, font=font, fill='black')
    
    # 获取点阵数据，逐行扫描
    pixels = []
    for y in range(height):
        # 每行16位，分成两个字节
        row_data = 0  # 存储这一行的16位数据
        
        # 扫描这一行的12个像素
        for x in range(width):
            pixel = image.getpixel((x, y))
            if pixel == 0:  # 黑点
                # 从左到右，高位在前，所以是15-x
                row_data |= (1 << (15-x))
        
        # 将16位数据分成两个字节
        byte1 = (row_data >> 8) & 0xFF  # 高8位
        byte2 = row_data & 0xFF         # 低8位
        pixels.append(byte1)
        pixels.append(byte2)
    
    return pixels

def generate_c51_code(text, font_size=12):
    """
    生成C51格式的代码
    """
    pixels = create_font_bitmap(text, font_size)
    
    # 生成十六进制数据
    hex_data = ','.join([f'0x{byte:02X}' for byte in pixels])
    
    return f'/*"{text}"*/\n{hex_data}'

def generate_chars_code(chars, font_size=12):
    """
    生成多个汉字的点阵代码并复制到剪贴板
    """
    results = []
    for char in chars:
        result = generate_c51_code(char, font_size)
        results.append(result)
    
    # 用换行符连接所有结果
    final_result = '\n\n'.join(results)
    
    # 打印结果
    print("生成的代码：")
    print(final_result)
    
    # 复制到剪贴板
    pyperclip.copy(final_result)
    print("\n代码已复制到剪贴板！")

def main():
    # 在这里定义要转换的汉字
    characters = ['亮', '度']
    font_size = 12
    
    generate_chars_code(characters, font_size)

if __name__ == "__main__":
    main()