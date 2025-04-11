import os

# # 设置音量为50%
os.system('amixer set Master 50%')

# 开心
file_name_kaixin = "/home/pi/Desktop/mineCode/music/kaixin.mp3"  # 0 
file_name_shengqi = "/home/pi/Desktop/mineCode/music/shengqi.mp3"  # 1
file_name_nomal = "/home/pi/Desktop/mineCode/music/nomal.mp3"  # 2
file_name_shangxin = "/home/pi/Desktop/mineCode/music/shangxin.mp3"  # 3

# 播放开心函数
def play_kaixin():
    os.system('mplayer %s' % file_name_kaixin)

# 播放生气函数
def play_shengqi():
    os.system('mplayer %s' % file_name_shengqi)

# 播放正常函数
def play_nomal():
    os.system('mplayer %s' % file_name_nomal)

def play_shangxin():
    os.system('mplayer %s' % file_name_shangxin)


if __name__ == "__main__":
    play_kaixin()
    # play_shengqi()
    # play_nomal()
    # play_shangxin()
