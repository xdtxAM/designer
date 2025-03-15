screenSerial.print("SET_TXT(13,'");
screenSerial.write(0xCE); // "无" 的 GB2312 编码高位
screenSerial.write(0xDE); // "无" 的 GB2312 编码低位
screenSerial.write(0xC8); // "人" 的 GB2312 编码高位
screenSerial.write(0xCB); // "人" 的 GB2312 编码低位
screenSerial.println("');");
