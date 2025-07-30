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

@app.get("/search_notes")
def search_notes(keywords: str = Query(...), limit: int = Query(5, ge=1, le=20)):
    """
    搜索小红书笔记
    
    Args:
        keywords: 搜索关键词
        limit: 返回结果数量限制，最多20条
    """
    try:
        logger.info(f"接收到搜索请求: {keywords}, 限制: {limit}")
        result = tools.search_notes(keywords, limit)
        logger.info(f"搜索完成: {keywords} - 找到 {len(result.get('data', []))} 条结果")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"搜索异常: {keywords} - {error_msg}")
        return {
            "success": False,
            "message": f"搜索失败: {error_msg}",
            "data": []
        }

@app.get("/get_note_content")
def get_note_content(url: str = Query(...)):
    """
    获取小红书笔记的详细内容
    
    Args:
        url: 小红书笔记URL
    """
    try:
        logger.info(f"接收到获取笔记内容请求: {url}")
        result = tools.get_note_content(url)
        if result.get("success"):
            logger.info(f"笔记内容获取成功: {url}")
        else:
            logger.warning(f"笔记内容获取失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"获取笔记内容异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"获取笔记内容失败: {error_msg}",
            "data": {}
        }

@app.get("/analyze_note")
def analyze_note(url: str = Query(...)):
    """
    分析小红书笔记内容，提取关键信息和领域标签
    
    Args:
        url: 小红书笔记URL
    """
    try:
        logger.info(f"接收到笔记分析请求: {url}")
        result = tools.analyze_note(url)
        if result.get("success"):
            logger.info(f"笔记分析成功: {url} - 主要领域: {result.get('data', {}).get('领域分析', {}).get('主要领域', [])}")
        else:
            logger.warning(f"笔记分析失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"笔记分析异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"笔记分析失败: {error_msg}",
            "data": {}
        }

@app.post("/post_comment")
def post_comment(url: str = Query(...), comment: str = Body(..., embed=True)):
    """
    发布评论到指定小红书笔记
    
    Args:
        url: 小红书笔记URL
        comment: 要发布的评论内容
    """
    try:
        logger.info(f"接收到评论发布请求: {url}")
        logger.info(f"评论内容: {comment}")
        result = tools.post_comment(url, comment)
        if result.get("success"):
            logger.info(f"评论发布成功: {url}")
        else:
            logger.warning(f"评论发布失败: {url} - {result.get('message', '未知错误')}")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"评论发布异常: {url} - {error_msg}")
        return {
            "success": False,
            "message": f"评论发布失败: {error_msg}",
            "data": {}
        }

def main():
    """主函数入口点，用于uvx调用"""
    import uvicorn
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

    logger.info("🚀 启动小红书自动化工具 FastAPI 服务器...")
    logger.info("📖 API 文档: http://localhost:8000/docs")
    logger.info("🔧 健康检查: http://localhost:8000/")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


# 运行服务（默认端口 8000）
if __name__ == "__main__":
    main()