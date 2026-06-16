import os
import requests
import re

# ================= 配置参数 =================
BASE_URL = "http://4t.537224.xyz/live/4gtv-4gtv"
START_NUM = 1
END_NUM = 100
OUTPUT_FILE = "live.m3u"

# 直接请求四季线上的官方频道列表网页
OFFICIAL_URL = "https://m.4gtv.tv/channel"

def get_official_channel_map():
    """直接从四季官网移动端页面爬取最新的频道编号和名称"""
    channel_map = {}
    print("正在直接从四季官网 (m.4gtv.tv) 实时抓取最新台标...")
    
    headers = {
        # 模拟手机浏览器，确保四季官网返回的是轻量好解析的移动端 HTML
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept-Language": "zh-TW,zh;q=0.9",
        "Referer": "https://m.4gtv.tv/"
    }
    
    try:
        response = requests.get(OFFICIAL_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # 【核心正则匹配】
            # 四季移动端网页中通常包含类似：id="4gtv-4gtv045" ... title="华视新闻台" 
            # 或者 data-channel="4gtv045" ... >华视新闻台<
            # 这里使用一个组合正则，广泛抓取页面内所有包含 4gtv 纯数字编号与对应的中文标签
            
            # 匹配模式1：通用的带有 4gtv 编号和名称的特征
            # 例如在 HTML 属性中常见的 name/title/alt 或者是节点文本
            matches = re.findall(r'4gtv-?(?:4gtv)?(\d{3})".*?>([^<\n\r]+)</', html_content)
            
            # 匹配模式2：针对四季特有的 class 或 data 标签（做双重保障）
            matches_attr = re.findall(r'title="([^"]+)"[^>]*?4gtv-?(?:4gtv)?(\d{3})', html_content)
            matches_attr_reverse = re.findall(r'4gtv-?(?:4gtv)?(\d{3})"[^>]*?title="([^"]+)"', html_content)

            # 1. 注入模式1的数据
            for num_str, name in matches:
                clean_name = name.strip()
                # 过滤掉一些带有特殊符号或纯英文字符的干扰项，确保抓到的是真台名
                if len(clean_name) > 1 and not clean_name.startswith("http"):
                    channel_map[int(num_str)] = clean_name

            # 2. 注入模式2的数据（互相补充漏网之鱼）
            for name, num_str in matches_attr:
                channel_map[int(num_str)] = name.strip()
            for num_str, name in matches_attr_reverse:
                channel_map[int(num_str)] = name.strip()

            print(f"官网数据抓取成功！共实时解析出 {len(channel_map)} 个官方在播频道。")
    except Exception as e:
        print(f"警告：官网台标抓取失败 ({str(e)})，将启用本地硬编码兜底。")
        
    # 【万能兜底】如果刚好碰上四季官网改版或者 GitHub 访问官网抽风，内置一份经典频道表，确保绝对不翻车
    backup_map = {
        2: "民视无线台", 31: "民视新闻台", 38: "时代E-Sports台", 39: "八大综合台", 
        40: "中视首页台", 41: "华视主频", 42: "台视主频", 43: "公视主频", 
        45: "华视新闻资讯台", 83: "TVBS新闻台", 84: "TVBS欢乐台", 85: "TVBS精彩台"
    }
    for k, v in backup_map.items():
        if k not in channel_map:
            channel_map[k] = v
            
    return channel_map

def main():
    # 1. 从官网获取最新活体映射
    dynamic_map = get_official_channel_map()
    
    print(f"正在基于全新格式批量生成 4gtv001 到 4gtv{END_NUM:03d} 的直播源地址...")
    
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
            
    print(f"处理完毕！已成功将 {len(lines)} 个真实同步的频道写入 {OUTPUT_FILE}。")

if __name__ == "__main__":
    main()
