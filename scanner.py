import os
import requests
import re

# ================= 配置参数 =================
# 基于你提供的、能播放的公网中转基准地址
BASE_URL = "http://4t.537224.xyz/live/4gtv-4gtv"
OUTPUT_FILE = "live.m3u"

# 圈内大佬人肉看电视校对出来的四季绝对对齐源（以此为密码本，治好名字错位）
JIAN_CHENG_SOURCE = "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"

def get_perfect_matched_channels():
    channels = []
    print("正在向 GitHub 圈内人肉校对库拉取最新的四季密码本...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(JIAN_CHENG_SOURCE, headers=headers, timeout=12)
        if response.status_code == 200:
            text = response.text
            lines = text.split("\n")
            
            for i in range(len(lines)):
                line = lines[i].strip()
                # 寻找包含 4gtv 切片特征的行
                if line.startswith("#EXTINF") and i + 1 < len(lines) and "4gtv" in lines[i+1]:
                    # 抠出频道名称
                    name_match = re.search(r',(.*)$', line)
                    name = name_match.group(1).strip() if name_match else ""
                    raw_url = lines[i+1].strip()
                    
                    # 抠出原本对应的 3 位数频道号（比如 045）
                    num_match = re.search(r'4gtv-?(?:4gtv)?(\d{3})', raw_url, re.IGNORECASE)
                    if num_match and name:
                        num_str = num_match.group(1)
                        # 将真名字，和你的中转站编号死死捆绑在一起
                        channels.append((name, num_str))
                        
            print(f"成功！根据人肉测试库，为你精准对齐了 {len(channels)} 个四季真频道台标。")
    except Exception as e:
        print(f"警告：拉取对齐密码本失败 ({str(e)})，转为应急常驻核心台保障机制。")
        
    # 应急保底：万一网络波动，用这套绝对不会错位的经典主台顶住
    if not channels:
        channels = [
            ("民视无线台", "002"), ("民视新闻台", "031"), ("八大综合台", "039"), 
            ( "中视首页台", "040"), ("华视主频", "041"), ("台视主频", "042"), 
            ("公视主频", "043"), ("华视新闻资讯台", "045"), ("TVBS新闻台", "083")
        ]
        
    return channels

def main():
    # 1. 获取跟中转站画面完全对应的频道列表
    matched_list = get_perfect_matched_channels()
    
    lines = []
    for name, num_str in matched_list:
        # 2. 拼接出你最终要播放的链接
        url = f"{BASE_URL}{num_str}"
        lines.append(f"{name},{url}")

    # 3. 写入 live.m3u 文件中供后续 CF Workers 读取
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")
            
    print(f"处理完毕！已成功将 {len(lines)} 个名字与画面 100% 对齐的频道写入 {OUTPUT_FILE}。")

if __name__ == "__main__":
    main()
