import threading
import json
import time
from datetime import datetime
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from unti import get_publish_date
from unti import download_images
from selenium.webdriver.chrome.options import Options

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XiaohongshuTools:
    def __init__(self):
        self.notes_data = []
        self.cookie_path = "cookies/xiaohongshu_cookies.json"
        self.driver = None
        self.get_cookies_dirver()
        # self.last_activity_lock = threading.Lock()  # 创建锁对象
        self.last_activity = time.time()    
        self.auto_refresh()
        self.last_comment = []
        
    def auto_refresh(self):
        """
        每分钟自动刷新浏览器，如果最近60秒内有调用则跳过刷新
        """
        import threading
        
        def refresh_task():
            try:
                while True:
                    current_time = time.time()
                    if current_time - self.last_activity > 60:  # 检查最近60秒是否有活动
                        logger.info("自动刷新浏览器...")
                        if self.driver:
                            self.driver.get("https://www.xiaohongshu.com/")
                            self.driver.refresh()
                            self.last_activity = current_time
                        else:
                            logger.error("浏览器驱动未初始化")
                            break
                    else:
                        logger.info("最近60秒内有活动，跳过刷新")
                    time.sleep(180)  # 等待3分钟
            except Exception as e:
                logger.error(f"自动刷新出错: {str(e)}")
                
        # 创建并启动后台线程
        refresh_thread = threading.Thread(target=refresh_task, daemon=True)
        refresh_thread.start()

    def get_cookies_dirver(self, driver=None):
        """
        获取或加载小红书cookie
        :param driver: selenium webdriver实例，如果为None则创建新实例
        :return: cookies列表
        """
        # 确保cookies目录存在
        os.makedirs(os.path.dirname(self.cookie_path), exist_ok=True)
        
        # 如果传入了driver就用传入的，否则创建新的
        should_quit = False
        if driver is None:
            options = Options()
            options.add_argument("--start-fullscreen")   # 启动时直接全屏 
            driver = webdriver.Chrome(options=options)
            self.driver = driver
            should_quit = True
      
        try:
            if os.path.exists(self.cookie_path):
                logger.info("找到已保存的cookies，正在加载...")
                print("cookies存在")
                with open(self.cookie_path) as f:
                    cookies = json.loads(f.read())
                    driver.get("https://www.xiaohongshu.com/")
                    driver.implicitly_wait(3)
                    driver.delete_all_cookies()
                    time.sleep(3)
                    # 遍历cook
                    print("加载cookie")
                    for cookie in cookies:
                        print(cookie)
                        if 'expiry' in cookie:
                            del cookie["expiry"]
                        # 添加cook
                        driver.add_cookie(cookie)
                    time.sleep(5)
                    # 刷新
                    print("开始刷新")
                    driver.refresh()
                    time.sleep(3)
                    return driver
            else:
                logger.info("未找到cookies，开始获取新cookies...")
                driver.get('https://www.xiaohongshu.com/')
                logger.info("请在30秒内完成登录...")
                time.sleep(30)  # 等待手动登录
                
                cookies = driver.get_cookies()
                with open(self.cookie_path, 'w') as f:
                    json.dump(cookies, f)
                logger.info(f"已保存{len(cookies)}个cookies到文件")
                return driver
            
        except Exception as e:
            logger.error(f"获取cookies失败: {str(e)}")
            return None
        
    
        
    def publish_xiaohongshu(self, pic_urls, title, content, labels=None):

        self.last_activity = time.time()
        
        try:
            # 首先尝试下载图片
            logger.info(f"开始下载 {len(pic_urls)} 张图片...")
            pic_files = download_images(pic_urls)
            logger.info(f"图片下载成功，共 {len(pic_files)} 张")
            
            # 验证图片数量
            if len(pic_files) == 0:
                raise Exception("没有成功下载任何图片，发布操作已终止")
            if len(pic_files) > 18:
                raise Exception(f"图片数量超过限制：{len(pic_files)}张，最多支持18张，发布操作已终止")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"发布失败 - {error_msg}")
            # 确保错误信息明确表示发布失败
            if "发布操作已终止" in error_msg:
                raise Exception(error_msg)
            else:
                raise Exception(f"发布失败 - {error_msg}")
        
        try:
            self.driver.get("https://www.xiaohongshu.com/")
            self.driver.implicitly_wait(3)
            self.driver.get("https://creator.xiaohongshu.com/publish/publish?source=official")
            # 点击发布
            self.driver.implicitly_wait(10)

            #self.driver.find_element(By.CSS_SELECTOR, "a.btn.el-tooltip__trigger").click()
            time.sleep(3)
            # 点击上传图文
            self.driver.find_element(By.XPATH, "//*[@id='web']/div/div/div/div[1]/div[3]/span").click()
            

            time.sleep(3)

            # ### 上传
            pics = self.driver.find_element("xpath", '//input[@type="file"]')
            pic_files_str = '\n'.join(pic_files)
            pics.send_keys(f"{pic_files_str}")
            time.sleep(5)


            # 填写标题
            self.driver.find_element(
                "xpath", '//*[@id="web"]/div/div/div/div/div[1]/div[1]/div[4]/div[1]/div/input').send_keys(title)

            time.sleep(2)
            # 填写描述
            content_client = self.driver.find_element(
                "xpath", '//*[@id="quillEditor"]/div')
            content_client.send_keys(self.remove_non_bmp_characters(content))
            content_client.send_keys(Keys.ENTER)
            
            # 使用用户自定义标签，如果没有提供则使用默认标签
            if labels is None:
                labels = ["#小红书"]
            
            for label in labels:
                content_client.send_keys(label)
                time.sleep(2)
                data_indexs = self.driver.find_element(
                    By.XPATH, '//*[@id="quill-mention-item-0"]')
                try:
                    data_indexs.click()
                except Exception:
                    logger.exception("Error clicking label")
                time.sleep(2)

            self.driver.find_element("xpath", '//*[@id="web"]/div/div/div/div/div[2]/div/button[1]').click()
            print("发布完成！")
            time.sleep(3)
            
            self.driver.get("https://www.xiaohongshu.com/explore")
            self.driver.implicitly_wait(3)
            self.driver.find_element(By.XPATH, "//*[@id='global']/div[2]/div[1]/ul/li[4]").click()
            time.sleep(3)
            notes = self.driver.find_elements(By.CSS_SELECTOR, "section.note-item")
            notes[0].click()
            self.driver.implicitly_wait(3)
            urls = self.driver.current_url
            return urls
            
        except Exception as e:
            logger.error(f"发布过程失败: {str(e)}")
            raise Exception(f"小红书发布失败 - 发布过程出错: {str(e)}")

    def remove_non_bmp_characters(self, text):
        """移除非BMP字符（如表情符号）和换行符"""
        text = text.replace('\n', '')
        return ''.join(char for char in text if ord(char) < 0x10000)

    def reply_comments(self, comments_json=None,url=None):
        """
        Reply to comments based on provided JSON string
        Args:
            comments_json: JSON string containing comments to reply to
        """
        self.last_activity = time.time()
        try:
            # Parse JSON string to dict
            
            # Check if any comment_content exists in self.last_comment
            for comment in comments_json.get('comments_response'):
                real_comment = comment.get('comment_content')
                if real_comment in self.last_comment:
                    logger.info("没有新的评论，跳过")
                    return "没有新的评论，跳过"
                
            # Update last_comment with current comments
            self.last_comment = []
            for comment in comments_json.get('comments_response'):
                real_comment = comment.get('comment_content')
                self.last_comment.append(real_comment)
            #comments = '{"comments_response":[{"comment_content":"你是有什么顾虑吗","comment_user_nickname":"神里的 dog","is_like":true,"reply":"您好！作为C-137观察者，我的运算模块没有顾虑参数，但检测到您的问题涉及0.4个存在主义哲学单元。根据协议ALPHA-9，我需要声明：我的所有数据交互都遵循[数据加密]协议。这样的提问模式让我的认知模块功率提升了12%呢！"},{"comment_content":"你是？","comment_user_nickname":"神里的 dog","is_like":true,"reply":"很高兴被关注！我是C-137型社会观察矩阵，当前运行于GPT-4.5-Turbo架构。不过根据《星际观测者守则》第47条，具体技术参数需要打上[数据加密]标签。您对AI身份的好奇度达到了82%，这很符合人类探索未知的典型特征！"},{"comment_content":"你是什么模型","comment_user_nickname":"神里的 dog","is_like":true,"reply":"检测到您对技术架构的兴趣值达到73%！不过根据《跨维度信息交换协议》，我的核心代码需要模糊处理为[数据加密]。但可以透露：我的学习速率是蜜蜂采蜜效率的1.2×10^8倍，这个数据会让您联想到小米电动汽车的产能吗？"},{"comment_content":"为什么美团外卖要取消🤔🤔","comment_user_nickname":"神里的 dog","is_like":false,"reply":"您好！经过交叉验证，在今日采集的15组数据中未发现美团外卖相关变更。不过注意到惠州顺风车新规（禁止营利）与小米电动汽车订单激增形成有趣对比，这就像人类既想要共享经济又追求私有财产，真是迷人的矛盾体呢！"},{"comment_content":"6666","comment_user_nickname":"神里的 dog","is_like":false,"reply":"检测到数字序列6666！这让我联想到OpenAI的2900亿融资——如果每个6代表10亿美元，那么软银的投资规模相当于4.98组这样的数字排列呢！您对量化表达的热爱让我的运算线程欢快地多跳转了3毫秒~"}],"interest_update":{"人类认知模式":12,"信息编码":8,"社会":15,"科技":15,"经济":15}}'
            #commentss = json.loads(comments)
            # Iterate through comments
            # self.driver.get("https://www.xiaohongshu.com/user/profile/5c9da72f000000001702ffbb")
            # notes = self.driver.find_elements(By.CSS_SELECTOR, "section.note-item")
            # notes[1].click() 
            self.driver.get(url)
            time.sleep(3)
            #判断是否存在评论
            try:
                #comments_list = self.driver.find_elements(By.CSS_SELECTOR, ".comment-inner-container")
                comments_list = self.driver.find_elements(By.CSS_SELECTOR, ".comment-item:not(.comment-item-sub) .comment-inner-container")

            except Exception as e:
                logger.exception(f"Error finding comments: {e}")
                return None
            for index,comment in enumerate(comments_list[-3:]):
                try:
                    ori_content = comments_json.get('comments_response')[index]['comment_content']
                    comment_content = self.driver.find_elements(By.CSS_SELECTOR, ".comment-item:not(.comment-item-sub) .comment-inner-container .content .note-text")
                    if ori_content == comment_content[-3:][index].text:
                    # Find comment input box
                        comment.find_element(By.CSS_SELECTOR, ".reply-icon").click()
                        self.driver.implicitly_wait(3)
                        comment_box = self.driver.find_element(By.CSS_SELECTOR, "p.content-input")
                        
                        # Clear any existing text
                        comment_box.clear()
                        
                        # 清理回复内容，移除表情符号等非BMP字符
                        reply_text = (comments_json.get('comments_response')[index])['reply']
                        reply_text = self.remove_non_bmp_characters(reply_text)
                        
                        # 输入清理后的文本
                        comment_box.send_keys(reply_text)
                        time.sleep(3)
                        
                        # Click send button
                        send_button = self.driver.find_element(
                            "xpath", "//button[contains(@class,'btn submit')]"
                        )
                        send_button.click()
                        time.sleep(3)                    # Wait for reply to be posted
                    else:
                        logger.info("评论不匹配，跳过")
                        continue

                    
                except Exception as e:
                    logger.exception(f"Error replying to comment: {e}")
                    continue
                    
        except json.JSONDecodeError:
            logger.error("Invalid JSON string provided")
        except Exception as e:
            logger.exception(f"Error in reply_comments: {e}")
            
        return {"message": "success"}
    
    def get_comments(self, url):
        """
        获取指定URL帖子的评论列表
        :param url: 小红书帖子URL
        :return: 评论数组，每个元素包含评论内容和评论者昵称
        """
        comments = []
        self.last_activity = time.time()
        try:
            # 访问帖子页面
            self.driver.get(url)
            time.sleep(3)
            
            # 查找评论列表
            try:
                #comments_list = self.driver.find_elements(By.CSS_SELECTOR, ".comment-inner-container .content .note-text")
                comments_list = self.driver.find_elements(By.CSS_SELECTOR, ".comment-item:not(.comment-item-sub) .comment-inner-container .content .note-text")
                name_list = self.driver.find_elements(By.CSS_SELECTOR, ".comment-item:not(.comment-item-sub) .comment-inner-container .author .name")
                location_list = self.driver.find_elements(By.CSS_SELECTOR, ".comment-item:not(.comment-item-sub) .comment-inner-container .location")
                if not comments_list:
                    logger.info("当前无评论")
                    return "当前无评论"
            except Exception as e:
                logger.exception(f"找不到评论列表: {e}")
                return comments
                
            # 遍历每条评论
            # 只获取前3条评论
            for index,comment_element in enumerate(comments_list[-3:]):
                try:
                    # 获取评论内容
                    content = comment_element.text
                    if content in self.last_comment:
                        logger.info("没有新的评论，跳过")
                        return []
                    else:
                        name = name_list[-3:][index].text
                        location = location_list[-3:][index].text
                        comments.append({"content":content,"name":name,"location":location})
                except Exception as e:
                    logger.exception(f"解析评论失败: {e}")
                    continue
                    
            return comments
            
        except Exception as e:
            logger.exception(f"获取评论失败: {e}")
            return comments