import os
import sys
import time
import re
from datetime import datetime
from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver.common.by import By

# 导入自定义模块
import course_manager
import config_manager
import browser_manager
import notification_manager
import ai_manager
import utils
import threading

def main():
    # 初始化默认目录（logs、courses）
    utils.init_directories()
    utils.log("="*60)
    utils.log("         雨课堂页面更新检测工具（V3版·课程管理）")
    utils.log("="*60)
    
    # 主菜单交互
    while True:
        print("\n" + "="*60)
        print("                主菜单")
        print("="*60)
        print("1. 课程管理（新建/打开/删除课程）")
        print("2. 配置工具选项")
        print("3. 退出程序")
        
        main_choice = input("\n请选择操作 (1-3): ").strip()
        
        if main_choice == "3":
            utils.log("用户选择退出程序")
            print("程序已退出，感谢使用！")
            return
        
        elif main_choice == "2":
            # 配置管理流程
            utils.log("进入配置工具选项")
            if os.path.exists("config.ini"):
                loaded_config = config_manager.load_config()
                user_config = config_manager.confirm_or_modify_config(loaded_config)
            else:
                print("未找到配置文件，将创建新配置")
                user_config = config_manager.get_user_config()
            config_manager.save_config(user_config)
            print("配置已保存，返回主菜单")
            continue
        
        elif main_choice == "1":
            # 课程管理流程
            utils.log("进入课程管理")
            course_dir, action = course_manager.course_management_menu()
            
            if action == "back":
                utils.log("用户选择返回主菜单")
                continue
                
            if not course_dir:
                utils.log("未获取到有效课程目录")
                continue
            
            break
        
        else:
            print("输入无效，请输入1-3之间的数字")
    
    # 启动前环境检查
    utils.log("\n【启动前环境检查】")
    # 1. Python版本检查
    if sys.version_info < (3, 7):
        utils.log("[错误] Python版本过低（需3.7及以上），当前版本: " + sys.version)
        print("请升级Python版本后重新运行")
        return
    utils.log(f"Python版本检查通过: {sys.version.split()[0]}")
    
    # 2. 依赖库检查
    required_libs = ["selenium", "requests", "plyer"]
    missing_libs = []
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            missing_libs.append(lib)
    if missing_libs:
        utils.log(f"[错误] 缺少必要依赖库: {', '.join(missing_libs)}")
        print(f"请执行以下命令安装依赖：")
        print(f"pip install {' '.join(missing_libs)}")
        return
    utils.log("依赖库检查通过（所有必要库已安装）")
    
    # 3. Edge驱动检查
    driver_path = os.path.join(os.path.dirname(__file__), "msedgedriver.exe")
    if not os.path.exists(driver_path):
        utils.log(f"[警告] 未在当前目录找到Edge驱动: {driver_path}")
        print("请下载对应版本的Edge驱动并放在程序同一目录下")
        print("驱动下载地址: https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/")
        while True:
            continue_choice = input("是否继续运行？(y=继续, n=退出): ").strip().lower()
            if continue_choice == "n":
                return
            elif continue_choice == "y":
                utils.log("用户选择继续运行，后续可能因驱动问题报错")
                break
            else:
                print("输入无效！请输入y或n")
    
    # 4. 浏览器与驱动兼容性检查
    if not browser_manager.check_edge_compatibility():
        utils.log("【兼容性检查未通过】")
        print("请根据上述提示解决浏览器与驱动版本问题后重新运行")
        while True:
            force_run = input("是否强制继续运行？(y=强制, n=退出): ").strip().lower()
            if force_run == "n":
                return
            elif force_run == "y":
                utils.log("用户选择强制运行，可能出现兼容性错误")
                break
            else:
                print("输入无效！请输入y或n")
    
    # 加载配置与课程数据
    utils.log("\n【配置文件处理】")
    user_config = config_manager.load_config()
    
    # 初始化课程专属目录（图片/日志子目录）
    utils.init_directories(course_dir)
    
    # 加载已有课程数据（仅打开课程时）
    course_url = None
    server_name = user_config['server']['name']
    history = {
        "ppt": set(),
        "exercise": set(),
        "blank": set(),
        "subjective": set()
    }
    stats = {
        "total_cycles": 0,
        "new_pages_detected": 0,
        "errors_occurred": 0
    }
    
    if action == "open":
        course_dir, course_url, server_name, history, stats = course_manager.load_course_data(
            os.path.basename(course_dir)
        )
    
    # 初始化浏览器
    utils.log("\n【初始化浏览器】")
    driver = browser_manager.init_browser()
    if not driver:
        utils.log("浏览器初始化失败，尝试重新初始化...")
        driver = browser_manager.init_browser()  # 重试1次
        if not driver:
            utils.log("【错误】浏览器初始化失败（共2次尝试），程序退出")
            return
    
    # 登录与课程URL确认
    try:
        utils.log("\n【登录与课程准备】")
        # 复用已保存的课程URL
        if course_url and input(f"使用已保存的课程URL? {course_url} (y/n): ").strip().lower() == "y":
            utils.log(f"使用已保存的课程URL: {course_url}")
        else:
            # 1. 访问登录页
            login_url = f"{user_config['server']['base_url']}/web"
            utils.log(f"步骤1/3：访问{user_config['server']['name']}登录页面: {login_url}")
            driver.get(login_url)
            time.sleep(4)
            
            # 2. 等待用户扫码登录
            input("步骤2/3：请在浏览器中完成扫码登录，登录成功后按回车键继续...")
            
            # 3. 等待用户导航到课程页
            input("步骤3/3：请在浏览器中打开需要监控的课程页面（全屏/章节页），准备就绪后按回车键继续...")
            
            # 4. 获取当前活动窗口URL
            current_url = browser_manager.get_active_tab_url(driver)
            if not current_url:
                # 手动输入URL
                while True:
                    course_input = input("无法自动获取URL，请手动输入课程URL: ").strip()
                    if course_input.startswith("http") and user_config['server']['base_url'] in course_input and "lesson" in course_input:
                        course_url = course_input
                        break
                    print(f"URL格式无效！需包含{user_config['server']['base_url']}和'lesson'")
            else:
                # 提取课程ID并生成标准URL
                course_id = browser_manager.extract_course_id(current_url)
                if course_id:
                    course_url = f"{user_config['server']['base_url']}/lesson/fullscreen/v3/{course_id}"
                else:
                    course_url = current_url
            
            # 5. 确认URL
            while True:
                confirm_url = input(f"\n课程网址: {course_url}\n是否使用该URL？(y=是, n=手动修改): ").strip().lower()
                if confirm_url == "y":
                    utils.log(f"用户确认使用课程URL: {course_url}")
                    break
                elif confirm_url == "n":
                    while True:
                        manual_url = input("请输入正确的课程URL: ").strip()
                        if manual_url.startswith("http") and "lesson" in manual_url:
                            course_url = manual_url
                            utils.log(f"用户手动输入课程URL: {course_url}")
                            break
                        print("URL格式无效！需包含'lesson'")
                    break
                else:
                    print("输入无效！请输入y或n")
        
    except Exception as e:
        utils.log(f"[错误] 登录与课程准备失败: {str(e)}")
        if driver:
            driver.quit()
        return
    
    # 监控主循环
    try:
        utils.log("\n" + "="*60)
        utils.log("          开始进入监控循环（按Ctrl+C停止）")
        utils.log("="*60)
        utils.log(f"监控配置: 常规间隔={user_config['timing']['normal_interval']}s | 快速间隔={user_config['timing']['rapid_interval']}s")
        utils.log(f"          快速阈值={user_config['timing']['threshold']}s | 刷新设置={'启用' if user_config['refresh'] else '禁用'}")
        utils.log(f"          AI分析: {'启用' if user_config['ai']['enable'] else '禁用'} | OCR: {'已配置' if (user_config['ocr']['apikey'] and user_config['ocr']['secretkey']) else '未配置'}")
        utils.log(f"          课程目录: {course_dir}")
        utils.log("="*60 + "\n")
        
        # 监控参数初始化
        interval_time = user_config['timing']['normal_interval']  # 当前检测间隔
        rapid_mode_start = 0  # 快速模式启动时间（0表示未启用）
        last_succ_detect = time.time()  # 上次成功检测时间
        max_consec_errors = 3  # 最大连续错误次数
        consec_errors = 0  # 当前连续错误次数
        wechat_hook = user_config['wechat']['webhook_url']  # 企业微信WebHook
        
        while True:
            # 更新统计信息
            stats["total_cycles"] += 1
            current_cycle = stats["total_cycles"]
            cycle_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 日志记录周期信息
            utils.log(f"\n[检测周期 {current_cycle}] 开始时间: {cycle_time}")
            utils.log(f"当前状态: 间隔={interval_time}s | 快速模式={'已启用' if rapid_mode_start else '未启用'}")
            utils.log(f"性能统计: 新页面={stats['new_pages_detected']} | 错误数={stats['errors_occurred']} | 连续错误={consec_errors}")
            
            # 定期保存课程数据（每10个周期）
            if current_cycle % 10 == 0:
                course_manager.save_course_data(course_dir, course_url, server_name, history, stats)
            
            # 3分钟未成功检测，强制重连浏览器
            if time.time() - last_succ_detect > 3 * 60:
                utils.log("【警告】已超过3分钟未成功检测，尝试重连浏览器...")
                if driver:
                    driver.quit()
                driver = browser_manager.reconnect_browser(course_url)
                consec_errors = 0
            
            # 浏览器未连接，尝试重连
            if not driver:
                driver = browser_manager.reconnect_browser(course_url)
                if not driver:
                    utils.log(f"无法重新连接浏览器，{interval_time}秒后重试...")
                    time.sleep(interval_time)
                    continue
            
            try:
                # 按配置刷新页面
                if user_config['refresh']:
                    utils.log("执行页面刷新操作...")
                    browser_manager.handle_all_alerts(driver)  # 处理刷新前弹窗
                    driver.get(course_url)
                    time.sleep(3)  # 等待页面加载
                    browser_manager.handle_all_alerts(driver)  # 处理刷新后弹窗
                    utils.log("页面刷新完成")
                
                # 获取当前页面URL
                current_page_url = browser_manager.get_active_tab_url(driver)
                if not current_page_url:
                    utils.log("无法获取当前页面URL")
                    consec_errors += 1
                    stats["errors_occurred"] += 1
                    
                    # 连续错误达到阈值，重连浏览器
                    if consec_errors >= max_consec_errors:
                        utils.log(f"连续错误次数达到{max_consec_errors}次，触发浏览器重连...")
                        driver = browser_manager.reconnect_browser(course_url)
                        consec_errors = 0
                    
                    time.sleep(interval_time)
                    continue
                
                utils.log(f"当前页面URL: {current_page_url}")
                
                # 识别页面类型（PPT/选择题/填空题/主观题）和页面编号
                page_type, page_number = None, None
                page_patterns = {
                    "ppt": r"/ppt/(\d+)",
                    "exercise": r"/exercise/(\d+)",
                    "blank": r"/blank/(\d+)",
                    "subjective": r"/subjective/(\d+)"
                }
                for ptype, pattern in page_patterns.items():
                    match = re.search(pattern, current_page_url)
                    if match:
                        page_type = ptype
                        page_number = match.group(1)
                        break
                
                # 未识别到监控页面类型（如课程目录页）
                if not (page_type and page_number):
                    utils.log("未识别到已知页面类型（可能在课程目录页）")
                    consec_errors = 0
                    last_succ_detect = time.time()
                    time.sleep(interval_time)
                    continue
                
                utils.log(f"识别到页面类型: {page_type}，编号: {page_number}")
                
                # 判断是否为新页面+是否需要监控（下载/通知）
                is_new_page = page_number not in history[page_type]
                is_monitored_page = (user_config['page_settings'][page_type]['notify'] or 
                                    user_config['page_settings'][page_type]['download'])
                
                if is_monitored_page and is_new_page:
                    # 1. 进入快速模式
                    rapid_mode_start = time.time()
                    interval_time = user_config['timing']['rapid_interval']
                    utils.log(f"检测到新{page_type}页面，进入快速模式（间隔{interval_time}秒）")
                    
                    # 2. 更新历史记录与统计
                    history[page_type].add(page_number)
                    stats["new_pages_detected"] += 1
                    
                    # 3. 定位页面元素并下载图片（按配置）
                    image_path = None
                    try:
                        # 定位页面核心元素
                        base_element = browser_manager.locate_page_element(driver, page_type, user_config['xpaths'])
                        if base_element:
                            # 查找图片元素
                            img_elements = base_element.find_elements(By.TAG_NAME, "img")
                            if img_elements:
                                img_src = img_elements[0].get_attribute("src") or img_elements[0].get_attribute("data-src")
                                if img_src:
                                    utils.log(f"获取到{page_type}页面图片资源: {img_src[:100]}...")
                                    # 按配置下载图片
                                    if user_config['page_settings'][page_type]['download']:
                                        image_path = utils.download_image(img_src, course_dir, page_type, page_number)
                    
                    except Exception as e:
                        utils.log(f"{page_type}页面元素处理异常: {str(e)}")
                        stats["errors_occurred"] += 1
                    
                    # 4. 发送通知（系统通知+微信通知）
                    if user_config['page_settings'][page_type]['notify']:
                        # 发送系统通知
                        
                        notification_manager.send_system_notification(
                            title=f"新{page_type}页面",
                            message=f"编号: {page_number}\n时间: {cycle_time}\n课程URL: {course_url}"
                        )
                        
                        # 发送企业微信通知（按配置）
                        if wechat_hook:
                            page_name_map = {
                                "ppt": "PPT",
                                "exercise": "选择题",
                                "blank": "填空题",
                                "subjective": "主观题"
                            }
                            notification_manager.send_wechat_notification(
                                webhook_url=wechat_hook,
                                title=f"新{page_name_map[page_type]}页面提醒",
                                content=f"页面编号：{page_number}\n课程URL：{course_url}",
                                image_path=image_path
                            )
                    # 5. 用 ai 解答
                    if user_config['ai']['enable']:
                        def ai_process_and_notify(ocr_config, ai_config, image_path, wechat_hook, page_type):
                            ai_answer = ai_manager.get_ai_answer(
                                ocr_config=ocr_config,
                                ai_config=ai_config,
                                image_path=image_path
                            )
                            
                            if wechat_hook:
                                notification_manager.send_ai_notification(
                                    webhook_url=wechat_hook,
                                    title=f"新{page_name_map[page_type]}页面分析",
                                    content=ai_answer
                                    )
                        
                        ai_thread = threading.Thread(
                            target=ai_process_and_notify,
                            kwargs={
                                "ocr_config": user_config['ocr'],
                                "ai_config": user_config['ai'],
                                "image_path": image_path,
                                "wechat_hook": wechat_hook,
                                "page_type": page_type  # 传递当前页面类型（如"exercise"）
                            }
                        )
                        ai_thread.daemon = True  # 设为守护线程，主程序退出时自动关闭
                        ai_thread.start()  # 启动线程（异步执行，不阻塞主循环）
                
                elif is_monitored_page and not is_new_page:
                    # 快速模式超时判断（恢复常规间隔）
                    if rapid_mode_start and (time.time() - rapid_mode_start) > user_config['timing']['threshold']:
                        interval_time = user_config['timing']['normal_interval']
                        utils.log(f"快速模式已持续{(time.time() - rapid_mode_start):.1f}秒（超过阈值{user_config['timing']['threshold']}秒），恢复常规间隔{interval_time}秒")
                        rapid_mode_start = 0
                    elif rapid_mode_start:
                        utils.log(f"快速模式持续中（{(time.time() - rapid_mode_start):.1f}秒），保持间隔{interval_time}秒")
                
                else:
                    utils.log(f"当前页面类型({page_type})未配置监控，保持间隔{interval_time}秒")
                
                # 重置错误计数与检测时间
                consec_errors = 0
                last_succ_detect = time.time()
                browser_manager.handle_all_alerts(driver)
                
                # 等待下一个检测周期
                utils.log(f"检测周期{current_cycle}完成，{interval_time}秒后进行下一次检测...")
                time.sleep(interval_time)
            
            except InvalidSessionIdException:
                utils.log("【错误】浏览器会话已失效（可能已关闭）")
                consec_errors += 1
                stats["errors_occurred"] += 1
                driver = browser_manager.reconnect_browser(course_url)
                time.sleep(interval_time)
            
            except Exception as e:
                utils.log(f"【错误】检测周期中发生异常: {str(e)}")
                consec_errors += 1
                stats["errors_occurred"] += 1
                if consec_errors >= max_consec_errors:
                    utils.log(f"连续错误次数达到{max_consec_errors}次，触发重新连接...")
                    driver = browser_manager.reconnect_browser(course_url)
                    consec_errors = 0
                time.sleep(interval_time)
    
    except KeyboardInterrupt:
        utils.log("\n【用户操作】检测到Ctrl+C，手动终止程序")
    
    except Exception as e:
        utils.log(f"【严重错误】监控主循环异常终止: {str(e)}")
        import traceback
        utils.log(f"异常堆栈: {traceback.format_exc()}")
    
    finally:
        # 退出前保存课程数据
        course_manager.save_course_data(course_dir, course_url, server_name, history, stats)
        
        # 输出统计信息
        utils.log("\n" + "="*60)
        utils.log("          监控程序结束 - 统计信息")
        utils.log("="*60)
        utils.log(f"总检测周期: {stats['total_cycles']}次")
        utils.log(f"检测到新页面: {stats['new_pages_detected']}个")
        utils.log(f"发生错误次数: {stats['errors_occurred']}次")
        utils.log(f"PPT页面历史: {len(history['ppt'])}个")
        utils.log(f"选择题页面历史: {len(history['exercise'])}个")
        utils.log(f"填空题页面历史: {len(history['blank'])}个")
        utils.log(f"主观题页面历史: {len(history['subjective'])}个")
        utils.log(f"课程数据已保存至: {course_dir}")
        utils.log("="*60)
        
        # 关闭浏览器
        if driver:
            try:
                browser_manager.handle_all_alerts(driver)
                driver.quit()
                utils.log("浏览器已成功关闭")
            except Exception as e:
                utils.log(f"关闭浏览器时发生错误: {str(e)}")
        
        print("\n程序已退出，详细日志请查看课程目录下的 logs/monitor.log 文件")

if __name__ == "__main__":
    main()
