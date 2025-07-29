# local_api.py
from fastapi import FastAPI, Query, Body
from typing import List, Optional
from pydantic import BaseModel
import subprocess
from xiaohongshu_tools import XiaohongshuTools
import logging
import time
import threading
from unti import get_news,get_comments_and_reply

# 定义请求模型
class PublishRequest(BaseModel):
    pic_urls: List[str]
    title: str
    content: str
    labels: Optional[List[str]] = None  # 添加可选的labels字段

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

tools = XiaohongshuTools()

def run_get_comments_and_reply():
    retry_count = 0
    max_retries = 5
    reply_count = 0
    while True:
        try:
            url= "https://www.xiaohongshu.com/explore/67b94551000000002902b506?xsec_token=AB6AsqCQ2ck6I6ANbnEuEPHjAxMwvYCAm00BiLxfjU9o8=&xsec_source=pc_user"
            comments_data = get_comments_and_reply(url)
            logger.info("Successfully executed get_comments_and_reply()")
            reply_count += 1
            logger.info(f"Successfully executed get_comments_and_reply() {reply_count} times")
            retry_count = 0
        except Exception as e:
            if "[Errno 11001] getaddrinfo failed" or "network connectivity" in str(e):
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"getaddrinfo failed, retrying {retry_count}/{max_retries}...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"Max retries ({max_retries}) reached. Continuing main loop...")
            logger.error(f"Error executing get_comments_and_reply(): {str(e)}")
            # Don't break the loop on error, continue to next iteration
        logger.info("等待3分钟，准备下次执行")
        time.sleep(3 * 60)  # Sleep for 3 minutes before next iteration

# Start the background thread
#comments_thread = threading.Thread(target=run_get_comments_and_reply, daemon=True)
#comments_thread.start()
#logger.info("Comments thread started successfully")

@app.post("/publish")
def publish(request: PublishRequest):
    """
    发布内容到小红书
    支持 JSON 请求体，避免 URL 过长问题
    """
    try:
        logger.info(f"接收到发布请求: {request.title}")
        urls = tools.publish_xiaohongshu(
            request.pic_urls, 
            request.title, 
            request.content, 
            request.labels  # 传递labels参数
        )
        if urls:    
            logger.info(f"发布成功: {request.title}")
            return {"status": "success", "urls": urls}
        else:
            logger.error(f"发布失败，未返回URL: {request.title}")
            return {"status": "error", "message": "发布失败，未获得发布链接"}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"发布异常: {request.title} - {error_msg}")
        return {"status": "error", "message": error_msg}
    
    
@app.post("/post_comments")
def post_comments(
    comments_response: dict[str,List[dict]] = Body(...),
    url: str = Query(...)
):
    try:
        tools.reply_comments(comments_response, url)
        return {"message": "success"}
    except Exception as e:
        message = f"Error posting comments: {str(e)}"
        logger.error(message)
        return {"message": message}
    
@app.get("/get_comments")
def get_comments(url: str):
    try:
        comments = tools.get_comments(url)
        if comments == "当前无评论":
            return {"status": "success", "message": "当前无评论"}
        return {"status": "success", "comments": comments}
    except Exception as e:
        message = f"Error getting comments: {str(e)}"
        logger.error(message)
        return {"status": "error", "message": message}



# 运行服务（默认端口 8000）
if __name__ == "__main__":
    import threading
    import time

    def run_get_news():
        while True:
            try:
                time.sleep(10)
                get_news()
                logger.info("Successfully executed get_news()")
            except Exception as e:
                logger.error(f"Error executing get_news(): {str(e)}")
            time.sleep(6 * 60 * 60)  # Sleep for 6 hours

    # Start the background thread
    #news_thread = threading.Thread(target=run_get_news, daemon=True)
    #news_thread.start()



    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)