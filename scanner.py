import asyncio
import aiohttp

# ================= 配置参数 =================
TARGET_IP = "211.23.125.95"
PORT = 50007
START_NUM = 1   # 从 4gtv001 开始
END_NUM = 150   # 扫描到 4gtv150
OUTPUT_FILE = "live.m3u"
FORCE_WRITE = True  # 【关键配置】如果设为 True，则不论测活是否成功，都强制生成所有链接

# 已知频道的精确映射
CHANNEL_MAP = {
    39: "八大综合",
    40: "中视",
    41: "华视",
    # 你可以在这里继续添加你知道的频道编号
}

async def check_channel(session, num):
    num_str = f"{num:03d}"
    url = f"http://{TARGET_IP}:{PORT}/4gtv-4gtv{num_str}/index.m3u8?proxy=true"
    name = CHANNEL_MAP.get(num, f"台湾有线台-4gtv{num_str}")
    
    if FORCE_WRITE:
        # 如果开启了强制写入，不消耗时间去请求，直接返回结果
        return {"name": name, "url": url, "num": num}
        
    try:
        async with session.get(url, timeout=3) as response:
            if response.status == 200:
                return {"name": name, "url": url, "num": num}
    except Exception:
        pass
    return None

async def main():
    print(f"正在生成四季源数据...")
    
    connector = aiohttp.TCPConnector(limit=15)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_channel(session, num) for num in range(START_NUM, END_NUM + 1)]
        results = await asyncio.gather(*tasks)
        
    valid_channels = [r for r in results if r is not None]
    valid_channels.sort(key=lambda x: x["num"])
    
    # 按照你要求的 “名字,链接” 格式写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for ch in valid_channels:
            f.write(f'{ch["name"]},{ch["url"]}\n')
            
    print(f"处理完成！共写入 {len(valid_channels)} 行数据到 {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
