import subprocess
import concurrent.futures

def check_rtmp_source(num):
    """
    使用 ffprobe 对 RTMP 流进行超时探测
    """
    tv_number = f"{num:03d}"
    url = f"rtmp://f13.mine.nu/sat/tv{tv_number}"
    
    # 调用 ffprobe 获取流信息，设置 5 秒超时
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=format_name", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        "-timeout", "5000000",  # 5,000,000 微秒 = 5 秒
        url
    ]
    
    try:
        # 执行命令
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=6)
        if result.returncode == 0:
            print(f"✅ 发现可用频道: tv{tv_number}")
            return f"盲测频道 tv{tv_number},{url}\n"
    except Exception:
        pass
    return None

def main():
    print("🚀 开始并行盲测 rtmp://f13.mine.nu/sat/tv001 - tv999 ...")
    valid_channels = []
    
    # 建立一个拥有 30 个并行线程的线程池
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(check_rtmp_source, i): i for i in range(1, 1000)}
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                valid_channels.append(res)

    # 将所有存活的有效源写入文件
    valid_channels.sort()  # 按序排列
    with open("valid_rtmp.txt", "w", encoding="utf-8") as f:
        f.writelines(valid_channels)
        
    print(f"\n🎉 扫描完成！共发现 {len(valid_channels)} 个可用频道，已写入 valid_rtmp.txt")

if __name__ == "__main__":
    main()
