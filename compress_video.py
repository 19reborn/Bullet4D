import os
import subprocess
import shutil

# ================= 配置区域 =================
# 目标路径 (可以是具体视频文件，也可以是文件夹)
TARGET_PATH = "/Users/yiming/old_Documents/research/projects/Master_thesis/ms_thesis/cvpr_bullettime/website/bullet-time/static/videos/intro_public_1.mp4"

# 需要处理的视频后缀
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.mkv', '.avi', '.webm')

# FFmpeg 参数设置
CRF_VALUE = "25"  # 画质控制，数字越大体积越小，23-28 是网页常用范围
PRESET = "veryfast"
# ===========================================

def get_size_mb(path):
    """获取文件大小(MB)"""
    return os.path.getsize(path) / (1024 * 1024)

def compress_single_file(input_path):
    """处理单个视频文件的核心逻辑"""
    file_name = os.path.basename(input_path)
    dir_name = os.path.dirname(input_path)
    
    # 生成临时文件名
    temp_output_path = os.path.join(dir_name, f"temp_{file_name}")

    # 如果发现残留的临时文件，跳过
    if file_name.startswith("temp_"):
        return 0, 0 # (success_count, saved_space)

    original_size = get_size_mb(input_path)
    print(f"🎬 正在处理: {file_name} ({original_size:.2f} MB)...")

    # 构建 FFmpeg 命令
    cmd = [
        'ffmpeg',
        '-y',                 # 覆盖输出文件
        '-i', input_path,     # 输入文件
        '-vcodec', 'libx264', # 编码器
        '-crf', CRF_VALUE,    # 画质系数
        '-preset', PRESET,    # 编码速度
        '-movflags', '+faststart', # Web 优化
        '-loglevel', 'error', # 只显示错误信息
        temp_output_path      # 输出到临时文件
    ]

    try:
        subprocess.run(cmd, check=True)
        
        new_size = get_size_mb(temp_output_path)
        
        if os.path.exists(temp_output_path):
            # 删除原文件，重命名新文件
            os.replace(temp_output_path, input_path)
            
            reduction = original_size - new_size
            print(f"✅ 成功! {original_size:.2f}MB -> {new_size:.2f}MB (节省: {reduction:.2f} MB)")
            return 1, reduction
        else:
            print(f"⚠️ 警告: 压缩后未找到文件，跳过。")
            return 0, 0

    except subprocess.CalledProcessError:
        print(f"❌ 压缩失败: {file_name}")
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)
        return 0, 0
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)
        return 0, 0

def main_process(target_path):
    print(f"🚀 开始任务: {target_path} \n")
    
    if shutil.which("ffmpeg") is None:
        print("❌ 错误: 未找到 ffmpeg。请先安装: brew install ffmpeg")
        return

    total_count = 0
    total_saved = 0

    # 逻辑分支：判断是文件还是文件夹
    if os.path.isfile(target_path):
        # === 情况 A: 输入是单个文件 ===
        if target_path.lower().endswith(VIDEO_EXTENSIONS):
            count, saved = compress_single_file(target_path)
            total_count += count
            total_saved += saved
        else:
            print("⚠️ 目标文件不是指定的视频格式。")

    elif os.path.isdir(target_path):
        # === 情况 B: 输入是文件夹 (递归扫描) ===
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.lower().endswith(VIDEO_EXTENSIONS):
                    full_path = os.path.join(root, file)
                    count, saved = compress_single_file(full_path)
                    total_count += count
                    total_saved += saved
    else:
        print(f"❌ 错误: 路径不存在 -> {target_path}")
        return

    print("-" * 30)
    print(f"🎉 全部完成！")
    print(f"共处理视频: {total_count} 个")
    print(f"共节省空间: {total_saved:.2f} MB")

if __name__ == "__main__":
    main_process(TARGET_PATH)