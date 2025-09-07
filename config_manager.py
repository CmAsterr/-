import os
import configparser
import utils  # 导入通用工具模块

def get_default_config():
    """返回默认配置结构"""
    return {
        "server": {
            "name": "长江雨课堂",
            "base_url": "https://changjiang.yuketang.cn"
        },
        "timing": {
            "normal_interval": 20,          # 常规检测间隔（秒）
            "threshold": 60,                # 快速模式阈值（秒）
            "rapid_interval": 5             # 快速检测间隔（秒）
        },
        "refresh": True,                   # 每次检测前是否刷新页面
        "wechat": {
            "webhook_url": ""               # 企业微信机器人WebHook地址
        },
        "page_settings": {
            "ppt": {"download": False, "notify": False},
            "exercise": {"download": True, "notify": True},
            "blank": {"download": True, "notify": True},
            "subjective": {"download": True, "notify": True}
        },
        "xpaths": {
            "ppt": '//*[@id="app"]/section/section[1]/section[2]/section/section/section/section[1]/section/div/section/section',
            "exercise": '//*[@id="app"]/section/section[1]/section[2]/section/section/section/section[1]/section/section/section/section',
            "blank": '//*[@id="app"]/section/section[1]/section[2]/section/section/section/section[1]/section/div/section/section',
            "subjective": '//*[@id="app"]/section/section[1]/section[2]/section/section/section/section[1]/section/section[1]/div/section/section'
        },
        "ai": {
            "enable": True,  # 默认启用AI分析
            "apikey": "",
            "base_url": "",
            "model": ""
        },
        "ocr": {
            "apikey": "",
            "secretkey": ""
        }
    }

def load_config():
    """从 config.ini 加载配置，加载失败则返回默认配置"""
    config_parser = configparser.ConfigParser()
    default_config = get_default_config()

    if not os.path.exists("config.ini"):
        utils.log("未找到配置文件，使用默认配置")
        return default_config

    try:
        config_parser.read("config.ini", encoding="utf-8")
        # 解析服务器配置
        server_config = {
            "name": config_parser.get("Server", "name"),
            "base_url": config_parser.get("Server", "base_url")
        }
        # 解析时间配置（整数转换）
        timing_config = {
            "normal_interval": config_parser.getint("Timing", "normal_interval"),
            "threshold": config_parser.getint("Timing", "threshold"),
            "rapid_interval": config_parser.getint("Timing", "rapid_interval")
        }
        # 解析刷新配置（布尔转换）
        refresh_config = config_parser.getboolean("Refresh", "enable")
        # 解析微信配置
        wechat_config = {
            "webhook_url": config_parser.get("WeChat", "webhook_url", fallback="")
        }
        # 解析页面检测配置（布尔转换）
        page_settings_config = {
            "ppt": {
                "download": config_parser.getboolean("PageSettings", "ppt_download"),
                "notify": config_parser.getboolean("PageSettings", "ppt_notify")
            },
            "exercise": {
                "download": config_parser.getboolean("PageSettings", "exercise_download"),
                "notify": config_parser.getboolean("PageSettings", "exercise_notify")
            },
            "blank": {
                "download": config_parser.getboolean("PageSettings", "blank_download"),
                "notify": config_parser.getboolean("PageSettings", "blank_notify")
            },
            "subjective": {
                "download": config_parser.getboolean("PageSettings", "subjective_download"),
                "notify": config_parser.getboolean("PageSettings", "subjective_notify")
            }
        }
        # 解析 XPath 配置
        xpaths_config = {
            "ppt": config_parser.get("XPaths", "ppt"),
            "exercise": config_parser.get("XPaths", "exercise"),
            "blank": config_parser.get("XPaths", "blank"),
            "subjective": config_parser.get("XPaths", "subjective")
        }
        
        # 解析AI配置
        ai_config = {
            "enable": config_parser.getboolean("AI", "enable", fallback=True),
            "apikey": config_parser.get("AI", "apikey", fallback=""),
            "base_url": config_parser.get("AI", "base_url", fallback=""),
            "model": config_parser.get("AI", "model", fallback="")
        }
        
        # 解析OCR配置
        ocr_config = {
            "apikey": config_parser.get("OCR", "apikey", fallback=""),
            "secretkey": config_parser.get("OCR", "secretkey", fallback="")
        }

        # 组装加载后的配置
        loaded_config = {
            "server": server_config,
            "timing": timing_config,
            "refresh": refresh_config,
            "wechat": wechat_config,
            "page_settings": page_settings_config,
            "xpaths": xpaths_config,
            "ai": ai_config,
            "ocr": ocr_config
        }
        utils.log("配置文件加载成功")
        return loaded_config

    except Exception as e:
        utils.log(f"配置文件解析失败（格式错误）: {str(e)}，使用默认配置")
        return default_config

def save_config(config):
    """将配置保存到 config.ini 文件"""
    config_parser = configparser.ConfigParser()

    # 写入服务器配置
    config_parser["Server"] = {
        "name": config["server"]["name"],
        "base_url": config["server"]["base_url"]
    }

    # 写入时间配置
    config_parser["Timing"] = {
        "normal_interval": str(config["timing"]["normal_interval"]),
        "threshold": str(config["timing"]["threshold"]),
        "rapid_interval": str(config["timing"]["rapid_interval"])
    }

    # 写入刷新配置
    config_parser["Refresh"] = {
        "enable": str(config["refresh"]).lower()
    }

    # 写入微信配置
    config_parser["WeChat"] = {
        "webhook_url": config["wechat"]["webhook_url"]
    }

    # 写入页面检测配置
    config_parser["PageSettings"] = {
        "ppt_download": str(config["page_settings"]["ppt"]["download"]).lower(),
        "ppt_notify": str(config["page_settings"]["ppt"]["notify"]).lower(),
        "exercise_download": str(config["page_settings"]["exercise"]["download"]).lower(),
        "exercise_notify": str(config["page_settings"]["exercise"]["notify"]).lower(),
        "blank_download": str(config["page_settings"]["blank"]["download"]).lower(),
        "blank_notify": str(config["page_settings"]["blank"]["notify"]).lower(),
        "subjective_download": str(config["page_settings"]["subjective"]["download"]).lower(),
        "subjective_notify": str(config["page_settings"]["subjective"]["notify"]).lower()
    }

    # 写入 XPath 配置
    config_parser["XPaths"] = {
        "ppt": config["xpaths"]["ppt"],
        "exercise": config["xpaths"]["exercise"],
        "blank": config["xpaths"]["blank"],
        "subjective": config["xpaths"]["subjective"]
    }
    
    # 写入AI配置
    config_parser["AI"] = {
        "enable": str(config["ai"]["enable"]).lower(),
        "apikey": config["ai"]["apikey"],
        "base_url": config["ai"]["base_url"],
        "model": config["ai"]["model"]
    }
    
    # 写入OCR配置
    config_parser["OCR"] = {
        "apikey": config["ocr"]["apikey"],
        "secretkey": config["ocr"]["secretkey"]
    }

    # 保存到文件
    with open("config.ini", "w", encoding="utf-8") as f:
        config_parser.write(f)
    utils.log("配置已保存到 config.ini")

def confirm_or_modify_config(loaded_config):
    """展示加载的配置，让用户确认或修改"""
    print("\n" + "="*60)
    print("                加载的配置信息（可修改）")
    print("="*60)
    
    # 展示当前配置
    print(f"\n1. 服务器配置:")
    print(f"   - 名称: {loaded_config['server']['name']}")
    print(f"   - 基础URL: {loaded_config['server']['base_url']}")
    
    print(f"\n2. 时间配置:")
    print(f"   - 常规检测间隔: {loaded_config['timing']['normal_interval']} 秒")
    print(f"   - 快速模式阈值: {loaded_config['timing']['threshold']} 秒")
    print(f"   - 快速检测间隔: {loaded_config['timing']['rapid_interval']} 秒")
    
    print(f"\n3. 刷新配置:")
    print(f"   - 每次检测前刷新页面: {'是' if loaded_config['refresh'] else '否'}")
    
    # 展示微信配置
    print(f"\n4. 微信消息配置:")
    wechat_hook = loaded_config['wechat']['webhook_url']
    print(f"   - 企业微信机器人WebHook: {'已配置' if wechat_hook else '未配置'}（显示前30字符：{wechat_hook[:30]}...）")
    
    print(f"\n5. 页面检测配置:")
    for page_type, settings in loaded_config['page_settings'].items():
        page_name = {
            "ppt": "PPT页面",
            "exercise": "选择题页面",
            "blank": "填空题页面",
            "subjective": "主观题页面"
        }.get(page_type, page_type)
        print(f"   - {page_name}: 下载图片={'是' if settings['download'] else '否'}, 发送通知={'是' if settings['notify'] else '否'}")
    
    print(f"\n6. XPath配置（过长仅展示前50字符）:")
    for page_type, xpath in loaded_config['xpaths'].items():
        page_name = {
            "ppt": "PPT页面",
            "exercise": "选择题页面",
            "blank": "填空题页面",
            "subjective": "主观题页面"
        }.get(page_type, page_type)
        print(f"   - {page_name}: {xpath[:50]}..." if len(xpath) > 50 else f"   - {page_name}: {xpath}")
    
    # 展示AI分析配置
    print(f"\n7. AI分析配置:")
    print(f"   - 启用AI分析: {'是' if loaded_config['ai']['enable'] else '否'}")
    print(f"   - AI API Key: {'已配置' if loaded_config['ai']['apikey'] else '未配置'}")
    print(f"   - AI Base URL: {loaded_config['ai']['base_url']}")
    print(f"   - AI Model: {loaded_config['ai']['model']}")
    
    # 展示OCR配置
    print(f"\n8. OCR配置:")
    print(f"   - OCR API Key: {'已配置' if loaded_config['ocr']['apikey'] else '未配置'}")
    print(f"   - OCR Secret Key: {'已配置' if loaded_config['ocr']['secretkey'] else '未配置'}")
    
    # 询问用户是否修改
    while True:
        choice = input(f"\n配置是否符合需求？(y=直接使用, n=修改配置): ").strip().lower()
        if choice == "y":
            utils.log("用户确认使用当前配置")
            return loaded_config
        elif choice == "n":
            utils.log("用户选择修改配置，进入配置修改流程")
            return get_user_config()  # 调用配置修改流程
        else:
            print("输入无效！请输入 y 或 n")

def get_user_config():
    """配置输入流程，用于用户修改配置时调用"""
    config = get_default_config()
    
    print("\n" + "="*60)
    print("                雨课堂页面监控配置（修改模式）")
    print("="*60)
    
    # 1. 服务器选择
    print("\n【服务器选择】")
    servers = [
        {"id": 1, "name": "雨课堂", "base_url": "https://www.yuketang.cn"},
        {"id": 2, "name": "荷塘雨课堂", "base_url": "https://pro.yuketang.cn"},
        {"id": 3, "name": "长江雨课堂", "base_url": "https://changjiang.yuketang.cn"},
        {"id": 4, "name": "黄河雨课堂", "base_url": "https://huanghe.yuketang.cn"}
    ]
    for server in servers:
        print(f"  {server['id']}. {server['name']} - {server['base_url']}")
    
    while True:
        server_input = input(f"请选择服务器(1-{len(servers)}, 默认3): ").strip()
        if not server_input:
            selected = next(s for s in servers if s["id"] == 3)
            config["server"] = {"name": selected["name"], "base_url": selected["base_url"]}
            break
        try:
            server_id = int(server_input)
            if 1 <= server_id <= len(servers):
                selected = next(s for s in servers if s["id"] == server_id)
                config["server"] = {"name": selected["name"], "base_url": selected["base_url"]}
                break
            else:
                print(f"输入无效！请输入1-{len(servers)}之间的整数")
        except ValueError:
            print("输入无效！请输入数字")
    print(f"已选择: {config['server']['name']} ({config['server']['base_url']})")
    
    # 2. 时间配置
    print("\n【时间配置】")
    try:
        # 常规检测间隔
        while True:
            normal_input = input(f"请输入常规检测间隔时间(秒，默认{config['timing']['normal_interval']}秒): ").strip()
            if not normal_input:
                break
            normal_val = int(normal_input)
            if 1 <= normal_val <= 300:
                config['timing']['normal_interval'] = normal_val
                break
            print("输入无效！请输入1-300之间的整数")
        
        # 快速模式阈值
        while True:
            threshold_input = input(f"请输入连续页面更新检测阈值(秒，默认{config['timing']['threshold']}秒): ").strip()
            if not threshold_input:
                break
            threshold_val = int(threshold_input)
            if 10 <= threshold_val <= 300:
                config['timing']['threshold'] = threshold_val
                break
            print("输入无效！请输入10-300之间的整数")
        
        # 快速检测间隔
        while True:
            rapid_input = input(f"请输入连续出题检测时间(秒，默认{config['timing']['rapid_interval']}秒): ").strip()
            if not rapid_input:
                break
            rapid_val = int(rapid_input)
            if 1 <= rapid_val <= 60:
                config['timing']['rapid_interval'] = rapid_val
                break
            print("输入无效！请输入1-60之间的整数")
    except ValueError:
        utils.log("时间输入格式错误（需输入整数），使用默认值")
    
    # 3. 刷新配置
    print("\n【刷新配置】")
    while True:
        refresh_input = input("每次检测前是否刷新页面？(y=是, n=否, 默认y): ").strip().lower()
        if refresh_input in ["", "y", "n"]:
            config['refresh'] = refresh_input != 'n'
            break
        print("输入无效！请输入y或n")
    
    # 4. 微信消息配置
    print("\n【微信消息配置】")
    print("提示：企业微信机器人WebHook获取方式：企业微信→群聊→群机器人→添加机器人→复制WebHook")
    wechat_input = input(f"请输入企业微信机器人WebHook地址（留空则不启用微信提醒，默认空）: ").strip()
    config['wechat']['webhook_url'] = wechat_input
    print(f"微信配置已保存：{'已配置WebHook' if wechat_input else '未配置WebHook'}")
    
    # 5. 页面检测配置
    print("\n【页面检测配置】（输入y启用，n禁用，默认按提示）")
    # PPT页面
    print("\nPPT页面:")
    while True:
        ppt_download = input("检测到PPT页面后是否下载图片？(y=是, n=否, 默认n): ").strip().lower()
        if ppt_download in ["", "y", "n"]:
            config['page_settings']['ppt']['download'] = ppt_download == 'y'
            break
        print("输入无效！请输入y或n")
    while True:
        ppt_notify = input("检测到PPT页面后是否发送通知？(y=是, n=否, 默认n): ").strip().lower()
        if ppt_notify in ["", "y", "n"]:
            config['page_settings']['ppt']['notify'] = ppt_notify == 'y'
            break
        print("输入无效！请输入y或n")
    
    # 选择题页面
    print("\n选择题页面:")
    while True:
        exercise_download = input("检测到选择题页面后是否下载图片？(y=是, n=否, 默认y): ").strip().lower()
        if exercise_download in ["", "y", "n"]:
            config['page_settings']['exercise']['download'] = exercise_download != 'n'
            break
        print("输入无效！请输入y或n")
    while True:
        exercise_notify = input("检测到选择题页面后是否发送通知？(y=是, n=否, 默认y): ").strip().lower()
        if exercise_notify in ["", "y", "n"]:
            config['page_settings']['exercise']['notify'] = exercise_notify != 'n'
            break
        print("输入无效！请输入y或n")
    
    # 填空题页面
    print("\n填空题页面:")
    while True:
        blank_download = input("检测到填空题页面后是否下载图片？(y=是, n=否, 默认y): ").strip().lower()
        if blank_download in ["", "y", "n"]:
            config['page_settings']['blank']['download'] = blank_download != 'n'
            break
        print("输入无效！请输入y或n")
    while True:
        blank_notify = input("检测到填空题页面后是否发送通知？(y=是, n=否, 默认y): ").strip().lower()
        if blank_notify in ["", "y", "n"]:
            config['page_settings']['blank']['notify'] = blank_notify != 'n'
            break
        print("输入无效！请输入y或n")
    
    # 主观题页面
    print("\n主观题页面:")
    while True:
        subjective_download = input("检测到主观题页面后是否下载图片？(y=是, n=否, 默认y): ").strip().lower()
        if subjective_download in ["", "y", "n"]:
            config['page_settings']['subjective']['download'] = subjective_download != 'n'
            break
        print("输入无效！请输入y或n")
    while True:
        subjective_notify = input("检测到主观题页面后是否发送通知？(y=是, n=否, 默认y): ").strip().lower()
        if subjective_notify in ["", "y", "n"]:
            config['page_settings']['subjective']['notify'] = subjective_notify != 'n'
            break
        print("输入无效！请输入y或n")
    
    # 6. XPath配置
    print("\n" + "="*40)
    print("               XPath配置（直接回车使用默认值）")
    print("="*40)
    
    # PPT XPath
    ppt_xpath_default = config['xpaths']['ppt']
    ppt_xpath = input(f"PPT页面XPath (默认: {ppt_xpath_default}): ").strip()
    if ppt_xpath:
        config['xpaths']['ppt'] = ppt_xpath
        
    # 选择题 XPath
    exercise_xpath_default = config['xpaths']['exercise']
    exercise_xpath = input(f"选择题页面XPath (默认: {exercise_xpath_default}): ").strip()
    if exercise_xpath:
        config['xpaths']['exercise'] = exercise_xpath
        
    # 填空题 XPath
    blank_xpath_default = config['xpaths']['blank']
    blank_xpath = input(f"填空题页面XPath (默认: {blank_xpath_default}): ").strip()
    if blank_xpath:
        config['xpaths']['blank'] = blank_xpath
        
    # 主观题 XPath
    subjective_xpath_default = config['xpaths']['subjective']
    subjective_xpath = input(f"主观题页面XPath (默认: {subjective_xpath_default}): ").strip()
    if subjective_xpath:
        config['xpaths']['subjective'] = subjective_xpath
    
    # 7. AI分析配置
    print("\n" + "="*40)
    print("               AI分析配置")
    print("="*40)
    while True:
        ai_enable = input("是否启用AI分析功能？(y=是, n=否, 默认y): ").strip().lower()
        if ai_enable in ["", "y", "n"]:
            config['ai']['enable'] = ai_enable != 'n'
            break
        print("输入无效！请输入y或n")

    if config['ai']['enable']:
        config['ai']['apikey'] = input("请输入AI的API Key: ").strip()
        config['ai']['base_url'] = input("请输入AI的Base URL: ").strip()
        config['ai']['model'] = input("请输入AI的模型名称: ").strip()
    
    # 8. OCR配置
    print("\n" + "="*40)
    print("               OCR配置")
    print("="*40)
    config['ocr']['apikey'] = input("请输入百度OCR的API Key: ").strip()
    config['ocr']['secretkey'] = input("请输入百度OCR的Secret Key: ").strip()
    
    # 显示配置摘要并确认
    print("\n" + "="*60)
    print("                配置摘要（请确认）")
    print("="*60)
    print(f"1. 服务器: {config['server']['name']} ({config['server']['base_url']})")
    print(f"2. 时间配置:")
    print(f"   - 常规检测间隔: {config['timing']['normal_interval']}秒")
    print(f"   - 连续页面更新检测阈值: {config['timing']['threshold']}秒")
    print(f"   - 连续出题检测时间: {config['timing']['rapid_interval']}秒")
    print(f"3. 刷新设置: {'启用（每次检测前刷新页面）' if config['refresh'] else '禁用（不主动刷新）'}")
    print(f"4. 微信配置: {'已配置WebHook' if config['wechat']['webhook_url'] else '未配置WebHook'}")
    print(f"5. 页面检测设置:")
    print(f"   - PPT页面: 下载={'启用' if config['page_settings']['ppt']['download'] else '禁用'}, 通知={'启用' if config['page_settings']['ppt']['notify'] else '禁用'}")
    print(f"   - 选择题页面: 下载={'启用' if config['page_settings']['exercise']['download'] else '禁用'}, 通知={'启用' if config['page_settings']['exercise']['notify'] else '禁用'}")
    print(f"   - 填空题页面: 下载={'启用' if config['page_settings']['blank']['download'] else '禁用'}, 通知={'启用' if config['page_settings']['blank']['notify'] else '禁用'}")
    print(f"   - 主观题页面: 下载={'启用' if config['page_settings']['subjective']['download'] else '禁用'}, 通知={'启用' if config['page_settings']['subjective']['notify'] else '禁用'}")
    print(f"6. AI分析设置: {'启用' if config['ai']['enable'] else '禁用'}")
    print(f"7. OCR设置: {'已配置' if (config['ocr']['apikey'] and config['ocr']['secretkey']) else '未完全配置'}")
    print("="*60 + "\n")
    
    # 配置确认步骤
    while True:
        confirm = input("配置是否正确？(y=保存配置, n=重新配置): ").strip().lower()
        if confirm == "y":
            utils.log("用户确认配置正确，保存配置")
            save_config(config)  # 保存新配置
            return config
        elif confirm == "n":
            utils.log("用户选择重新配置，重新进入配置流程")
            return get_user_config()
        else:
            print("输入无效！请输入y或n")