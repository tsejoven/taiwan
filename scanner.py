import os
import requests
import re

# ================= 配置参数 =================
BASE_URL = "http://4t.537224.xyz/live/4gtv-4gtv"
START_NUM = 1
END_NUM = 100
OUTPUT_FILE = "live.m3u"

# 专属的台湾四季台标数据库地址
MAP_URL = "https://epg.pw/test_channels_taiwan.m3u"

def get_dynamic_channel_map():
    """从专属台湾频道列表中动态提取四季频道映射"""
    channel_map = {}
    print("正在从专属台湾频道库获取最新台标...")
    try:
        response = requests.get(MAP_URL, timeout=8)
        if response.status_code == 200:
            text = response.text
            # 改进的正则匹配：同时抓取包含 4gtv-4gtv 或者是 4gtv 后接数字的格式
            # 兼容 #EXTINF:-1 ...,民视新闻台\n...4gtv031 或者 4gtv-4gtv031
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n.*?4gtv-?(?:4gtv)?(\d{3})', text, re.IGNORECASE)
            
            for name, num_str in matches:
                # 剔除可能存在的特殊多余符号
                clean_name = name.strip().replace("\r", "")
                channel_map[int(num_str)] = clean_name
                
            print(f"专属台标库匹配完成！成功加载 {len(channel_map)} 个四季核心频道。")
    except Exception as e:
        print(f"警告：动态台标库获取失败 ({str(e)})，转为内置和数字兜底模式。")
        
    # 内置一份绝对不会变的核心五大台台标，防止网络意外时全变成数字
    backup_map = {2: "民视无线台", 31: "民视新闻台", 39: "八大综合", 40: "中视", 41: "华视", 42: "台视", 43: "公视", 45: "华视新闻台", 83: "TVBS新闻"}
    for k, v in backup_map.items():
        if k not in channel_map:
            channel_map[k] = v
            
    return channel_map

def main():
    # 1. 动态获取最新的名字映射表
    dynamic_map = get_dynamic_channel_map()
    
    print(f"正在批量生成 4gtv001 到 4gtv{END_NUM:03d} 的直播源地址...")
    
    lines = []
    for num in range(START_NUM, END_NUM + 1):
        num_str = f"{num:03d}"
        
        # 2. 匹配名字
        name = dynamic_map.get(num, f"四季频道-{num_str}")
        url = f"{BASE_URL}{num_str}"
        
        lines.append(f"{name},{url}")

    # 3. 写入 live.m3u 文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")
            
    print(f"处理完毕！已成功将 {len(lines)} 个频道写入 {OUTPUT_FILE}。")

if __name__ == "__main__":
    main()
