import os

# ================= 配置参数 =================
# 填入你本地运行 Flask 脚本的那台电脑的局域网内网 IP（例如 192.168.31.50）
# 如果你只在运行 Flask 的同一台电脑上看，可以保持 "127.0.0.1"
PROXY_SERVER_IP = "127.0.0.1" 
PROXY_PORT = 18080

START_NUM = 1   # 从 4gtv001 开始
END_NUM = 150   # 盲推到 4gtv150
OUTPUT_FILE = "live.m3u"

# 已知频道的精确映射（只要对上号的，就会显示中文名；对不上的显示数字编号）
CHANNEL_MAP = {
    2: "民视无线台",
    31: "民视新闻台",
    39: "八大综合",
    40: "中视",
    41: "华视",
    42: "台视",
    43: "公视",
    83: "TVBS新闻",
}

def main():
    print("【模式：直接盲推生成】正在为您批量生成所有 4GTV 代理链接...")
    
    channels_list = []
    for num in range(START_NUM, END_NUM + 1):
        num_str = f"{num:03d}"
        target_path = f"4gtv-4gtv{num_str}/index.m3u8"
        
        # 拼接成你本地 Flask 代理需要的标准格式
        play_url = f"http://{PROXY_SERVER_IP}:{PROXY_PORT}/{target_path}"
        name = CHANNEL_MAP.get(num, f"四季有线台-4gtv{num_str}")
        
        channels_list.append(f"{name},{play_url}")

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in channels_list:
            f.write(f"{line}\n")
            
    print(f"成功！已强制生成 {len(channels_list)} 行数据到 {OUTPUT_FILE}，不再受 GitHub 境外 IP 限制。")

if __name__ == "__main__":
    main()
