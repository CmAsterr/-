> 不停下零距离的思念.

想必很多大学生被老登雨课堂随机布置题阴过，作者也是因此大物 I 平时分很低.

于是有了这款软件，支持检测到指定类型页面后企业微信中推送消息提醒（可同步至微信），附带题目图片和 ai 解析.以下是教程

---

### 企业微信通知设置

- 使用者创建一个企业

- 打开全员群（默认打开）

  - 【首页 -> 工作台 -> 管理企业 -> 聊天管理 -> 全员群】

    > 参考：[企业微信全员群已关闭是什么意思？全员群如何开启？ - 企业微信指南](https://weibanzhushou.com/blog/1359)

- 设置该群的消息推送

  - 【群聊页 -> 右上角三个 · -> 消息推送 -> 添加 -> 填写配置 -> Webhook 地址 -> 复制链接】

    > 参考：[如何设置「消息推送」-帮助中心-企业微信](https://open.work.weixin.qq.com/help2/pc/14931)

    将该 Webhook 链接复制粘贴到软件【配置工具】中对应文本框，在检测到指定类型页面后即会发送消息推送到企业微信群

  - 可以在[机器人接收管理 - 接收管理 - 消息中心 - 控制台](https://console.cloud.tencent.com/message/robot)进行机器人消息推送测试

    【新建机器人 -> 按需填写，粘贴 Webhook 地址，指定成员可不填 -> 确定】

    在“操作”栏下点击“测试”进行消息推送测试

- 在微信中接收提醒

  - 将企业微信和个人微信消息互通，避免错过消息推送

    1. 在企业微信[官网](https://work.weixin.qq.com/)登录 或 在 PC 端企业微信主页【左上角 -> 头像 -> 管理企业】，打开管理后台界面

       > 参考：[登录管理后台-帮助中心-企业微信](https://open.work.weixin.qq.com/help2/pc/17309)

    2. 【管理后台 -> 我的企业 -> 微信插件】，点击“获取更多尺寸的二维码”，可获取“邀请关注微信插件”的二维码

       > 参考：[如何关注微信插件-帮助中心-企业微信](https://open.work.weixin.qq.com/help2/pc/14799)

----

### 百度智能云 OCR 接入识别题目

1. 【访问[百度智能云官网](https://cloud.baidu.com/) -> 右上角“控制台” -> 搜索“文字识别”】或 直接访问[百度智能云控制台](https://console.bce.baidu.com/ai-engine/ocr/overview/index)

2. 在下方“服务列表”中选择“教育场景OCR”，找到“公式识别”，点横着的三个 ·，查看 api 文档【[公式识别 - 文字识别OCR](https://cloud.baidu.com/doc/OCR/s/Ok3h7xxva)】，其中有详细请求方法

3. 在左侧点击“应用列表”，点击“创建应用”，填写必要信息，然后“确定”；创建好之后即可看到该应用的 API Key 和 Secret Key，复制粘贴到软件【配置工具】中对应文本框

   在以后若要再次查看该应用 API Key 和 Secret Key，点击左侧“应用列表”即可

> 参考：[如何获取百度智能云开放平台 API Key 密钥（分步指南） - 幂简集成](https://explinks.com/blog/hou-to-get-baidu-cloud-open-platform-api-key-step-by-step-guide/)

---

### 火山引擎 AI 接入解析题目

1. 访问[豆包大模型-火山引擎](https://www.volcengine.com/product/doubao/)，点击主页“开启AI新体验”，登录；来到[火山方舟大模型体验中心-火山引擎](https://www.volcengine.com/experience/ark?model=deepseek-v3-1-250821)

2. 点击右上角“API 接入”，在 STEP 1 中获取 API KEY；STEP 2 中【选择模型并开通 -> OpenAI SDK 调用示例】可查看在 python 中调用方法

   将该 API KEY 复制粘贴到软件【配置工具】中对应文本框

---

### msedgedriver 驱动配置

1. 在 edge 浏览器中访问 `edge://version/`，第一行中会展示你使用的 Edge 浏览器版本（本项目测试时使用 139.0 大版本）

2. 访问 [Microsoft Edge WebDriver |Microsoft Edge 开发人员](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver)，下拉找到和你浏览器前三位匹配的版本，根据电脑类别和架构下载对应版本的 WebDriver

   > 参考：[Windows如何查看系统是ARM64还是X64架构_arm64和x64怎么查看windows-CSDN博客](https://blog.csdn.net/hong_taizi/article/details/90690595)

3. 将解压得到的 msedgedriver.exe 直接放在软件根目录（如原来就有可直接替换）

4. 在软件【配置工具 -> 驱动与版本检测】中进行测试，看是否配置成功（使用 release 版本可忽略第 1 ，2  项检查）

---

### 搭建雨课堂教师环境测试

1. 下载雨课堂 Office 插件【[雨课堂下载](https://www.yuketang.cn/download)】，并安装
2. 打开 PowerPoint，打开你上课要用的 ppt，在顶部最右侧会出现“雨课堂”插件，点击使用；具体步骤请看视频
   - [使用雨课堂授课_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1sq4y1Q7Ez)
   - [添加制作题目_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1Vy4y1L7MP)
3. 你可以使用另一个微信号进行听课，测试软件

---

## 雨课堂检测软件使用教程

把以上全部配置好之后，打开  `yuketang_monitor.exe`

- 在【课程管理】选项卡中可 新建、打开、删除课程

- 在【配置工具】选项卡中进行

  - 环境检测：见【msedgedriver 驱动配置】
  - 服务器配置：选择你要监控的课程使用的服务器，在**开始监控前一定要在页面底部“保存配置”**，否则可能导致监控失败
  - 时间配置：快速模式阈值指检测到页面出现一个指定监控页面后会持续快速检测的时间；不建议将两个间隔拉的太低，请保证 常规检测间隔 > 快速检测间隔
  - 页面监控设置：选择你要监控的页面类型；勾选自动下载会将当页图片保存到当前课程目录，勾选发送通知会向企业微信发送消息提醒（此时共同勾选企业微信还会收到当页图片）
  - 刷新配置：默认勾选。否则可能会因雨课堂页面未自动更新页面而导致错过题目
  - 微信消息配置：见【企业微信通知设置】
  - 百度OCR配置：见【百度智能云 OCR 接入识别题目】
  - AI分析配置：默认勾选“启用AI分析功能”；若你不想配置可取消勾选；详见【火山引擎 AI 接入解析题目】
  - 页面元素XPath配置：检测页面是否为指定类型的根据，用于定位元素；默认不用修改

  **修改完后一定记得保存配置！**

- 在【监控中心】选项卡中

  - 选择好课程后，点击“开始监控”

  - 此时浏览器会弹出登录界面，请扫码登录，然后点【1.我已完成扫码登录】

  - 请你自己遭浏览器导航到需要监控的课程主页，它们的网址会类似

    `https://changjiang.yuketang.cn/lesson/fullscreen/v3/1502938654875391232` 或

    `https://www.yuketang.cn/lesson/fullscreen/v3/1503621560706334976`

    然后点【2.我已导航到课程页面】

    此时将进入监控轮询，在检测到指定类型页面后会有系统弹框提醒和企业微信消息推送（若勾选了指定类型页面的“发送通知”），在消息中直接点击链接即可进答题界面

  - 点击【停止监控】，软件将会在几秒卡顿后停止监控流程（出现“未响应”是正常现象，等待即可）
