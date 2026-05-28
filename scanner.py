import asyncio
import aiohttp
import os

# 配置参数
TARGET_IP = "211.72.174.95"
START_PORT = 8110
END_PORT = 8150  # 扫描到8150，可根据需要自行扩大范围
OUTPUT_FILE = "live.m3u"

# 预设的已知频道名称映射，未知的会显示为“未知频道”
CHANNEL_MAPs = {
    8112: "TVB 翡翠台",
    8113: "华视 (CTS)",
    8114: "公视 (PTS)",
    8115: "台视 (TTV)",
    8116: "民视 (FTV)",
    8117: "中视 (CTV)",
}

async def check_port(session, port):
    url = f"http://{TARGET_IP}:{port}/0.ts"
    headers = {"Range": "bytes=0-1024"} # 使用Range请求，不消耗服务器和流媒体流量
    
    try:
        async with session.get(url, headers=headers, timeout=3) as response:
            # 状态码 200 或 206(部分内容) 均代表视频流服务存活
            if response.status in [200, 206]:
                name = CHANNEL_MAPs.get(port, f"台湾有线备用频道-{port}")
                print(f"[+] 发现有效源 -> 端口 {port}: {name}")
                return {"port": port, "name": name, "url": url}
    except Exception:
        pass
    return None

async def main():
    print(f"开始扫描服务器 {TARGET_IP} 的端口区间 {START_PORT}-{END_PORT}...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [check_port(session, port) for port in range(START_PORT, END_PORT + 1)]
        results = await asyncio.gather(*tasks)
        
    # 过滤出有效连接
    valid_channels = [r for r in results if r is not None]
    
    # 生成 M3U 文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U name=\"台湾网络数字电视\"\n")
        for ch in valid_channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch["port"]}" group-title="台湾数字电视",{ch["name"]}\n')
            f.write(f'{ch["url"]}\n')
            
    print(f"扫描完成，共找到 {len(valid_channels)} 个有效频道，已写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())

