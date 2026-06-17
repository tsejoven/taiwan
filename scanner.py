import subprocess
import concurrent.futures

def check_rtmp_source(num):
    """
    使用 ffprobe 對 RTMP 流進行超時探測
    """
    tv_number = f"{num:03d}"
    url = f"rtmp://f13.mine.nu/sat/tv{tv_number}"
    
    # 呼叫 ffprobe 獲取流資訊，設定 5 秒超時
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=format_name", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        "-timeout", "5000000",  # 5 秒
        url
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=6)
        if result.returncode == 0:
            print(f"✅ 發現可用頻道: tv{tv_number}")
            return {"num": tv_number, "url": url}
    except Exception:
        pass
    return None

def main():
    print("🚀 開始並行盲測 rtmp://f13.mine.nu/sat/tv001 - tv999 ...")
    valid_list = []
    
    # 使用 30 執行緒並行掃描
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(check_rtmp_source, i): i for i in range(1, 1000)}
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                valid_list.append(res)

    # 按頻道號排序
    valid_list.sort(key=lambda x: x["num"])

    # 1. 生成 TXT 格式（方便你手動改名、備註）
    with open("valid_rtmp.txt", "w", encoding="utf-8") as f_txt:
        for ch in valid_list:
            f_txt.write(f"盲测频道 tv{ch['num']},{ch['url']}\n")

    # 2. 生成標準的 M3U 格式（方便播放器直接識別）
    with open("valid_rtmp.m3u", "w", encoding="utf-8") as f_m3u:
        f_m3u.write("#EXTM3U\n")
        for ch in valid_list:
            f_m3u.write(f'#EXTINF:-1 group-title="盲测扫台",盲测频道 tv{ch["num"]}\n{ch["url"]}\n')
        
    print(f"\n🎉 掃描完成！共發現 {len(valid_list)} 個可用頻道。")
    print("📁 已同步写入 valid_rtmp.txt 和 valid_rtmp.m3u")

if __name__ == "__main__":
    main()
