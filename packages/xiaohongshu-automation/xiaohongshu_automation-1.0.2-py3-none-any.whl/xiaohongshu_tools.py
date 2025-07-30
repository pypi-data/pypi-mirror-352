import threading
import json
import time
from datetime import datetime
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
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

    def search_notes(self, keywords: str, limit: int = 5):
        """
        根据关键词搜索小红书笔记
        
        Args:
            keywords: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            dict: 包含搜索结果的字典
        """
        self.last_activity = time.time()
        
        try:
            # 构建搜索URL并访问
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keywords}"
            logger.info(f"开始搜索关键词: {keywords}")
            
            self.driver.get(search_url)
            time.sleep(5)  # 等待页面加载
            
            # 额外等待页面完全加载
            time.sleep(5)
            
            # 尝试获取帖子卡片
            post_cards = []
            post_links = []
            post_titles = []
            
            # 使用多种选择器策略获取帖子卡片
            selectors = [
                "section.note-item",
                "div[data-v-a264b01a]",
                ".feeds-container .note-item",
                ".search-result-container .note-item"
            ]
            
            for selector in selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        post_cards = cards
                        logger.info(f"使用选择器 {selector} 找到 {len(post_cards)} 个帖子卡片")
                        break
                except Exception as e:
                    logger.warning(f"选择器 {selector} 失败: {str(e)}")
                    continue
            
            if not post_cards:
                logger.warning("未找到任何帖子卡片")
                return {
                    "success": False,
                    "message": f"未找到与\"{keywords}\"相关的笔记",
                    "data": []
                }
            
            # 处理每个帖子卡片  
            for card in post_cards[:limit * 2]:  # 多获取一些以防有无效的
                card_cover = card.find_element(By.CSS_SELECTOR, ".cover")
                try:
                    # 获取链接
                    link_element = None
                    link_selectors = [
                        'a[href*="/explore/"]',
                        'a[href*="/discovery/"]',
                        'a',
                        '.cover'
                    ]
                    
                    for link_selector in link_selectors:
                        try:
                            link_element = card_cover.get_attribute('href')
                            if link_element:
                                break
                        except:
                            continue
                    
                    if not link_element:
                        continue
                    
                    href = link_element
                    if not href or 'xiaohongshu.com' not in href:
                        continue
                    
                    # 确保是完整URL
                    if href.startswith('/'):
                        href = f"https://www.xiaohongshu.com{href}"
                    
                    # 获取帖子标题
                    title = "未知标题"
                    title_selectors = [
                        '.footer .title span',
                        '.title span',
                        'span.title',
                        '.desc',
                        '.content'
                    ]
                    
                    for title_selector in title_selectors:
                        try:
                            title_element = card.find_element(By.CSS_SELECTOR, title_selector)
                            if title_element:
                                title_text = title_element.get_attribute('textContent') or title_element.text
                                if title_text and len(title_text.strip()) > 5:
                                    title = title_text.strip()
                                    break
                        except:
                            continue
                    
                    # 如果还是没有找到标题，尝试获取卡片中的所有文本
                    if title == "未知标题":
                        try:
                            # 获取卡片中所有的span元素的文本
                            text_elements = card.find_elements(By.CSS_SELECTOR, 'span')
                            potential_titles = []
                            for text_el in text_elements:
                                text = text_el.text
                                if text and len(text.strip()) > 5 and len(text.strip()) < 100:
                                    potential_titles.append(text.strip())
                            
                            if potential_titles:
                                # 选择最长的文本作为标题
                                title = max(potential_titles, key=len)
                        except:
                            pass
                    
                    # 验证链接和标题有效性
                    if href and title != "未知标题":
                        post_links.append(href)
                        post_titles.append(title)
                        logger.info(f"找到笔记: {title[:50]}...")
                    
                except Exception as e:
                    logger.warning(f"处理帖子卡片时出错: {str(e)}")
                    continue
            
            # 去重
            unique_posts = []
            seen_urls = set()
            for url, title in zip(post_links, post_titles):
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_posts.append({"url": url, "title": title})
            
            # 限制返回数量
            unique_posts = unique_posts[:limit]
            
            if unique_posts:
                logger.info(f"搜索成功，找到 {len(unique_posts)} 条结果")
                return {
                    "success": True,
                    "message": f"找到 {len(unique_posts)} 条与\"{keywords}\"相关的笔记",
                    "data": unique_posts,
                    "total": len(unique_posts)
                }
            else:
                return {
                    "success": False,
                    "message": f"未找到与\"{keywords}\"相关的笔记",
                    "data": []
                }
        
        except Exception as e:
            logger.error(f"搜索笔记时出错: {str(e)}")
            return {
                "success": False,
                "message": f"搜索笔记时出错: {str(e)}",
                "data": []
            }

    def get_note_content(self, url: str):
        """
        获取小红书笔记的详细内容
        
        Args:
            url: 小红书笔记URL
            
        Returns:
            dict: 包含笔记内容的字典
        """
        self.last_activity = time.time()
        
        try:
            logger.info(f"开始获取笔记内容: {url}")
            
            # 访问笔记页面
            self.driver.get(url)
            time.sleep(10)  # 等待页面加载
            
            # 增强滚动操作以确保所有内容加载
            self.driver.execute_script("""
                // 先滚动到页面底部
                window.scrollTo(0, document.body.scrollHeight);
                setTimeout(() => { 
                    // 然后滚动到中间
                    window.scrollTo(0, document.body.scrollHeight / 2); 
                }, 1000);
                setTimeout(() => { 
                    // 最后回到顶部
                    window.scrollTo(0, 0); 
                }, 2000);
            """)
            time.sleep(3)  # 等待滚动完成和内容加载
            
            # 获取帖子内容
            post_content = {}
            
            # 获取帖子标题 - 方法1：使用id选择器
            try:
                logger.info("尝试获取标题 - 方法1：使用id选择器")
                title_element = self.driver.find_element(By.CSS_SELECTOR, '#detail-title')
                if title_element:
                    title = title_element.text or title_element.get_attribute('textContent')
                    post_content["标题"] = title.strip() if title else "未知标题"
                    logger.info(f"方法1获取到标题: {post_content['标题']}")
                else:
                    logger.info("方法1未找到标题元素")
                    post_content["标题"] = "未知标题"
            except Exception as e:
                logger.info(f"方法1获取标题出错: {str(e)}")
                post_content["标题"] = "未知标题"
            
            # 获取帖子标题 - 方法2：使用class选择器
            if post_content["标题"] == "未知标题":
                try:
                    logger.info("尝试获取标题 - 方法2：使用class选择器")
                    title_element = self.driver.find_element(By.CSS_SELECTOR, 'div.title')
                    if title_element:
                        title = title_element.text or title_element.get_attribute('textContent')
                        post_content["标题"] = title.strip() if title else "未知标题"
                        logger.info(f"方法2获取到标题: {post_content['标题']}")
                    else:
                        logger.info("方法2未找到标题元素")
                except Exception as e:
                    logger.info(f"方法2获取标题出错: {str(e)}")
            
            # 获取帖子标题 - 方法3：使用JavaScript
            if post_content["标题"] == "未知标题":
                try:
                    logger.info("尝试获取标题 - 方法3：使用JavaScript")
                    title = self.driver.execute_script("""
                        // 尝试多种可能的标题选择器
                        const selectors = [
                            '#detail-title',
                            'div.title',
                            'h1',
                            'div.note-content div.title'
                        ];
                        
                        for (const selector of selectors) {
                            const el = document.querySelector(selector);
                            if (el && el.textContent.trim()) {
                                return el.textContent.trim();
                            }
                        }
                        return null;
                    """)
                    if title:
                        post_content["标题"] = title
                        logger.info(f"方法3获取到标题: {post_content['标题']}")
                    else:
                        logger.info("方法3未找到标题元素")
                except Exception as e:
                    logger.info(f"方法3获取标题出错: {str(e)}")
            
            # 获取作者 - 方法1：使用username类选择器
            try:
                logger.info("尝试获取作者 - 方法1：使用username类选择器")
                author_element = self.driver.find_element(By.CSS_SELECTOR, 'span.username')
                if author_element:
                    author = author_element.text or author_element.get_attribute('textContent')
                    post_content["作者"] = author.strip() if author else "未知作者"
                    logger.info(f"方法1获取到作者: {post_content['作者']}")
                else:
                    logger.info("方法1未找到作者元素")
                    post_content["作者"] = "未知作者"
            except Exception as e:
                logger.info(f"方法1获取作者出错: {str(e)}")
                post_content["作者"] = "未知作者"
            
            # 获取作者 - 方法2：使用链接选择器
            if post_content["作者"] == "未知作者":
                try:
                    logger.info("尝试获取作者 - 方法2：使用链接选择器")
                    author_element = self.driver.find_element(By.CSS_SELECTOR, 'a.name')
                    if author_element:
                        author = author_element.text or author_element.get_attribute('textContent')
                        post_content["作者"] = author.strip() if author else "未知作者"
                        logger.info(f"方法2获取到作者: {post_content['作者']}")
                    else:
                        logger.info("方法2未找到作者元素")
                except Exception as e:
                    logger.info(f"方法2获取作者出错: {str(e)}")
            
            # 获取作者 - 方法3：使用JavaScript
            if post_content["作者"] == "未知作者":
                try:
                    logger.info("尝试获取作者 - 方法3：使用JavaScript")
                    author = self.driver.execute_script("""
                        // 尝试多种可能的作者选择器
                        const selectors = [
                            'span.username',
                            'a.name',
                            '.author-wrapper .username',
                            '.info .name'
                        ];
                        
                        for (const selector of selectors) {
                            const el = document.querySelector(selector);
                            if (el && el.textContent.trim()) {
                                return el.textContent.trim();
                            }
                        }
                        return null;
                    """)
                    if author:
                        post_content["作者"] = author
                        logger.info(f"方法3获取到作者: {post_content['作者']}")
                    else:
                        logger.info("方法3未找到作者元素")
                except Exception as e:
                    logger.info(f"方法3获取作者出错: {str(e)}")
            
            # 获取发布时间 - 方法1：使用date类选择器
            try:
                logger.info("尝试获取发布时间 - 方法1：使用date类选择器")
                time_element = self.driver.find_element(By.CSS_SELECTOR, 'span.date')
                if time_element:
                    time_text = time_element.text or time_element.get_attribute('textContent')
                    post_content["发布时间"] = time_text.strip() if time_text else "未知"
                    logger.info(f"方法1获取到发布时间: {post_content['发布时间']}")
                else:
                    logger.info("方法1未找到发布时间元素")
                    post_content["发布时间"] = "未知"
            except Exception as e:
                logger.info(f"方法1获取发布时间出错: {str(e)}")
                post_content["发布时间"] = "未知"
            
            # 获取发布时间 - 方法2：使用JavaScript搜索日期格式
            if post_content["发布时间"] == "未知":
                try:
                    logger.info("尝试获取发布时间 - 方法2：使用JavaScript搜索")
                    time_text = self.driver.execute_script("""
                        // 尝试多种可能的时间选择器
                        const selectors = [
                            'span.date',
                            '.bottom-container .date',
                            '.date'
                        ];
                        
                        for (const selector of selectors) {
                            const el = document.querySelector(selector);
                            if (el && el.textContent.trim()) {
                                return el.textContent.trim();
                            }
                        }
                        
                        // 尝试查找包含日期格式的文本
                        const dateRegexes = [
                            /编辑于\\s*([\\d-]+)/,
                            /(\\d{2}-\\d{2})/,
                            /(\\d{4}-\\d{2}-\\d{2})/,
                            /(\\d+月\\d+日)/,
                            /(\\d+天前)/,
                            /(\\d+小时前)/,
                            /(今天)/,
                            /(昨天)/
                        ];
                        
                        const allText = document.body.textContent;
                        for (const regex of dateRegexes) {
                            const match = allText.match(regex);
                            if (match) {
                                return match[0];
                            }
                        }
                        
                        return null;
                    """)
                    if time_text:
                        post_content["发布时间"] = time_text
                        logger.info(f"方法2获取到发布时间: {post_content['发布时间']}")
                    else:
                        logger.info("方法2未找到发布时间元素")
                except Exception as e:
                    logger.info(f"方法2获取发布时间出错: {str(e)}")
            
            # 获取帖子正文内容 - 方法1：使用精确的ID和class选择器
            try:
                logger.info("尝试获取正文内容 - 方法1：使用精确的ID和class选择器")
                
                # 先明确标记评论区域
                self.driver.execute_script("""
                    const commentSelectors = [
                        '.comments-container', 
                        '.comment-list',
                        '.feed-comment',
                        'div[data-v-aed4aacc]',  // 根据评论HTML结构
                        '.content span.note-text'  // 评论中的note-text结构
                    ];
                    
                    for (const selector of commentSelectors) {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {
                            if (el) {
                                el.setAttribute('data-is-comment', 'true');
                                console.log('标记评论区域:', el.tagName, el.className);
                            }
                        });
                    }
                """)
                
                # 先尝试获取detail-desc和note-text组合
                try:
                    content_element = self.driver.find_element(By.CSS_SELECTOR, '#detail-desc .note-text')
                    if content_element:
                        # 检查是否在评论区域内
                        is_in_comment = self.driver.execute_script("""
                            const el = arguments[0];
                            return !!el.closest("[data-is-comment='true']") || false;
                        """, content_element)
                        
                        if not is_in_comment:
                            content_text = content_element.text or content_element.get_attribute('textContent')
                            if content_text and len(content_text.strip()) > 50:  # 增加长度阈值
                                post_content["内容"] = content_text.strip()
                                logger.info(f"方法1获取到正文内容，长度: {len(post_content['内容'])}")
                            else:
                                logger.info(f"方法1获取到的内容太短: {len(content_text.strip() if content_text else 0)}")
                                post_content["内容"] = "未能获取内容"
                        else:
                            logger.info("方法1找到的元素在评论区域内，跳过")
                            post_content["内容"] = "未能获取内容"
                    else:
                        logger.info("方法1未找到正文内容元素")
                        post_content["内容"] = "未能获取内容"
                except:
                    post_content["内容"] = "未能获取内容"
                    
            except Exception as e:
                logger.info(f"方法1获取正文内容出错: {str(e)}")
                post_content["内容"] = "未能获取内容"
            
            # 获取帖子正文内容 - 方法2：使用JavaScript获取最长文本
            if post_content["内容"] == "未能获取内容":
                try:
                    logger.info("尝试获取正文内容 - 方法2：使用JavaScript获取最长文本")
                    content_text = self.driver.execute_script("""
                        // 定义评论区域选择器
                        const commentSelectors = [
                            '.comments-container', 
                            '.comment-list',
                            '.feed-comment',
                            'div[data-v-aed4aacc]',
                            '.comment-item',
                            '[data-is-comment="true"]'
                        ];
                        
                        // 找到所有评论区域
                        let commentAreas = [];
                        for (const selector of commentSelectors) {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach(el => commentAreas.push(el));
                        }
                        
                        // 查找可能的内容元素，排除评论区
                        const contentElements = Array.from(document.querySelectorAll('div#detail-desc, div.note-content, div.desc, span.note-text'))
                            .filter(el => {
                                // 检查是否在评论区域内
                                const isInComment = commentAreas.some(commentArea => 
                                    commentArea && commentArea.contains(el));
                                
                                if (isInComment) {
                                    console.log('排除评论区域内容:', el.tagName, el.className);
                                    return false;
                                }
                                
                                const text = el.textContent.trim();
                                return text.length > 100 && text.length < 10000;
                            })
                            .sort((a, b) => b.textContent.length - a.textContent.length);
                        
                        if (contentElements.length > 0) {
                            console.log('找到内容元素:', contentElements[0].tagName, contentElements[0].className);
                            return contentElements[0].textContent.trim();
                        }
                        
                        return null;
                    """)
                    
                    if content_text and len(content_text) > 100:  # 增加长度阈值
                        post_content["内容"] = content_text
                        logger.info(f"方法2获取到正文内容，长度: {len(post_content['内容'])}")
                    else:
                        logger.info(f"方法2获取到的内容太短或为空: {len(content_text) if content_text else 0}")
                except Exception as e:
                    logger.info(f"方法2获取正文内容出错: {str(e)}")
            
            # 获取帖子正文内容 - 方法3：区分正文和评论内容
            if post_content["内容"] == "未能获取内容":
                try:
                    logger.info("尝试获取正文内容 - 方法3：区分正文和评论内容")
                    content_text = self.driver.execute_script("""
                        // 首先尝试获取note-content区域
                        const noteContent = document.querySelector('.note-content');
                        if (noteContent) {
                            // 查找note-text，这通常包含主要内容
                            const noteText = noteContent.querySelector('.note-text');
                            if (noteText && noteText.textContent.trim().length > 50) {
                                return noteText.textContent.trim();
                            }
                            
                            // 如果没有找到note-text或内容太短，返回整个note-content
                            if (noteContent.textContent.trim().length > 50) {
                                return noteContent.textContent.trim();
                            }
                        }
                        
                        // 如果上面的方法都失败了，尝试获取所有段落并拼接
                        const paragraphs = Array.from(document.querySelectorAll('p'))
                            .filter(p => {
                                // 排除评论区段落
                                const isInComments = p.closest('.comments-container, .comment-list');
                                return !isInComments && p.textContent.trim().length > 10;
                            });
                            
                        if (paragraphs.length > 0) {
                            return paragraphs.map(p => p.textContent.trim()).join('\\n\\n');
                        }
                        
                        return null;
                    """)
                    
                    if content_text and len(content_text) > 50:
                        post_content["内容"] = content_text
                        logger.info(f"方法3获取到正文内容，长度: {len(post_content['内容'])}")
                    else:
                        logger.info(f"方法3获取到的内容太短或为空: {len(content_text) if content_text else 0}")
                except Exception as e:
                    logger.info(f"方法3获取正文内容出错: {str(e)}")
            
            # 确保所有字段都有值
            if "标题" not in post_content or not post_content["标题"]:
                post_content["标题"] = "未知标题"
            if "作者" not in post_content or not post_content["作者"]:
                post_content["作者"] = "未知作者"
            if "发布时间" not in post_content or not post_content["发布时间"]:
                post_content["发布时间"] = "未知"
            if "内容" not in post_content or not post_content["内容"]:
                post_content["内容"] = "未能获取内容"
            
            logger.info(f"笔记内容获取完成: {url}")
            
            return {
                "success": True,
                "message": "成功获取笔记内容",
                "data": {
                    "url": url,
                    "标题": post_content["标题"],
                    "作者": post_content["作者"],
                    "发布时间": post_content["发布时间"],
                    "内容": post_content["内容"]
                }
            }
        
        except Exception as e:
            logger.error(f"获取笔记内容时出错: {str(e)}")
            return {
                "success": False,
                "message": f"获取笔记内容时出错: {str(e)}",
                "data": {}
            }

    def analyze_note(self, url: str):
        """
        分析小红书笔记内容，提取关键信息和领域标签
        
        Args:
            url: 小红书笔记URL
            
        Returns:
            dict: 包含分析结果的字典
        """
        self.last_activity = time.time()
        
        try:
            logger.info(f"开始分析笔记: {url}")
            
            # 首先获取笔记内容
            content_result = self.get_note_content(url)
            
            if not content_result.get("success"):
                return {
                    "success": False,
                    "message": f"无法获取笔记内容: {content_result.get('message', '未知错误')}",
                    "data": {}
                }
            
            content_data = content_result.get("data", {})
            
            # 提取基础信息
            title = content_data.get("标题", "未知标题")
            author = content_data.get("作者", "未知作者")
            publish_time = content_data.get("发布时间", "未知")
            content = content_data.get("内容", "未能获取内容")
            
            # 简单分词 - 提取关键词
            import re
            text_for_analysis = f"{title} {content}"
            words = re.findall(r'\w+', text_for_analysis)
            
            # 定义热门领域关键词
            domain_keywords = {
                "美妆": ["口红", "粉底", "眼影", "护肤", "美妆", "化妆", "保湿", "精华", "面膜", "彩妆", "护理", "肌肤", "美白", "防晒", "卸妆"],
                "穿搭": ["穿搭", "衣服", "搭配", "时尚", "风格", "单品", "衣橱", "潮流", "服装", "鞋子", "包包", "配饰", "款式", "街拍"],
                "美食": ["美食", "好吃", "食谱", "餐厅", "小吃", "甜点", "烘焙", "菜谱", "料理", "厨房", "食材", "味道", "推荐", "探店"],
                "旅行": ["旅行", "旅游", "景点", "出行", "攻略", "打卡", "度假", "酒店", "民宿", "风景", "拍照", "游记", "机票", "行程"],
                "母婴": ["宝宝", "母婴", "育儿", "儿童", "婴儿", "辅食", "玩具", "奶粉", "尿布", "孕妇", "怀孕", "产后", "早教"],
                "数码": ["数码", "手机", "电脑", "相机", "智能", "设备", "科技", "苹果", "华为", "小米", "测评", "开箱", "配置"],
                "家居": ["家居", "装修", "家具", "设计", "收纳", "布置", "家装", "厨房", "卧室", "客厅", "装饰", "软装", "整理"],
                "健身": ["健身", "运动", "瘦身", "减肥", "训练", "塑形", "肌肉", "跑步", "瑜伽", "力量", "有氧", "体重", "饮食"],
                "AI": ["AI", "人工智能", "大模型", "编程", "开发", "技术", "Claude", "GPT", "算法", "机器学习", "代码", "软件"],
                "生活": ["生活", "日常", "分享", "记录", "感悟", "心得", "体验", "推荐", "实用", "技巧", "方法", "习惯"]
            }
            
            # 检测笔记可能属于的领域
            detected_domains = []
            domain_scores = {}  # 记录每个领域的匹配分数
            
            for domain, domain_keys in domain_keywords.items():
                score = 0
                matched_keywords = []
                
                for key in domain_keys:
                    # 检查标题中是否包含关键词（权重更高）
                    if key.lower() in title.lower():
                        score += 3
                        matched_keywords.append(key)
                    # 检查内容中是否包含关键词
                    elif key.lower() in content.lower():
                        score += 1
                        matched_keywords.append(key)
                
                if score > 0:
                    domain_scores[domain] = {
                        "score": score,
                        "keywords": matched_keywords
                    }
            
            # 根据分数排序，选择最相关的领域
            if domain_scores:
                sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1]["score"], reverse=True)
                # 取前3个最相关的领域
                detected_domains = [domain for domain, _ in sorted_domains[:3]]
            else:
                # 如果没有检测到明确的领域，默认为生活
                detected_domains = ["生活"]
            
            # 提取关键词（去重并限制数量）
            unique_words = list(set(words))[:20]
            
            # 分析内容长度和复杂度
            content_length = len(content) if content != "未能获取内容" else 0
            word_count = len(words)
            
            # 生成分析结果
            analysis_result = {
                "url": url,
                "基础信息": {
                    "标题": title,
                    "作者": author,
                    "发布时间": publish_time,
                    "内容长度": content_length,
                    "词汇数量": word_count
                },
                "内容": content,
                "领域分析": {
                    "主要领域": detected_domains,
                    "领域详情": domain_scores
                },
                "关键词": unique_words,
                "分析指标": {
                    "内容质量": "高" if content_length > 200 else "中" if content_length > 50 else "低",
                    "信息丰富度": "高" if word_count > 100 else "中" if word_count > 30 else "低",
                    "领域明确度": "高" if len(detected_domains) <= 2 else "中" if len(detected_domains) <= 3 else "低"
                }
            }
            
            logger.info(f"笔记分析完成: {url} - 主要领域: {detected_domains}")
            
            return {
                "success": True,
                "message": f"成功分析笔记内容 - 主要领域: {', '.join(detected_domains)}",
                "data": analysis_result
            }
        
        except Exception as e:
            logger.error(f"分析笔记时出错: {str(e)}")
            return {
                "success": False,
                "message": f"分析笔记时出错: {str(e)}",
                "data": {}
            }

    def post_comment(self, url: str, comment: str):
        """
        发布评论到指定小红书笔记
        
        Args:
            url: 小红书笔记URL
            comment: 要发布的评论内容
            
        Returns:
            dict: 包含发布结果的字典
        """
        self.last_activity = time.time()
        
        try:
            logger.info(f"开始发布评论到笔记: {url}")
            logger.info(f"评论内容: {comment}")
            
            # 访问笔记页面
            self.driver.get(url)
            time.sleep(5)  # 等待页面加载
            
            # 定位评论区域并滚动到该区域
            comment_area_found = False
            comment_area_selectors = [
                'text="条评论"',
                'text="共"',
                'text="评论"',
                '.comment-container',
                '.comments-container'
            ]
            
            # 使用JavaScript查找评论区域并滚动
            try:
                comment_area_found = self.driver.execute_script("""
                    const selectors = ['[aria-label*="评论"]', '.comment', '.comments', '[data-testid*="comment"]'];
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            element.scrollIntoView({behavior: 'smooth', block: 'center'});
                            return true;
                        }
                    }
                    
                    // 如果没有找到明确的评论区域，滚动到页面中下部
                    window.scrollTo(0, document.body.scrollHeight * 0.7);
                    return false;
                """)
                time.sleep(3)
            except Exception as e:
                logger.info(f"JavaScript滚动失败，使用备用方案: {str(e)}")
                # 备用滚动方案
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7)")
                time.sleep(3)
            
            # 定位评论输入框
            comment_input = None
            input_selectors = [
                '//*[@id="noteContainer"]/div[4]/div[3]/div/div/div[1]/div[1]/div/div/span',
                'div[contenteditable="true"]',
                'textarea[placeholder*="说点什么"]',
                'input[placeholder*="说点什么"]',
                'div[placeholder*="说点什么"]',
                'textarea[placeholder*="评论"]',
                'input[placeholder*="评论"]'
            ]
            
            # 尝试常规选择器
            for selector in input_selectors:
                try:
                    intpu_element = self.driver.find_element(By.XPATH, selector)
                    comment_input = intpu_element
                    
                    #TODO添加适配性
                    #elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    # for element in elements:
                    #     if element.is_displayed() and element.is_enabled():
                    #         # 滚动到元素可见
                    #         self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    #         time.sleep(1)
                    #         comment_input = element
                    #         logger.info(f"找到评论输入框: {selector}")
                    #         break
                    if comment_input:
                        break
                except Exception as e:
                    logger.info(f"选择器 {selector} 失败: {str(e)}")
                    continue
            
            # 如果常规选择器失败，使用JavaScript查找
            if not comment_input:
                logger.info("尝试使用JavaScript查找评论输入框")
                try:
                    js_result = self.driver.execute_script("""
                        // 查找可编辑元素
                        const editableElements = Array.from(document.querySelectorAll('[contenteditable="true"]'));
                        if (editableElements.length > 0) {
                            for (const el of editableElements) {
                                if (el.offsetParent !== null) {  // 检查元素是否可见
                                    el.scrollIntoView({block: 'center'});
                                    el.setAttribute('data-comment-input', 'true');
                                    return true;
                                }
                            }
                        }
                        
                        // 查找包含"说点什么"的元素
                        const placeholderElements = Array.from(document.querySelectorAll('*'))
                            .filter(el => el.textContent && el.textContent.includes('说点什么') && el.offsetParent !== null);
                        if (placeholderElements.length > 0) {
                            placeholderElements[0].scrollIntoView({block: 'center'});
                            placeholderElements[0].setAttribute('data-comment-input', 'true');
                            return true;
                        }
                        
                        // 查找textarea元素
                        const textareas = Array.from(document.querySelectorAll('textarea'));
                        for (const textarea of textareas) {
                            if (textarea.offsetParent !== null) {
                                textarea.scrollIntoView({block: 'center'});
                                textarea.setAttribute('data-comment-input', 'true');
                                return true;
                            }
                        }
                        
                        return false;
                    """)
                    
                    if js_result:
                        time.sleep(1)
                        # 尝试再次查找标记的元素
                        try:
                            comment_input = self.driver.find_element(By.CSS_SELECTOR, '[data-comment-input="true"]')
                            logger.info("JavaScript成功找到评论输入框")
                        except:
                            logger.warning("JavaScript标记成功但无法定位元素")
                except Exception as e:
                    logger.warning(f"JavaScript查找评论输入框失败: {str(e)}")
            
            if not comment_input:
                return {
                    "success": False,
                    "message": "未能找到评论输入框，无法发布评论。可能需要手动滚动到评论区域或笔记不支持评论。"
                }
            
            # 输入评论内容
            try:
                # 先点击输入框激活
                comment_input.click()
                time.sleep(1)
                comment_input_real = self.driver.find_element(By.XPATH, '//*[@id="content-textarea"]')
                # 清空现有内容
                comment_input_real.clear()
                time.sleep(0.5)
                
                # 输入评论内容
                comment_input_real.send_keys(comment)
                time.sleep(2)
                
                logger.info("评论内容输入完成")
                
            except Exception as e:
                logger.error(f"输入评论内容失败: {str(e)}")
                return {
                    "success": False,
                    "message": f"输入评论内容失败: {str(e)}"
                }
            
            # 发送评论
            send_success = False
            
            # 方法1: 尝试点击发送按钮
            try:
                send_button_selectors = [
                    'button:contains("发送")',
                    'button:contains("发布")',
                    'button:contains("提交")',
                    'button[type="submit"]',
                    '.send-button',
                    '.submit-button'
                ]
                
                for selector in send_button_selectors:
                    try:
                        if selector.startswith('button:contains'):
                            # 使用XPath处理包含文本的选择器
                            text = selector.split('"')[1]
                            xpath = f"//button[contains(text(), '{text}')]"
                            send_button = self.driver.find_element(By.XPATH, xpath)
                        else:
                            send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if send_button.is_displayed() and send_button.is_enabled():
                            send_button.click()
                            time.sleep(3)
                            send_success = True
                            logger.info(f"使用选择器 {selector} 成功点击发送按钮")
                            break
                    except Exception as e:
                        logger.info(f"发送按钮选择器 {selector} 失败: {str(e)}")
                        continue
                        
                if send_success:
                    logger.info("方法1: 发送按钮点击成功")
                    
            except Exception as e:
                logger.info(f"方法1发送失败: {str(e)}")
            
            # 方法2: 如果方法1失败，尝试使用Enter键
            if not send_success:
                try:
                    comment_input.send_keys("\n")  # 发送回车键
                    time.sleep(3)
                    send_success = True
                    logger.info("方法2: Enter键发送成功")
                except Exception as e:
                    logger.info(f"方法2发送失败: {str(e)}")
            
            # 方法3: 如果方法2失败，尝试使用JavaScript点击发送按钮
            if not send_success:
                try:
                    js_send_result = self.driver.execute_script("""
                        // 查找包含"发送"、"发布"、"提交"文本的按钮
                        const buttonTexts = ['发送', '发布', '提交', 'Send', 'Post', 'Submit'];
                        const buttons = Array.from(document.querySelectorAll('button'));
                        
                        for (const btn of buttons) {
                            for (const text of buttonTexts) {
                                if (btn.textContent && btn.textContent.includes(text) && 
                                    btn.offsetParent !== null && !btn.disabled) {
                                    btn.click();
                                    return true;
                                }
                            }
                        }
                        
                        // 尝试查找submit类型的按钮
                        const submitButtons = document.querySelectorAll('button[type="submit"]');
                        for (const btn of submitButtons) {
                            if (btn.offsetParent !== null && !btn.disabled) {
                                btn.click();
                                return true;
                            }
                        }
                        
                        return false;
                    """)
                    
                    if js_send_result:
                        time.sleep(3)
                        send_success = True
                        logger.info("方法3: JavaScript点击发送按钮成功")
                    else:
                        logger.info("方法3: JavaScript未找到发送按钮")
                        
                except Exception as e:
                    logger.info(f"方法3发送失败: {str(e)}")
            
            # 检查发送结果
            if send_success:
                # 等待一下再检查是否发送成功
                time.sleep(2)
                
                # 简单检查：看评论输入框是否被清空（通常发送成功后会清空）
                try:
                    current_value = comment_input.get_attribute('value') or comment_input.text
                    if not current_value.strip():
                        logger.info("评论输入框已清空，推测发送成功")
                    else:
                        logger.info(f"评论输入框仍有内容: {current_value[:50]}...")
                except:
                    pass
                
                return {
                    "success": True,
                    "message": f"已成功发布评论：{comment}",
                    "data": {
                        "url": url,
                        "comment": comment,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "发布评论失败，未能找到或点击发送按钮。请检查笔记是否支持评论或网络连接。"
                }
        
        except Exception as e:
            logger.error(f"发布评论时出错: {str(e)}")
            return {
                "success": False,
                "message": f"发布评论时出错: {str(e)}"
            }