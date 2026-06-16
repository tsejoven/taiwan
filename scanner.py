import cloudscraper
import time

# ================= 配置参数 =================
# 注意：因为你的代理最终要在你的本地运行（端口18080）
# 所以生成的 M3U 里面的 IP 应该指向你本地运行 Flask 的设备的内网 IP（例如 192.168.1.100）
# 或者如果你在公网部署，就写公网 IP。这里我先用 127.0.0.1 举例，你可以自行修改。
PROXY_SERVER_IP = "127.0.0.1" 
PROXY_PORT = 18080

START_NUM = 1   # 从 4gtv001 开始
END_NUM = 150   # 扫描到 4gtv150
OUTPUT_FILE = "live.m3u"
FORCE_WRITE = False  # 如果设为 True 则不测活直接生成所有；设为 False 则进行强力测活

# 已知频道的精确映射
CHANNEL_MAP = {
    39: "八大综合",
    40: "中视",
    41: "华视",
}

def check_channel(scraper, num):
    num_str = f"{num:03d}"
    # 这是直接向 4GTV 官方接口请求的路径
    target_path = f"4gtv-4gtv{num_str}/index.m3u8"
    target_url = f"https://4gtvmobile-mozai.4gtv.tv/{target_path}"
    
    # 最终生成的、供你播放器使用的本地代理地址
    play_url = f"http://{PROXY_SERVER_IP}:{PROXY_PORT}/{target_path}"
    name = CHANNEL_MAP.get(num, f"台湾有线台-4gtv{num_str}")

    if FORCE_WRITE:
        return {"name": name, "url": play_url, "num": num}

    # 模拟你 Flask 里完全一致的强力请求头
    headers = {
        "User-Agent": "%E5%9B%9B%E5%AD%A3%E7%B7%9A%E4%B8%8A/4 CFNetwork/3826.500.131 Darwin/24.5.0",
        "Referer": "https://www.4gtv.tv/",
        "fsdevice": "iOS",
        "fsversion": "3.2.8",
        "Content-Type": "application/json; charset=UTF-8",
        "Accept-Encoding": "identity"
    }

    try:
        # 使用 cloudscraper 绕过五秒盾去测活
        resp = scraper.get(target_url, headers=headers, timeout=5, allow_redirects=False)
        if resp.status_code == 200 and "#EXTM3U" in resp.text:
            print(f"[+] 成功绕过 CF 防御，发现有效源 -> {name}")
            return {"name": name, "url": play_url, "num": num}
    except Exception as e:
        # 打印错误方便在 GitHub Actions 日志里排查
        print(f"[-] 频道 {num_str} 请求失败: {str(e)}")
        pass
    return None

def main():
    print("正在初始化高级 Cloudflare 绕过模块...")
    scraper = cloudscraper.create_scraper()
    valid_channels = []

    print(f"开始扫描官方四季源，区间 4gtv001 - 4gtv{END_NUM:03d}...")
    
    # 由于 cloudscraper 是同步请求，为了防止请求过快被风控，我们使用单线程顺序扫描
    # 并且在每次请求之间加入微小的随机延迟
    for num in range(START_NUM, END_NUM + 1):
        result = check_channel(scraper, num)
        if result:
            valid_channels.append(result)
        # 适当减缓速度，模拟真人 App 行为
        time.sleep(0.2)

    valid_channels.sort(key=lambda x: x["num"])
    
    # 按照 “名字,链接” 格式写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for ch in valid_channels:
            f.write(f'{ch["name"]},{ch["url"]}\n')
            
    print(f"清洗完成！共写入 {len(valid_channels)} 行代理源数据到 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
