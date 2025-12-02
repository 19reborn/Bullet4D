import os
import subprocess
import shutil

# ================= 配置区域 =================
# 目标文件夹路径 (根据你的路径修改)
# TARGET_DIR = "/Users/yiming/old_Documents/research/projects/Master_thesis/ms_thesis/cvpr_bullettime/website/bullet-time/static/videos"
TARGET_DIR = "/Users/yiming/old_Documents/research/projects/Master_thesis/ms_thesis/cvpr_bullettime/website/bullet-time/static/assets"

# 需要处理的视频后缀
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.mkv', '.avi', '.webm')

# FFmpeg 参数设置
CRF_VALUE = "25"  # 画质控制，数字越大体积越小，23-28 是网页常用范围
PRESET = "veryfast"
# ===========================================

def get_size_mb(path):
    """获取文件大小(MB)"""
    return os.path.getsize(path) / (1024 * 1024)

def compress_videos_recursive(root_dir):
    print(f"🚀 开始扫描并压缩: {root_dir} \n")
    
    # 检查 ffmpeg 是否安装
    if shutil.which("ffmpeg") is None:
        print("❌ 错误: 未在系统中找到 ffmpeg。请先安装: brew install ffmpeg")
        return

    count = 0
    saved_space = 0

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(VIDEO_EXTENSIONS):
                input_path = os.path.join(root, file)
                # 生成一个临时文件名
                temp_output_path = os.path.join(root, f"temp_{file}")
                
                # 如果发现残留的临时文件，跳过
                if file.startswith("temp_"):
                    continue

                original_size = get_size_mb(input_path)
                print(f"正在处理: {file} ({original_size:.2f} MB)...")

                # 构建 FFmpeg 命令
                # 注意：如果不想要声音（网页背景通常静音），可以在下面命令中加入 '-an' 参数，体积会更小
                cmd = [
                    'ffmpeg',
                    '-y',                 # 覆盖输出文件（如果存在）
                    '-i', input_path,     # 输入文件
                    '-vcodec', 'libx264', # 编码器
                    '-crf', CRF_VALUE,    # 画质系数
                    '-preset', PRESET,    # 编码速度
                    '-movflags', '+faststart', # Web 优化 (元数据前置)
                    '-loglevel', 'error', # 减少控制台输出，只显示错误
                    temp_output_path      # 输出到临时文件
                ]

                try:
                    # 执行命令
                    subprocess.run(cmd, check=True)
                    
                    # 获取新文件大小
                    new_size = get_size_mb(temp_output_path)
                    
                    # 只有当压缩成功且文件存在时，才进行替换
                    if os.path.exists(temp_output_path):
                        # 删除原文件，重命名新文件
                        os.replace(temp_output_path, input_path)
                        
                        reduction = original_size - new_size
                        saved_space += reduction
                        print(f"✅ 成功! {original_size:.2f}MB -> {new_size:.2f}MB (节省: {reduction:.2f} MB)")
                        count += 1
                    else:
                        print(f"⚠️ 警告: 压缩后未找到文件 {temp_output_path}，跳过替换。")

                except subprocess.CalledProcessError as e:
                    print(f"❌ 压缩失败: {file}")
                    # 清理可能生成的临时文件
                    if os.path.exists(temp_output_path):
                        os.remove(temp_output_path)
                except Exception as e:
                    print(f"❌ 发生未知错误: {e}")
                    if os.path.exists(temp_output_path):
                        os.remove(temp_output_path)

    print("-" * 30)
    print(f"🎉 全部完成！")
    print(f"共处理视频: {count} 个")
    print(f"共节省空间: {saved_space:.2f} MB")

if __name__ == "__main__":
    if os.path.exists(TARGET_DIR):
        compress_videos_recursive(TARGET_DIR)
    else:
        print(f"❌ 找不到路径: {TARGET_DIR}")