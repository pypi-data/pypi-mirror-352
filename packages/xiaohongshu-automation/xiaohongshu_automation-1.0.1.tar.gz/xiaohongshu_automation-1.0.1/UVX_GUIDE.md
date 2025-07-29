# uvx 使用指南 - 小红书自动化工具

## 🌟 什么是 uvx？

`uvx` 是 uv 提供的包执行工具，类似于 `npx`，可以直接运行 Python 包而无需先安装到当前环境。这对于 CLI 工具和一次性任务特别有用。

## ✨ uvx 的优势

- 🚀 **无需安装**: 直接运行包，不污染当前环境
- ⚡ **自动管理**: 自动创建临时环境和依赖管理
- 🔒 **隔离运行**: 每次运行都在独立环境中
- 💾 **缓存优化**: 自动缓存环境，再次运行更快
- 🔄 **版本控制**: 可以指定特定版本运行
- 🌐 **多源支持**: 支持 PyPI、TestPyPI、Git 等多种源

## 🚀 基础用法

### 运行小红书自动化工具

```bash
# 启动 FastAPI 服务器
uvx --from xiaohongshu-automation xhs-server

# 启动 MCP 服务器
uvx --from xiaohongshu-automation xhs-mcp
```

### 指定版本

```bash
# 运行特定版本
uvx --from xiaohongshu-automation==1.0.0 xhs-server

# 运行最新预发布版本
uvx --from xiaohongshu-automation --pre xhs-server
```

### 从不同源安装

```bash
# 从 TestPyPI 运行
uvx --index-url https://test.pypi.org/simple/ --from xiaohongshu-automation xhs-server

# 从私有 PyPI 运行
uvx --index-url https://private.pypi.com/simple/ --from xiaohongshu-automation xhs-server
```

## 🔧 开发者用法

### 本地测试

```bash
# 测试本地构建的 wheel 包
uvx --from ./dist/xiaohongshu_automation-1.0.0-py3-none-any.whl xhs-server

# 测试本地源码（需要有 pyproject.toml）
uvx --from . xhs-server
```

### Git 仓库

```bash
# 从 Git 仓库运行
uvx --from git+https://github.com/A1721/xiaohongshu-automation.git xhs-server

# 从特定分支运行
uvx --from git+https://github.com/A1721/xiaohongshu-automation.git@dev xhs-server

# 从特定标签运行
uvx --from git+https://github.com/A1721/xiaohongshu-automation.git@v1.0.0 xhs-server
```

### 带额外依赖

```bash
# 安装额外的可选依赖
uvx --from xiaohongshu-automation[dev] xhs-server

# 临时安装额外包
uvx --with requests --from xiaohongshu-automation xhs-server
```

## 📊 高级功能

### 环境管理

```bash
# 查看 uvx 创建的环境
uv cache dir

# 清理 uvx 缓存
uv cache clean

# 强制重新创建环境
uvx --force --from xiaohongshu-automation xhs-server
```

### 调试模式

```bash
# 详细输出模式
uvx --verbose --from xiaohongshu-automation xhs-server

# 查看 uvx 命令
uvx --help
```

### 配置参数

```bash
# 设置超时
uvx --timeout 60 --from xiaohongshu-automation xhs-server

# 使用特定 Python 版本
uvx --python 3.11 --from xiaohongshu-automation xhs-server
```

## 💡 实用场景

### 快速测试

```bash
# 测试新版本是否正常工作
uvx --from xiaohongshu-automation==1.0.1 xhs-server

# 比较不同版本的行为
uvx --from xiaohongshu-automation==1.0.0 xhs-server  # 终端1
uvx --from xiaohongshu-automation==1.0.1 xhs-server  # 终端2
```

### CI/CD 集成

```bash
# 在 GitHub Actions 中使用
- name: Test package
  run: uvx --from xiaohongshu-automation xhs-server --test

# 在 Docker 中使用
RUN uv pip install uv
RUN uvx --from xiaohongshu-automation xhs-server
```

### 临时使用

```bash
# 一次性运行，不留任何痕迹
uvx --from xiaohongshu-automation xhs-server

# 处理完成后自动清理环境
uvx --clean --from xiaohongshu-automation xhs-server
```

## 🔍 故障排除

### 常见问题

1. **包找不到**
   ```bash
   # 检查包名是否正确
   uvx --verbose --from xiaohongshu-automation xhs-server
   ```

2. **版本冲突**
   ```bash
   # 强制重新创建环境
   uvx --force --from xiaohongshu-automation xhs-server
   ```

3. **网络问题**
   ```bash
   # 使用镜像源
   uvx --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ --from xiaohongshu-automation xhs-server
   ```

### 调试技巧

```bash
# 查看详细日志
uvx --verbose --from xiaohongshu-automation xhs-server

# 检查环境信息
uvx --python-info --from xiaohongshu-automation xhs-server

# 查看安装的包
uvx --show-deps --from xiaohongshu-automation xhs-server
```

## 📚 最佳实践

1. **开发阶段**: 使用 `uvx --from .` 测试本地代码
2. **测试阶段**: 使用 `uvx --index-url testpypi --from package` 测试发布版本
3. **生产使用**: 指定具体版本 `uvx --from package==x.y.z`
4. **CI/CD**: 使用 uvx 进行自动化测试
5. **文档示例**: 在文档中提供 uvx 运行示例

## 🔗 相关资源

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uvx 详细指南](https://docs.astral.sh/uv/guides/tools/)
- [Python 打包最佳实践](https://packaging.python.org/)

---

*使用 uvx 让 Python 包的分发和使用变得更加简单！* 