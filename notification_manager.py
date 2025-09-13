import os
import json
import requests
import base64
import hashlib
from datetime import datetime
from plyer import notification
import utils  # 导入通用通用工具模块
import threading  # 新增：导入线程模块

def send_system_notification(title, message):
    """发送系统通知（Windows/macOS/Linux）"""
    try:
        full_title = f"雨课堂监控 | {title}"
        formatted_msg = message.replace("|", "\n")  # 格式化消息内容
        notification.notify(
            title=full_title,
            message=formatted_msg,
            app_name="雨课堂页面监控工具",
            timeout=10  # 通知显示10秒
        )
        utils.log(f"已发送系统通知: {full_title}")
    except Exception as e:
        utils.log(f"系统通知发送失败: {str(e)}（可能是系统通知权限未开启）")

def image_to_base64(image_path):
    """将图片转为base64编码和md5值（用于企业微信图片消息）"""
    try:
        if not os.path.exists(image_path):
            utils.log(f"图片文件不存在: {image_path}")
            return None, None
            
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        # 计算base64编码
        base64_str = base64.b64encode(image_data).decode('utf-8')
        
        # 计算md5值
        md5_hash = hashlib.md5()
        md5_hash.update(image_data)
        md5_str = md5_hash.hexdigest()
        
        return base64_str, md5_str
        
    except Exception as e:
        utils.log(f"图片处理失败: {str(e)}")
        return None, None

def send_wechat_image(webhook_url, image_path):
    """发送图片到企业微信群"""
    if not webhook_url:
        utils.log("未配置企业微信WebHook，无法发送图片")
        return False
        
    # 处理图片
    base64_str, md5_str = image_to_base64(image_path)
    if not base64_str or not md5_str:
        return False
    
    # 构建图片消息格式
    message = {
        "msgtype": "image",
        "image": {
            "base64": base64_str,
            "md5": md5_str
        }
    }
    
    try:
        response = requests.post(
            url=webhook_url,
            data=json.dumps(message),
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        result = response.json()
        if result.get("errcode") == 0:
            utils.log(f"图片消息发送成功（文件：{os.path.basename(image_path)}）")
            return True
        else:
            utils.log(f"图片消息发送失败：{result.get('errmsg')}（错误码：{result.get('errcode')}）")
            return False
            
    except Exception as e:
        utils.log(f"图片消息发送异常：{str(e)}")
        return False

def send_wechat_text(webhook_url, title, content):
    """发送普通文本消息到企业微信群"""
    if not webhook_url:
        utils.log("未配置企业微信WebHook，无法发送通知")
        return False
        
    # 构建文本消息格式
    message = {
        "msgtype": "text",
        "text": {
            "content": f"{title}\n\n检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n详细信息：{content}\n来源：雨课堂页面监控工具"
        }
    }
    
    try:
        response = requests.post(
            url=webhook_url,
            data=json.dumps(message, ensure_ascii=False),
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=10
        )
        
        result = response.json()
        if result.get("errcode") == 0:
            utils.log(f"文本消息发送成功（标题：{title}）")
            return True
        else:
            utils.log(f"文本消息发送失败：{result.get('errmsg')}（错误码：{result.get('errcode')}）")
            return False
            
    except Exception as e:
        utils.log(f"文本消息发送异常：{str(e)}")
        return False

def send_wechat_notification(webhook_url, title, content, image_path=None, is_ai=False):
    """发送微信通知（支持文本+图片，新增AI类型标识）"""
    if not webhook_url:
        return False
        
    # 构建AI相关消息前缀
    ai_prefix = "[AI内容] " if is_ai else ""
    
    # 启动线程发送文本消息（添加AI标识）
    text_thread = threading.Thread(
        target=send_wechat_text,
        args=(webhook_url, f"{ai_prefix}{title}", content)
    )
    text_thread.start()
    
    # 启动线程发送图片（如果有）
    image_success = True
    if image_path and os.path.exists(image_path):
        image_thread = threading.Thread(
            target=send_wechat_image,
            args=(webhook_url, image_path)
        )
        image_thread.start()
        # 等待图片线程完成并获取结果
        image_thread.join()
        image_success = image_thread.is_alive() is False  # 检查线程是否正常结束
    
    # 等待文本线程完成并获取结果
    text_thread.join()
    text_success = text_thread.is_alive() is False
    
    return text_success and image_success

def send_ai_notification(webhook_url, title, content, image_path=None):
    """专门用于发送AI相关内容的通知（系统通知+微信通知）"""
    # 启动线程发送系统通知（添加AI标识）
    system_thread = threading.Thread(
        target=send_system_notification,
        args=(f"AI内容 | {title}", content)
    )
    system_thread.start()
    
    # 启动线程发送企业微信通知（标记为AI内容）
    wechat_success = True
    if webhook_url:
        wechat_thread = threading.Thread(
            target=send_wechat_notification,
            args=(webhook_url, title, content, image_path, True)
        )
        wechat_thread.start()
        wechat_thread.join()
        wechat_success = wechat_thread.is_alive() is False
    
    # 等待系统通知线程完成
    system_thread.join()
    system_success = system_thread.is_alive() is False
    
    return system_success and wechat_success
