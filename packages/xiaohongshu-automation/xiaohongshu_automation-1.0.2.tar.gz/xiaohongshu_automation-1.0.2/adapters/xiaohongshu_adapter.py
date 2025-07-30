"""
小红书适配器
连接 MCP 服务端和现有的 FastAPI 服务
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import httpx
import json
from datetime import datetime
from config import MCPConfig

logger = logging.getLogger(__name__)

class XiaohongshuAdapter:
    """小红书功能适配器，负责与现有 FastAPI 服务通信"""
    
    def __init__(self, fastapi_base_url: str = "http://localhost:8000"):
        self.base_url = fastapi_base_url
        self.config = MCPConfig.get_adapter_config()
        
        # 使用配置的超时设置创建客户端
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=5.0,  # 连接超时
                read=self.config["timeout"],  # 读取超时
                write=10.0,   # 写入超时
                pool=5.0      # 连接池超时
            )
        )
        
        self._monitor_status = {
            "is_running": True,
            "last_check": datetime.now().isoformat(),
            "success_count": 0,
            "error_count": 0
        }
        self._publish_history = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request_with_retry(self, method: str, url: str, operation: str, **kwargs) -> httpx.Response:
        """
        带重试机制的HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            operation: 操作类型，用于获取超时设置
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应
            
        Raises:
            Exception: 所有重试都失败后抛出异常
        """
        # 获取操作特定的超时设置
        timeout = MCPConfig.get_timeout_for_operation(operation)
        kwargs['timeout'] = timeout
        
        max_retries = self.config["max_retries"] if self.config["enable_auto_retry"] else 1
        retry_delay = self.config["retry_delay"]
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"重试第 {attempt} 次请求: {method} {url}")
                    await asyncio.sleep(retry_delay)
                
                response = await self.client.request(method, url, **kwargs)
                
                # 检查状态码
                if response.status_code == 503:
                    raise httpx.HTTPStatusError(
                        "FastAPI 服务当前不可用 (503)。请确保后端服务正在运行：python main.py",
                        request=response.request,
                        response=response
                    )
                
                response.raise_for_status()
                return response
                
            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{max_retries}): {url} - 超时设置: {timeout}秒")
                if attempt == max_retries - 1:
                    raise Exception(f"请求超时：{timeout}秒内无响应。建议检查网络连接或增加超时设置。")
                    
            except httpx.ConnectError as e:
                last_exception = e
                logger.warning(f"连接失败 (尝试 {attempt + 1}/{max_retries}): {url}")
                if attempt == max_retries - 1:
                    raise Exception(f"无法连接到FastAPI服务({self.base_url})。请确保服务正在运行：python main.py")
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 503:
                    last_exception = e
                    logger.warning(f"服务不可用 (尝试 {attempt + 1}/{max_retries}): {url}")
                    if attempt == max_retries - 1:
                        raise Exception("FastAPI服务当前不可用。请启动后端服务：python main.py")
                else:
                    # 其他HTTP错误不重试
                    raise e
                    
            except Exception as e:
                last_exception = e
                logger.error(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    break
        
        # 所有重试都失败
        raise Exception(f"请求失败，已重试 {max_retries} 次。最后错误: {str(last_exception)}")
    
    async def publish_content(self, pic_urls: List[str], title: str, content: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        发布内容到小红书
        
        Args:
            pic_urls: 图片URL列表
            title: 标题
            content: 内容
            labels: 自定义标签列表，可选
            
        Returns:
            发布结果
        """
        try:
            # 构建请求参数
            data = {
                "pic_urls": pic_urls,
                "title": title,
                "content": content
            }
            
            # 如果提供了labels参数，添加到请求数据中
            if labels is not None:
                data["labels"] = labels
            
            logger.info(f"开始发布内容: {title}")
            
            # 调用 FastAPI 服务 - 使用改进的重试机制
            response = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/publish",
                "publish",
                json=data
            )
            
            result = response.json()
            
            # 检查响应中的status字段，如果是error则抛出异常
            if result.get("status") == "error":
                error_message = result.get("message", "发布失败，未知错误")
                logger.error(f"FastAPI返回错误: {error_message}")
                # 添加明确的业务错误标识，让异常处理能正确识别
                raise Exception(f"发布失败: {error_message}")
            
            # 记录发布历史
            self._publish_history.append({
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "pic_count": len(pic_urls),
                "labels": labels or ["#小红书"],  # 记录使用的标签
                "status": result.get("status", "unknown"),
                "urls": result.get("urls", [])
            })
            
            # 保持历史记录在合理范围内
            if len(self._publish_history) > 50:
                self._publish_history = self._publish_history[-50:]
            
            logger.info(f"内容发布成功: {title}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"发布内容失败: {error_msg}")
            
            # 记录失败的发布历史
            self._publish_history.append({
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "pic_count": len(pic_urls),
                "labels": labels or ["#小红书"],  # 记录使用的标签
                "status": "failed",
                "error": error_msg
            })
            
            # 优先检查是否为业务逻辑错误（来自FastAPI响应的error状态）
            if "发布失败:" in error_msg:
                # 这是业务逻辑错误，直接传递原始错误信息
                raise Exception(error_msg)
            
            # 然后检查HTTP/网络相关的错误
            elif isinstance(e, (httpx.ConnectError, httpx.TimeoutException)):
                # 真正的网络连接错误
                if isinstance(e, httpx.ConnectError):
                    raise Exception(f"无法连接到FastAPI服务器({self.base_url})。请检查服务是否运行。")
                else:
                    raise Exception(f"发布操作超时。当前超时设置: {MCPConfig.get_timeout_for_operation('publish')}秒")
            
            # 检查HTTP状态码错误
            elif "503" in error_msg or "不可用" in error_msg:
                raise Exception("FastAPI服务当前不可用。请确保后端服务正在运行：python main.py")
            
            # 其他未分类的错误
            else:
                # 保持原始错误信息，不要修改
                raise Exception(error_msg)

    async def get_comments(self, url: str) -> Dict[str, Any]:
        """
        获取帖子评论
        
        Args:
            url: 小红书帖子URL
            
        Returns:
            评论数据
        """
        try:
            logger.info(f"开始获取评论: {url}")
            
            # 调用 FastAPI 服务
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/get_comments",
                "comments",
                params={"url": url}
            )
            
            result = response.json()
            logger.info(f"获取评论成功: {url}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取评论失败: {error_msg}")
            
            if "503" in error_msg or "不可用" in error_msg:
                raise Exception("FastAPI服务未运行。请先启动后端服务：python main.py")
            elif "超时" in error_msg:
                raise Exception(f"获取评论超时。当前超时设置: {MCPConfig.get_timeout_for_operation('comments')}秒")
            else:
                raise Exception(f"获取评论失败: {error_msg}")

    async def reply_comments(self, comments_response: Dict[str, List[str]], url: str) -> Dict[str, Any]:
        """
        回复评论
        
        Args:
            comments_response: 评论回复数据
            url: 帖子URL
            
        Returns:
            回复结果
        """
        try:
            logger.info(f"开始回复评论: {url}")
            
            # 调用 FastAPI 服务
            response = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/post_comments",
                "comments",
                json=comments_response,
                params={"url": url}
            )
            
            result = response.json()
            logger.info(f"回复评论成功: {url}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"回复评论失败: {error_msg}")
            
            if "503" in error_msg or "不可用" in error_msg:
                raise Exception("FastAPI服务未运行。请先启动后端服务：python main.py")
            elif "超时" in error_msg:
                raise Exception(f"回复评论超时。当前超时设置: {MCPConfig.get_timeout_for_operation('comments')}秒")
            else:
                raise Exception(f"回复评论失败: {error_msg}")

    async def search_notes(self, keywords: str, limit: int = 5) -> Dict[str, Any]:
        """
        搜索小红书笔记
        
        Args:
            keywords: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            搜索结果
        """
        try:
            logger.info(f"开始搜索笔记: {keywords}")
            
            # 调用 FastAPI 服务
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/search_notes",
                "search",
                params={"keywords": keywords, "limit": limit}
            )
            
            result = response.json()
            
            # 检查搜索结果
            if result.get("success"):
                logger.info(f"搜索成功: {keywords} - 找到 {len(result.get('data', []))} 条结果")
            else:
                logger.warning(f"搜索失败: {keywords} - {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"搜索笔记失败: {error_msg}")
            
            if "503" in error_msg or "不可用" in error_msg:
                raise Exception("FastAPI服务未运行。请先启动后端服务：python main.py")
            elif "超时" in error_msg:
                raise Exception(f"搜索笔记超时。当前超时设置: {MCPConfig.get_timeout_for_operation('search')}秒")
            else:
                raise Exception(f"搜索笔记失败: {error_msg}")

    async def get_note_content(self, url: str) -> Dict[str, Any]:
        """
        获取小红书笔记的详细内容
        
        Args:
            url: 小红书笔记URL
            
        Returns:
            笔记内容数据
        """
        try:
            logger.info(f"开始获取笔记内容: {url}")
            
            # 调用 FastAPI 服务
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/get_note_content",
                "content",
                params={"url": url}
            )
            
            result = response.json()
            
            # 检查获取结果
            if result.get("success"):
                logger.info(f"笔记内容获取成功: {url}")
            else:
                logger.warning(f"笔记内容获取失败: {url} - {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取笔记内容失败: {error_msg}")
            
            if "503" in error_msg or "不可用" in error_msg:
                raise Exception("FastAPI服务未运行。请先启动后端服务：python main.py")
            elif "超时" in error_msg:
                raise Exception(f"获取笔记内容超时。当前超时设置: {MCPConfig.get_timeout_for_operation('content')}秒")
            else:
                raise Exception(f"获取笔记内容失败: {error_msg}")

    async def analyze_note(self, url: str) -> Dict[str, Any]:
        """
        分析小红书笔记内容，提取关键信息和领域标签
        
        Args:
            url: 小红书笔记URL
            
        Returns:
            笔记分析结果
        """
        try:
            logger.info(f"开始分析笔记: {url}")
            
            # 调用 FastAPI 服务
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/analyze_note",
                "analysis",  # 使用新的操作类型
                params={"url": url}
            )
            
            result = response.json()
            
            # 检查分析结果
            if result.get("success"):
                logger.info(f"笔记分析成功: {url}")
            else:
                logger.warning(f"笔记分析失败: {url} - {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"分析笔记失败: {error_msg}")
            
            if "503" in error_msg or "不可用" in error_msg:
                raise Exception("FastAPI服务未运行。请先启动后端服务：python main.py")
            elif "超时" in error_msg:
                raise Exception(f"分析笔记超时。当前超时设置: {MCPConfig.get_timeout_for_operation('analysis')}秒")
            else:
                raise Exception(f"分析笔记失败: {error_msg}")

    async def post_comment(self, url: str, comment: str) -> Dict[str, Any]:
        """
        发布评论到指定小红书笔记
        
        Args:
            url: 小红书笔记URL
            comment: 要发布的评论内容
            
        Returns:
            评论发布结果
        """
        try:
            logger.info(f"开始发布评论: {url}")
            logger.info(f"评论内容: {comment}")
            
            # 调用 FastAPI 服务
            response = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/post_comment",
                "comments",  # 使用comments操作类型
                params={"url": url},
                json={"comment": comment}
            )
            
            result = response.json()
            
            # 检查发布结果
            if result.get("success"):
                logger.info(f"评论发布成功: {url}")
            else:
                logger.warning(f"评论发布失败: {url} - {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"发布评论失败: {error_msg}")
            
            if "503" in error_msg or "不可用" in error_msg:
                raise Exception("FastAPI服务未运行。请先启动后端服务：python main.py")
            elif "超时" in error_msg:
                raise Exception(f"发布评论超时。当前超时设置: {MCPConfig.get_timeout_for_operation('comments')}秒")
            else:
                raise Exception(f"发布评论失败: {error_msg}")

    async def get_monitor_status(self) -> Dict[str, Any]:
        """
        获取监控状态
        
        Returns:
            监控状态信息
        """
        try:
            # 尝试连接 FastAPI 服务检查健康状态
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/docs",
                "health_check"
            )
            
            if response.status_code == 200:
                self._monitor_status["is_running"] = True
                self._monitor_status["last_check"] = datetime.now().isoformat()
            else:
                self._monitor_status["is_running"] = False
                
        except Exception as e:
            logger.warning(f"检查服务状态时出错: {str(e)}")
            self._monitor_status["is_running"] = False
        
        return self._monitor_status
    
    async def get_publish_history(self) -> List[Dict[str, Any]]:
        """
        获取发布历史
        
        Returns:
            发布历史记录
        """
        return self._publish_history
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            服务是否健康
        """
        try:
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/docs",
                "health_check"
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def update_monitor_stats(self, success: bool):
        """
        更新监控统计信息
        
        Args:
            success: 操作是否成功
        """
        if success:
            self._monitor_status["success_count"] += 1
        else:
            self._monitor_status["error_count"] += 1
        
        self._monitor_status["last_check"] = datetime.now().isoformat() 