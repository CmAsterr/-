import os
import time
import requests
from datetime import datetime

def init_directories(course_dir=None):
    """初始化所需的目录结构（支持课程目录）"""
    if course_dir:
        # 使用课程特定目录
        dirs = ["blank_images", "exercise_images", "ppt_images", "subjective_images", "logs"]
        for dir_name in dirs:
            dir_path = os.path.join(course_dir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                log(f"[调试] 创建课程目录: {dir_path}")
        return course_dir
    else:
        # 使用默认目录
        dirs = ["courses", "logs"]
        for dir_name in dirs:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                log(f"[调试] 创建默认目录: {dir_name}")
        return os.path.dirname(__file__)

def log(message, course_dir=None):
    """记录调试信息到控制台和日志文件（支持课程特定日志）"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)  # 控制台输出
    
    # 确定日志文件路径
    if course_dir and os.path.exists(course_dir):
        log_dir = os.path.join(course_dir, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_path = os.path.join(log_dir, "monitor.log")
    else:
        log_path = os.path.join("logs", "monitor.log")
    
    # 写入日志文件
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def download_image(src, course_dir, page_type, page_number):
    """下载图片并保存到课程对应目录"""
    try:
        if not src or not course_dir:
            log("图片src为空或课程目录无效，无法下载")
            return None
            
        # 处理URL特殊字符和协议头
        src = src.replace("&amp;", "&")
        if src.startswith("//"):
            src = "https:" + src
        log(f"开始下载{page_type}图片: {src[:100]}...")
        
        # 确定图片保存目录
        dir_mapping = {
            "ppt": "ppt_images",
            "exercise": "exercise_images",
            "blank": "blank_images",
            "subjective": "subjective_images"
        }
        img_dir = dir_mapping.get(page_type, "other_images")
        save_dir = os.path.join(course_dir, img_dir)
        os.makedirs(save_dir, exist_ok=True)
        
        # 请求头（模拟浏览器）
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.67",
            "Referer": "https://changjiang.yuketang.cn/",
            "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        }
        
        # 带重试的下载
        retry_count = 2
        response = None
        for i in range(retry_count + 1):
            try:
                response = requests.get(src, headers=headers, timeout=15, stream=True)
                response.raise_for_status()  # 抛出HTTP错误
                break
            except Exception as e:
                if i == retry_count:
                    log(f"图片下载重试失败（{retry_count+1}次）: {str(e)}")
                    return None
                log(f"图片下载失败，正在重试（{i+1}/{retry_count+1}）: {str(e)}")
                time.sleep(2)
        
        # 确定图片格式
        content_type = response.headers.get("Content-Type", "image/jpeg")
        if "png" in content_type:
            ext = "png"
        elif "gif" in content_type:
            ext = "gif"
        elif "svg" in content_type:
            ext = "svg"
        else:
            ext = "jpg"
        
        # 生成文件名（包含时间戳防重复）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_type}_{page_number}_{timestamp}.{ext}"
        file_path = os.path.join(save_dir, filename)
        
        # 保存图片
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        # 记录下载结果
        file_size = round(os.path.getsize(file_path)/1024, 2)
        log(f"图片下载成功: {file_path}（大小：{file_size}KB）")
        return file_path
        
    except Exception as e:
        log(f"图片下载异常: {str(e)}")
        return None
