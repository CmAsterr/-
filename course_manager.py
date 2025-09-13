import os
import re
import json
import shutil
from datetime import datetime
import utils  # 导入通用工具模块
import sys  # 需导入sys模块

def get_courses_directory():
    """获取课程存储根目录（适配打包后环境）"""
    # 判断是否为打包后的环境（_MEIPASS是pyinstaller的临时目录标识）
    if getattr(sys, 'frozen', False):
        # 打包后：获取.exe所在目录
        base_dir = os.path.dirname(sys.executable)
    else:
        # 未打包：使用原逻辑（脚本所在目录）
        base_dir = os.path.dirname(__file__)
    
    courses_dir = os.path.join(base_dir, "courses")
    if not os.path.exists(courses_dir):
        os.makedirs(courses_dir)
    return courses_dir

def list_saved_courses():
    """列出所有已保存的课程（返回课程名称与安全目录名的映射）"""
    courses_dir = get_courses_directory()
    if not os.path.exists(courses_dir):
        return {}
    
    courses_map = {}  # key: 课程名称, value: 安全目录名
    for safe_dir in os.listdir(courses_dir):
        safe_dir_path = os.path.join(courses_dir, safe_dir)
        if os.path.isdir(safe_dir_path):
            info_path = os.path.join(safe_dir_path, "course_info.json")
            if os.path.exists(info_path):
                try:
                    with open(info_path, "r", encoding="utf-8") as f:
                        course_info = json.load(f)
                    course_name = course_info.get("name", safe_dir)
                    # 处理重复课程名称（添加时间戳后缀）
                    if course_name in courses_map:
                        created_time = course_info.get("created_at", "未知时间")
                        course_name = f"{course_name} ({created_time[:10]})"
                    courses_map[course_name] = safe_dir
                except:
                    courses_map[safe_dir] = safe_dir  # 异常情况下使用目录名
    
    return courses_map

def create_new_course(course_name):
    """创建新的课程目录结构"""
    # 处理课程名称中的特殊字符
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", course_name)
    if not safe_name:
        safe_name = f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    courses_dir = get_courses_directory()
    course_dir = os.path.join(courses_dir, safe_name)
    
    # 如果课程已存在，添加时间戳
    if os.path.exists(course_dir):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        course_dir = f"{course_dir}_{timestamp}"
    
    # 创建课程目录及子目录
    subdirs = ["blank_images", "exercise_images", "ppt_images", "subjective_images", "logs"]
    for subdir in subdirs:
        os.makedirs(os.path.join(course_dir, subdir), exist_ok=True)
    
    # 初始化课程信息文件
    course_info = {
        "name": course_name,
        "safe_name": os.path.basename(course_dir),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_opened": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "course_url": "",
        "server": "",
        "history": {
            "ppt": [],
            "exercise": [],
            "blank": [],
            "subjective": []
        },
        "stats": {
            "total_cycles": 0,
            "new_pages_detected": 0,
            "errors_occurred": 0
        }
    }
    
    with open(os.path.join(course_dir, "course_info.json"), "w", encoding="utf-8") as f:
        json.dump(course_info, f, ensure_ascii=False, indent=2)
    
    utils.log(f"已创建新课程: {course_name}（存储目录: {os.path.basename(course_dir)}）")
    return course_dir

def delete_course(course_safe_dir):
    """删除课程目录及所有数据"""
    courses_dir = get_courses_directory()
    course_dir = os.path.join(courses_dir, course_safe_dir)
    
    if not os.path.exists(course_dir):
        utils.log(f"课程目录不存在: {course_dir}")
        return False
    
    try:
        shutil.rmtree(course_dir)
        utils.log(f"已删除课程目录: {course_dir}")
        return True
    except Exception as e:
        utils.log(f"删除课程失败: {str(e)}")
        return False

def save_course_data(course_dir, course_url, server_name, history, stats):
    """保存课程数据到课程目录"""
    if not course_dir or not os.path.exists(course_dir):
        utils.log("无效的课程目录，无法保存课程数据")
        return False
    
    info_path = os.path.join(course_dir, "course_info.json")
    if not os.path.exists(info_path):
        utils.log("未找到课程信息文件，无法保存")
        return False
    
    try:
        # 读取现有信息
        with open(info_path, "r", encoding="utf-8") as f:
            course_info = json.load(f)
        
        # 更新课程信息
        course_info["last_opened"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        course_info["course_url"] = course_url
        course_info["server"] = server_name
        course_info["history"] = {
            "ppt": list(history["ppt"]),
            "exercise": list(history["exercise"]),
            "blank": list(history["blank"]),
            "subjective": list(history["subjective"])
        }
        course_info["stats"] = stats
        
        # 保存更新后的信息
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(course_info, f, ensure_ascii=False, indent=2)
        
        utils.log("课程数据已成功保存")
        return True
    except Exception as e:
        utils.log(f"保存课程数据失败: {str(e)}")
        return False

def load_course_data(course_safe_dir):
    """加载已保存的课程数据"""
    courses_dir = get_courses_directory()
    course_dir = os.path.join(courses_dir, course_safe_dir)
    
    if not os.path.exists(course_dir):
        utils.log(f"课程目录不存在: {course_dir}")
        return None, None, None, None, None
    
    info_path = os.path.join(course_dir, "course_info.json")
    if not os.path.exists(info_path):
        utils.log(f"课程信息文件不存在: {info_path}")
        return None, None, None, None, None
    
    try:
        with open(info_path, "r", encoding="utf-8") as f:
            course_info = json.load(f)
        
        # 转换历史记录为集合（便于去重）
        history = {
            "ppt": set(course_info["history"]["ppt"]),
            "exercise": set(course_info["history"]["exercise"]),
            "blank": set(course_info["history"]["blank"]),
            "subjective": set(course_info["history"]["subjective"])
        }
        
        utils.log(f"已加载课程: {course_info['name']}（创建于: {course_info['created_at']}）")
        return (course_dir, course_info["course_url"], 
                course_info["server"], history, course_info["stats"])
    except Exception as e:
        utils.log(f"加载课程数据失败: {str(e)}")
        return None, None, None, None, None

def course_management_menu():
    """课程管理菜单（支持新建/打开/删除课程）"""
    print("\n" + "="*60)
    print("                课程管理中心")
    print("="*60)
    
    saved_courses = list_saved_courses()  # 字典：课程名称 -> 安全目录名
    course_names = sorted(saved_courses.keys())
    
    if course_names:
        print("\n已保存的课程:")
        for i, course_name in enumerate(course_names, 1):
            # 获取课程信息
            safe_dir = saved_courses[course_name]
            info_path = os.path.join(get_courses_directory(), safe_dir, "course_info.json")
            last_opened = "未知"
            
            if os.path.exists(info_path):
                try:
                    with open(info_path, "r", encoding="utf-8") as f:
                        course_info = json.load(f)
                        last_opened = course_info.get("last_opened", "未知")
                except:
                    pass
                    
            print(f"  {i}. {course_name} (最后打开: {last_opened[:16]})")
    
    print("\n操作选项:")
    print("  1. 新建课程")
    if course_names:
        print("  2. 打开已有课程")
        print("  3. 删除课程")
    print("  4. 返回主菜单")
    
    while True:
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == "1":
            course_name = input("请输入新课程名称: ").strip()
            if not course_name:
                course_name = f"新课程_{datetime.now().strftime('%m%d')}"
            return create_new_course(course_name), "new"
        
        elif choice == "2" and course_names:
            while True:
                course_input = input(f"请输入要打开的课程名称 (或序号1-{len(course_names)}): ").strip()
                selected_name = None
                
                # 检查是否是序号
                try:
                    course_idx = int(course_input) - 1
                    if 0 <= course_idx < len(course_names):
                        selected_name = course_names[course_idx]
                except ValueError:
                    # 不是序号，尝试匹配课程名称
                    for name in course_names:
                        if course_input == name:
                            selected_name = name
                            break
                    if not selected_name:
                        # 尝试模糊匹配
                        matches = [name for name in course_names if course_input in name]
                        if len(matches) == 1:
                            selected_name = matches[0]
                            print(f"找到匹配课程: {selected_name}")
                        elif len(matches) > 1:
                            print(f"找到多个匹配课程: {', '.join(matches)}，请输入更精确的名称")
                            continue
                        else:
                            print(f"未找到名为 '{course_input}' 的课程，请重新输入")
                            continue
                
                if selected_name:
                    safe_dir = saved_courses[selected_name]
                    course_data = load_course_data(safe_dir)
                    if course_data[0]:  # course_dir 存在
                        return course_data[0], "open"
                    else:
                        print("课程数据加载失败，请重新选择")
                else:
                    print(f"请输入有效的课程名称或1-{len(course_names)}之间的数字")
        
        elif choice == "3" and course_names:
            while True:
                course_input = input(f"请输入要删除的课程名称 (或序号1-{len(course_names)}): ").strip()
                selected_name = None
                
                # 检查是否是序号
                try:
                    course_idx = int(course_input) - 1
                    if 0 <= course_idx < len(course_names):
                        selected_name = course_names[course_idx]
                except ValueError:
                    # 不是序号，尝试匹配课程名称
                    for name in course_names:
                        if course_input == name:
                            selected_name = name
                            break
                    if not selected_name:
                        # 尝试模糊匹配
                        matches = [name for name in course_names if course_input in name]
                        if len(matches) == 1:
                            selected_name = matches[0]
                            print(f"找到匹配课程: {selected_name}")
                        elif len(matches) > 1:
                            print(f"找到多个匹配课程: {', '.join(matches)}，请输入更精确的名称")
                            continue
                        else:
                            print(f"未找到名为 '{course_input}' 的课程，请重新输入")
                            continue
                
                if selected_name:
                    confirm = input(f"确定要删除课程 '{selected_name}' 吗？此操作不可恢复！(y/n): ").strip().lower()
                    if confirm == 'y':
                        safe_dir = saved_courses[selected_name]
                        if delete_course(safe_dir):
                            print(f"课程 '{selected_name}' 已成功删除")
                            # 重新显示课程管理菜单
                            return course_management_menu()
                        else:
                            print("删除课程失败，请重试")
                    else:
                        print("已取消删除操作")
                        break
                else:
                    print(f"请输入有效的课程名称或1-{len(course_names)}之间的数字")
        
        elif choice == "4":
            return None, "back"
        
        else:
            valid_choices = ["1", "4"]
            if course_names:
                valid_choices.extend(["2", "3"])
            print(f"输入无效，请输入 {'、'.join(valid_choices)}")
