import os
import base64
import requests
import utils
import time
from openai import OpenAI

# -------------------------- 配置参数 --------------------------
# 1. DeepSeek API配置（已提供）
DEEPSEEK_API_KEY = None
DEEPSEEK_BASE_URL = None
DEEPSEEK_MODEL = None

# 2. 百度OCR API配置（替换为自己的）
BAIDU_OCR_API_KEY = None  # 替换为你自己的百度OCR API Key
BAIDU_OCR_SECRET_KEY = None  # 替换为你自己的百度OCR Secret Key

# 3. OCR重试配置（解决QPS超限）
OCR_MAX_RETRIES = 3  # 最大重试次数
OCR_INIT_DELAY = 2   # 初始重试延迟（秒）
# --------------------------------------------------------------------------


def get_baidu_ocr_access_token(api_key, secret_key):
    """获取百度OCR访问令牌（带重试）"""
    retries = 0
    while retries < OCR_MAX_RETRIES:
        try:
            url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 触发HTTP错误（如429超限）
            token = response.json().get("access_token")
            if token:
                return token
            return f"获取令牌失败: 响应无token字段"
        except requests.exceptions.RequestException as e:
            retries += 1
            delay = OCR_INIT_DELAY * (2 ** (retries - 1))  # 指数退避延迟（2s→4s→8s）
            error_msg = str(e)
            # 识别QPS超限错误，针对性提示
            if "qps request limit" in error_msg.lower() or response.status_code == 429:
                print(f"[OCR令牌] QPS超限，{delay}秒后重试（{retries}/{OCR_MAX_RETRIES}）")
            else:
                print(f"[OCR令牌] 第{retries}次失败: {error_msg}，{delay}秒后重试")
            time.sleep(delay)
    return f"获取令牌失败（已重试{OCR_MAX_RETRIES}次）"


def image_to_text_baidu_ocr(image_path, access_token):
    """OCR识别图片文字（带QPS限流与重试）"""
    # 1. 预处理图片（基础校验）
    if not os.path.exists(image_path):
        return None, "图片文件不存在"
    file_size = os.path.getsize(image_path)
    if file_size > 4 * 1024 * 1024:  # 百度OCR免费版4MB限制
        return None, f"图片过大（{file_size/(1024*1024):.1f}MB），请压缩至4MB以内"
    if not image_path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
        return None, "不支持的图片格式（仅支持JPG/PNG/BMP）"

    # 2. 图片转Base64
    try:
        with open(image_path, "rb") as f:
            base64_img = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return None, f"图片转Base64失败: {str(e)}"

    # 3. 带重试的OCR请求
    retries = 0
    # ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"  # 通用文字识别（支持中英）
    ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/formula"  # 题目专用接口
    params = {"access_token": access_token}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"image": base64_img, "language_type": "CHN_ENG", "detect_direction": "true"}  # 自动纠正倾斜图片

    while retries < OCR_MAX_RETRIES:
        try:
            print(f"[OCR识别] 第{retries+1}次尝试...")
            response = requests.post(ocr_url, params=params, headers=headers, data=data, timeout=15)
            response.raise_for_status()
            result = response.json()

            # 处理OCR业务错误（如超限、无权限）
            if "error_code" in result:
                error_code = result["error_code"]
                error_msg = result["error_msg"]
                # QPS超限（错误码17）或每日调用量超限（错误码18）
                if error_code in [17, 18]:
                    retries += 1
                    delay = OCR_INIT_DELAY * (2 ** (retries - 1))
                    print(f"[OCR识别] 错误{error_code}: {error_msg}，{delay}秒后重试（{retries}/{OCR_MAX_RETRIES}）")
                    time.sleep(delay)
                    continue
                # 其他业务错误（如图片为空、密钥无效）
                return None, f"OCR业务错误{error_code}: {error_msg}"

            # 提取识别结果
            if "words_result" not in result:
                return None, "OCR未返回识别结果（可能图片无文字）"
            text = "\n".join([item["words"].strip() for item in result["words_result"]])
            if not text:
                return None, "OCR识别到空文本（可能图片模糊或无文字）"
            return text, f"OCR识别成功（{len(result['words_result'])}行文字）"

        except requests.exceptions.RequestException as e:
            retries += 1
            delay = OCR_INIT_DELAY * (2 ** (retries - 1))
            print(f"[OCR识别] 网络错误: {str(e)}，{delay}秒后重试（{retries}/{OCR_MAX_RETRIES}）")
            time.sleep(delay)

    return None, f"OCR识别失败（已重试{OCR_MAX_RETRIES}次，可能QPS长期超限）"


def ask_deepseek_text(question_text):
    """调用DeepSeek纯文本模型解答（保持与示例一致的格式）"""
    client = OpenAI(
        base_url=DEEPSEEK_BASE_URL,
        api_key=DEEPSEEK_API_KEY,
    )
    
    try:
        print("\n----- 向DeepSeek发送文字问题 -----")
        completion = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一个精通大学理工科的教授，针对题目类问题，需给出简洁清晰的步骤和答案（如数学题需写计算过程，选择题需说明理由）。"},
                {"role": "user", "content": f"请先直接给出图中问题的答案(选择题给选项，填空题给填的答案)，然后面再在答案后给出分析：\n{question_text}"}
            ],
            max_tokens=500,  # 限制回答长度，避免冗余
            temperature=0.2   # 降低随机性，确保解答严谨
        )
        return completion.choices[0].message.content
    
    except Exception as e:
        error_msg = str(e)
        if "Unauthorized" in error_msg:
            return f"DeepSeek认证失败: 请检查API Key是否正确"
        elif "InvalidParameter" in error_msg:
            return f"DeepSeek参数错误: {error_msg}"
        else:
            return f"DeepSeek调用失败: {error_msg}"

def get_ai_answer(ocr_config, ai_config, image_path):
    global BAIDU_OCR_SECRET_KEY,BAIDU_OCR_API_KEY,DEEPSEEK_API_KEY,DEEPSEEK_BASE_URL,DEEPSEEK_MODEL

    print(ocr_config)

    if not all([ocr_config.get('apikey'), ocr_config.get('secretkey')]):
        utils.log("OCR配置不完整，无法进行OCR解析")
        return None
    
    """调用Deepseek AI获取图片中题目的解答"""
    if not all([ai_config.get('apikey'), ai_config.get('base_url'), ai_config.get('model')]):
        utils.log("AI配置不完整，无法进行AI解析")
        return None
        
    if not os.path.exists(image_path):
        utils.log(f"图片文件不存在: {image_path}")
        return None

    BAIDU_OCR_API_KEY=ocr_config['apikey']
    BAIDU_OCR_SECRET_KEY=ocr_config['secretkey']

    DEEPSEEK_API_KEY=ai_config['apikey']
    DEEPSEEK_BASE_URL=ai_config['base_url']
    DEEPSEEK_MODEL=ai_config['model']

    # 1. 第一步：OCR识别图片文字
    print("----- 第一步：OCR识别图片文字 -----")
    ocr_token = get_baidu_ocr_access_token(BAIDU_OCR_API_KEY, BAIDU_OCR_SECRET_KEY)
    if isinstance(ocr_token, str) and "失败" in ocr_token:
        print(f"初始化失败: {ocr_token}")
        exit()
    print("[OCR令牌] 获取成功（有效期30天）")

    question_text, ocr_msg = image_to_text_baidu_ocr(image_path, ocr_token)
    if not question_text:
        print(f"识别失败: {ocr_msg}")
        exit()
    print(f"识别到的问题：\n{question_text}")
    print("-" * 50)
    
    # 2. 第二步：调用DeepSeek解答
    print("\n----- 第二步：获取DeepSeek解答 -----")
    answer = ask_deepseek_text(question_text)
    
    # 3. 返回结果
    return answer

    '''
    # 3. 输出结果
    print("\n" + "=" * 60)
    print("                    最终解答结果")
    print("=" * 60)
    print(f"📄 图片识别的问题：\n{question_text}\n")
    print(f"🤖 DeepSeek的解答：\n{answer}")
    print("=" * 60)
    '''