import asyncio
import aiohttp

# ================= 配置参数 =================
TARGET_IP = "211.23.125.95"
PORT = 50007
START_NUM = 1   # 从 4gtv001 开始
END_NUM = 150   # 扫描到 4gtv150（覆盖绝大多数四季线上的频道区间）
OUTPUT_FILE = "live.m3u"

# 已知频道的精确映射（扫描到对应的编号时会自动命名，未知的会自动命名为"台湾有线台-编号"）
CHANNEL_MAP = {
    39: "八大综合台",
    40: "中视",
    41: "华视",
    # 你可以根据后续扫描出来的结果，在这里手动添加更多名字，例如：
    # 42: "民视", 
}

async def check_channel(session, num):
    # 格式化数字为 3 位补零，如 39 变成 "039"
    num_str = f"{num:03d}"
    
    # 构建完整的测试 URL
    url = f"http://{TARGET_IP}:{PORT}/4gtv-4gtv{num_str}/index.m3u8?proxy=true"
    
    try:
        # HLS(M3U8) 测活只需要获取索引文件，3秒超时足够
        async with session.get(url, timeout=3) as response:
            # 如果返回 200 OK，说明该频道在线且可以播放
            if response.status == 200:
                name = CHANNEL_MAP.get(num, f"台湾有线台-4gtv{num_str}")
                print(f"[+] 发现有效源 -> {name}")
                return {"name": name, "url": url, "num": num}
    except Exception:
        pass
    return None

async def main():
    print(f"开始扫描四季代理源 ({TARGET_IP}:{PORT})，区间 4gtv001 - 4gtv{END_NUM:03d}...")
    
    # 限制并发量，防止请求过快被服务器临时屏蔽
    connector = aiohttp.TCPConnector(limit=15)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_channel(session, num) for num in range(START_NUM, END_NUM + 1)]
        results = await asyncio.gather(*tasks)
        
    # 过滤掉无效结果并排序
    valid_channels = [r for r in results if r is not None]
    valid_channels.sort(key=lambda x: x["num"])
    
    # 写入 M3U 文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U name=\"台湾四季有线电视\"\n")
        for ch in valid_channels:
            f.write(f'#EXTINF:-1 group-title=\"台湾四季源\",{ch["name"]}\n')
            f.write(f'{ch["url"]}\n')
            
    print(f"扫描完成！共找到 {len(valid_channels)} 个有效频道，已写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
