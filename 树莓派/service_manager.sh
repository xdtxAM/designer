#!/bin/bash

# 定义颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
SERVICE_NAME="auto.service"

# 检查是否为root用户运行
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}请使用sudo运行此脚本${NC}"
        exit 1
    fi
}

# 显示菜单
show_menu() {
    clear
    echo -e "${GREEN}=== 服务管理脚本 ===${NC}"
    echo -e "${YELLOW}1.${NC} 授予服务权限"
    echo -e "${YELLOW}2.${NC} 启动服务"
    echo -e "${YELLOW}3.${NC} 停止服务"
    echo -e "${YELLOW}4.${NC} 设置开机自启动"
    echo -e "${YELLOW}5.${NC} 关闭开机自启动"
    echo -e "${YELLOW}6.${NC} 查看服务状态"
    echo -e "${YELLOW}7.${NC} 查看服务日志"
    echo -e "${YELLOW}8.${NC} 清除服务日志"
    echo -e "${YELLOW}9.${NC} 退出"
    echo
    echo -e "${GREEN}请输入选项 [1-9]:${NC}"
}

# 授予服务权限
grant_permissions() {
    echo -e "${GREEN}正在授予服务权限...${NC}"
    chmod 644 /etc/systemd/system/$SERVICE_NAME
    systemctl daemon-reload
    echo -e "${GREEN}权限已更新${NC}"
    sleep 2
}

# 启动服务
start_service() {
    echo -e "${GREEN}正在启动服务...${NC}"
    systemctl start $SERVICE_NAME
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}服务已启动${NC}"
    else
        echo -e "${RED}服务启动失败${NC}"
    fi
    sleep 2
}

# 停止服务
stop_service() {
    echo -e "${YELLOW}正在停止服务...${NC}"
    systemctl stop $SERVICE_NAME
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}服务已停止${NC}"
    else
        echo -e "${RED}服务停止失败${NC}"
    fi
    sleep 2
}

# 设置开机自启动
enable_service() {
    echo -e "${GREEN}正在设置开机自启动...${NC}"
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}已设置开机自启动${NC}"
    else
        echo -e "${RED}设置失败${NC}"
    fi
    sleep 2
}

# 关闭开机自启动
disable_service() {
    echo -e "${YELLOW}正在关闭开机自启动...${NC}"
    systemctl disable $SERVICE_NAME
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}已关闭开机自启动${NC}"
    else
        echo -e "${RED}关闭失败${NC}"
    fi
    sleep 2
}

# 查看服务状态
check_status() {
    echo -e "${GREEN}服务状态:${NC}"
    systemctl status $SERVICE_NAME
    echo -e "\n${YELLOW}按任意键返回菜单${NC}"
    read -n 1
}

# 查看服务日志
view_logs() {
    echo -e "${GREEN}服务日志:${NC}"
    journalctl -u $SERVICE_NAME
    echo -e "\n${YELLOW}按任意键返回菜单${NC}"
    read -n 1
}

# 清除服务日志
clear_logs() {
    echo -e "${YELLOW}正在清除服务日志...${NC}"
    journalctl --rotate
    journalctl --vacuum-time=1s
    echo -e "${GREEN}日志已清除${NC}"
    sleep 2
}

# 主循环
main() {
    check_root
    while true; do
        show_menu
        read -r opt
        case $opt in
            1) grant_permissions ;;
            2) start_service ;;
            3) stop_service ;;
            4) enable_service ;;
            5) disable_service ;;
            6) check_status ;;
            7) view_logs ;;
            8) clear_logs ;;
            9) echo -e "${GREEN}再见！${NC}"; exit 0 ;;
            *) echo -e "${RED}无效选项，请重试${NC}"; sleep 2 ;;
        esac
    done
}

# 运行主程序
main