# MCP 服务超时问题排查指南

## 🎯 问题总结

**现象**: MCP服务调用成功，但AI执行结果显示失败
**根本原因**: FastAPI后端服务未运行，返回503错误
**解决方案**: 启动后端服务并优化超时配置

## 🔍 问题诊断

### 1. 快速诊断命令

```bash
# 运行超时诊断工具
python test_timeout_improvements.py

# 或者在MCP中调用诊断工具
xiaohongshu_timeout_diagnostic
```

### 2. 手动检查服务状态

```bash
# 检查FastAPI服务是否运行
curl http://localhost:8000/docs

# 或使用PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/docs"
```

## 🚀 解决步骤

### 步骤1: 启动FastAPI后端服务

```bash
# 在项目根目录运行
python main.py
```

**期望输出**:
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 步骤2: 验证服务可用性

```bash
# 访问API文档页面
# 浏览器打开: http://localhost:8000/docs
```

### 步骤3: 启动MCP服务器

```bash
# 在新的终端窗口运行
python mcp_server.py
```

### 步骤4: 配置AI客户端连接

在AI客户端中配置MCP服务器连接（具体配置方式取决于使用的AI客户端）。

## ⚙️ 超时配置优化

### 环境变量配置

根据不同使用场景，设置合适的超时值：

#### 本地开发环境
```bash
export FASTAPI_TIMEOUT=30
export PUBLISH_TIMEOUT=60
export COMMENTS_TIMEOUT=30
export MONITOR_TIMEOUT=15
export HEALTH_CHECK_TIMEOUT=5
export ENABLE_AUTO_RETRY=true
export MAX_RETRIES=3
export RETRY_DELAY=2
```

#### 生产环境
```bash
export FASTAPI_TIMEOUT=60
export PUBLISH_TIMEOUT=120
export COMMENTS_TIMEOUT=60
export MONITOR_TIMEOUT=30
export HEALTH_CHECK_TIMEOUT=10
export ENABLE_AUTO_RETRY=true
export MAX_RETRIES=5
export RETRY_DELAY=3
```

#### 网络较慢环境
```bash
export FASTAPI_TIMEOUT=90
export PUBLISH_TIMEOUT=180
export COMMENTS_TIMEOUT=90
export MONITOR_TIMEOUT=45
export HEALTH_CHECK_TIMEOUT=15
export ENABLE_AUTO_RETRY=true
export MAX_RETRIES=5
export RETRY_DELAY=5
```

### Windows PowerShell 配置
```powershell
$env:FASTAPI_TIMEOUT="60"
$env:PUBLISH_TIMEOUT="120"
$env:COMMENTS_TIMEOUT="60"
$env:ENABLE_AUTO_RETRY="true"
```

## 🛠️ 常见错误及解决方案

### 错误1: "503 Service Unavailable"
**原因**: FastAPI服务未运行
**解决**: 运行 `python main.py` 启动后端服务

### 错误2: "Connection refused" 或 "Connection error"
**原因**: 
- 端口被占用
- 防火墙阻止连接
- 服务绑定地址问题

**解决**:
```bash
# 检查端口占用
netstat -an | findstr 8000  # Windows
lsof -i :8000               # macOS/Linux

# 更换端口（修改main.py）
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### 错误3: "Request timeout"
**原因**: 网络延迟或服务响应慢
**解决**: 
- 增加对应操作的超时时间
- 检查网络连接
- 优化服务性能

### 错误4: "工具调用失败"
**原因**: 参数验证失败或权限问题
**解决**: 
- 检查参数格式
- 确认小红书登录状态
- 检查Cookie有效性

## 📊 性能监控

### 1. 使用内置监控工具
```python
# 调用监控工具
xiaohongshu_monitor
```

### 2. 查看详细日志
```bash
# 启动时开启详细日志
export LOG_LEVEL=DEBUG
python mcp_server.py
```

### 3. 性能指标
- **响应时间**: 正常 < 3秒，慢 > 5秒
- **成功率**: 优秀 > 95%，良好 > 85%
- **错误率**: 正常 < 5%，需关注 > 10%

## 🎯 最佳实践

### 1. 服务启动顺序
1. 启动 FastAPI 后端服务 (`python main.py`)
2. 等待服务完全启动（看到"Application startup complete"）
3. 启动 MCP 服务器 (`python mcp_server.py`)
4. 配置 AI 客户端连接

### 2. 开发调试
```bash
# 使用详细日志模式
export LOG_LEVEL=DEBUG
export DETAILED_ERROR_MSG=true

# 启用自动重试
export ENABLE_AUTO_RETRY=true
export MAX_RETRIES=3
```

### 3. 生产部署
```bash
# 使用生产级配置
export LOG_LEVEL=INFO
export FASTAPI_TIMEOUT=60
export ENABLE_AUTO_RETRY=true

# 使用进程管理器
pm2 start main.py --name "xiaohongshu-api"
pm2 start mcp_server.py --name "xiaohongshu-mcp"
```

## 🔧 故障排除清单

- [ ] FastAPI服务是否启动并监听8000端口？
- [ ] 可以访问 http://localhost:8000/docs 吗？
- [ ] MCP服务器是否成功启动？
- [ ] AI客户端是否正确配置了MCP连接？
- [ ] 超时配置是否合理？
- [ ] 网络连接是否正常？
- [ ] 小红书登录状态是否有效？
- [ ] Cookie文件是否存在且有效？

## 📞 获取帮助

如果问题仍然存在：

1. **运行诊断工具**: `python test_timeout_improvements.py`
2. **收集日志**: 开启DEBUG模式运行
3. **检查系统资源**: CPU、内存使用情况
4. **网络测试**: ping/traceroute到相关服务器

## 🎉 成功验证

当所有配置正确时，你应该看到：

```
✅ MCP服务调用成功
✅ FastAPI后端响应正常  
✅ 工具执行无超时错误
✅ AI获得正确的执行结果
```

---

*最后更新: 2025-06-01*
*版本: v1.0.0* 