from PIL import Image, ImageDraw, ImageFont
import os

def create_font_bitmap(text, font_size=8, font_path="simsun.ttc"):
    """
    创建单个汉字的点阵数据，返回C51格式的十六进制数据
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
        print(f"无法加载字体文件 {font_path}，尝试使用系统默认字体")
        font = ImageFont.load_default()
    
    # 计算文字位置，使其居中
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 绘制文字
    draw.text((x, y), text, font=font, fill='black')
    
    # 获取点阵数据
    pixels = []
    for y in range(height):
        byte = 0
        for x in range(width):
            pixel = image.getpixel((x, y))
            # 黑色像素为1，白色像素为0
            if pixel == 0:  # 黑色
                byte |= (1 << (7-x))
        pixels.append(byte)
    
    return pixels

def generate_c51_code(text, font_size=8):
    """
    生成C51格式的代码
    """
    pixels = create_font_bitmap(text, font_size)
    
    # 生成注释
    comment = f'/*-- ID:0,字符:"{text}",ASCII编码:{text.encode("utf-8").hex()},对应字:宽x高={font_size}x{font_size},画布:宽W={font_size} 高H={font_size},共{len(pixels)}字节*/'
    
    # 生成十六进制数据
    hex_data = ','.join([f'0x{byte:02X}' for byte in pixels])
    
    return f"{comment}\n{hex_data}"

def main():
    # 示例使用
    characters = ['光', '线', '温', '湿', '度']
    font_size = 8  # 8x8点阵
    
    print("// 生成的C51格式点阵数据：")
    print()
    
    for char in characters:
        print(f"// {char}")
        print(generate_c51_code(char, font_size))
        print()

if __name__ == "__main__":
    main() 