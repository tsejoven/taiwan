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
        "-timeout", "5000000",  # 5,000,000 微秒 = 5 秒
        url
    ]
    
    try:
        # 執行命令
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=6)
        if result.returncode == 0:
            print(print(f"✅ 發現可用頻道: tv{tv_number}"))
            return f"盲测频道 tv{tv_number},{url}\n"
    except Exception:
        pass
    return None

def main():
    print("🚀 開始並行盲測 rtmp://f13.mine.nu/sat/tv001 - tv999 ...")
    valid_channels = []
    
    # 建立一個擁有 30 個並行執行緒的執行緒池（防止 GitHub 被封禁，同時保持高效）
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        # 投放 1 到 999 的掃描任務
        futures = {executor.submit(check_rtmp_source, i): i for i in range(1, 1000)}
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                valid_channels.append(res)

    # 將所有存活的有效源寫入檔案
    valid_channels.sort()  # 按序排列
    with open("valid_rtmp.txt", "w", encoding="utf-8") as f:
        f.writelines(valid_channels)
        
    print(f"\n🎉 掃描完成！共發現 {len(valid_channels)} 個可用頻道，已寫入 valid_rtmp.txt")

if __name__ == "__main__":
    main()
