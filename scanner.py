import os
import requests
import re

# ================= 配置参数 =================
BASE_URL = "http://4t.537224.xyz/live/4gtv-4gtv"
START_NUM = 1
END_NUM = 100
OUTPUT_FILE = "live.m3u"

# 第三方实时更新的四季台标数据库（这里使用的是公开维护的四季清单源）
MAP_URL = "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"

def get_dynamic_channel_map():
    """动态从公网获取最新的四季频道名称映射表"""
    channel_map = {}
    print("正在从公网获取最新动态台标库...")
    try:
        # 设置5秒超时，防止网络卡死
        response = requests.get(MAP_URL, timeout=5)
        if response.status_code == 200:
            text = response.text
            # 使用正则表达式，在大佬的 M3U 文件里搜寻形如 4gtv045 的特征
            # 匹配格式示例：#EXTINF:-1 ...,华视新闻台 \n ...4gtv-4gtv045
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n.*?4gtv-4gtv(\d{3})', text)
            for name, num_str in matches:
                # 存入字典，如 {45: "华视新闻台"}
                channel_map[int(num_str)] = name.strip()
            print(f"动态台标库加载成功！共匹配到 {len(channel_map)} 个最新的频道名称。")
    except Exception as e:
        print(f"警告：动态台标库获取失败 ({str(e)})，将启用备用数字命名。")
    return channel_map

def main():
    # 1. 动态获取最新的名字映射表
    dynamic_map = get_dynamic_channel_map()
    
    print(f"正在基于全新格式批量生成 4gtv001 到 4gtv{END_NUM:03d} 的直播源地址...")
    
    lines = []
    for num in range(START_NUM, END_NUM + 1):
        num_str = f"{num:03d}"
        
        # 2. 优先从动态库里找名字，找不到的再用数字兜底
        name = dynamic_map.get(num, f"四季频道-{num_str}")
        url = f"{BASE_URL}{num_str}"
        
        lines.append(f"{name},{url}")

    # 3. 写入 live.m3u 文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")
            
    print(f"跑完了！已成功将 {len(lines)} 个频道写入 {OUTPUT_FILE}。")

if __name__ == "__main__":
    main()
