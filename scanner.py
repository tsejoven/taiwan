import os

# ================= 配置参数 =================
# 基于你提供的最新格式：http://4t.537224.xyz/live/4gtv-4gtv045
BASE_URL = "http://4.537224.xyz/live/4gtv-4gtv"
START_NUM = 1
END_NUM = 100
OUTPUT_FILE = "live.m3u"

# 已知常见频道的中文名称映射（没配的名字会自动显示为“四季频道-XXX”）
CHANNEL_MAP = {
    2: "民视无线台",
    31: "民视新闻台",
    39: "八大综合",
    40: "中视",
    41: "华视",
    42: "台视",
    43: "公视",
    45: "华视新闻台",  # 基于你提供的045测试
    83: "TVBS新闻",
}

def main():
    print(f"正在基于全新格式批量生成 4gtv001 到 4gtv{END_NUM:03d} 的直播源地址...")
    
    lines = []
    for num in range(START_NUM, END_NUM + 1):
        # 补零成 3 位数，如 1 变成 001，45 变成 045
        num_str = f"{num:03d}"
        
        # 拼接出标准的频道名称和资源链接
        name = CHANNEL_MAP.get(num, f"四季频道-{num_str}")
        url = f"{BASE_URL}{num_str}"
        
        # 组合成你要求的“名字,链接”格式
        lines.append(f"{name},{url}")

    # 写入 live.m3u 文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")
            
    print(f"跑完了！已成功将 {len(lines)} 个频道写入 {OUTPUT_FILE}。")

if __name__ == "__main__":
    main()
