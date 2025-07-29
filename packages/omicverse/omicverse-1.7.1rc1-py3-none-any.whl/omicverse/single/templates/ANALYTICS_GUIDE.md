# 📊 OmicVerse 统计功能指南

## 概述

OmicVerse 包含了匿名使用统计功能，帮助开发团队了解软件使用情况并持续改进功能。本文档详细介绍了统计功能的工作原理、隐私保护措施和使用方法。

## 🔒 隐私保护承诺

### 我们收集什么

✅ **匿名信息**：
- 报告生成时间戳
- 匿名用户ID（基于机器信息的不可逆hash）
- 操作系统类型（如 Windows、macOS、Linux）
- 浏览器语言设置（仅在查看报告时）
- 时区信息
- 基本使用统计

### 我们不收集什么

❌ **个人信息**：
- 姓名、邮箱等个人身份信息
- 分析数据的具体内容
- 文件路径或文件名
- IP地址或精确位置
- 用户的具体数据

### 技术实现

```python
# 用户信息hash化示例
import hashlib
import platform

machine_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
user_hash = hashlib.md5(machine_info.encode()).hexdigest()[:8]
# 结果: "a5ee06aa" (不可逆转为原始信息)
```

## 🚀 使用方法

### 1. 默认启用统计

```python
import omicverse as ov

# 默认情况下统计功能是启用的
ov.generate_scRNA_report(
    adata,
    output_path="my_report.html"
)
# 输出: 📊 Analytics enabled (use enable_analytics=False to disable)
```

### 2. 禁用统计功能

#### 方法1：函数参数

```python
ov.generate_scRNA_report(
    adata,
    output_path="my_report.html",
    enable_analytics=False  # 明确禁用
)
```

#### 方法2：环境变量

```bash
# 在终端中设置
export OMICVERSE_ANALYTICS=false

# 或在Python中设置
import os
os.environ['OMICVERSE_ANALYTICS'] = 'false'
```

支持的环境变量值：
- **禁用**: `false`, `no`, `0`, `off`, `disable`
- **启用**: `true`, `yes`, `1`, `on`, `enable`

### 3. 自定义项目ID

```python
ov.generate_scRNA_report(
    adata,
    output_path="my_report.html",
    analytics_id="MY-PROJECT-001"  # 自定义项目标识
)
```

## 🔧 技术详情

### 统计数据传输

1. **主要方式**：像素追踪（1x1 透明图片请求）
   ```javascript
   var img = new Image();
   img.src = 'https://analytics.omicverse.org/track.gif?id=...&user=...';
   ```

2. **备用方式**：Google Analytics兼容格式（如果配置）

### 数据格式

发送的统计数据示例：
```json
{
    "id": "OV-001",
    "user": "a5ee06aa",
    "timestamp": "2025-05-31T18:24:47.836Z",
    "platform": "Darwin",
    "language": "zh-CN",
    "timezone": "Asia/Shanghai"
}
```

### 服务器端点

- 主要端点：`https://analytics.omicverse.org/track.gif`
- 备用端点：Google Analytics（如果配置）

## 🧪 测试和验证

### 运行测试脚本

```bash
cd omicverse/single/templates
python test_analytics.py
```

这将：
1. 生成测试统计数据
2. 验证隐私合规性
3. 创建测试HTML页面

### 查看生成的统计代码

```bash
# 打开测试页面
open test_analytics.html

# 在浏览器控制台查看统计信息
# 应该看到类似的输出：
# 📊 Analytics Data: {id: "TEST-001", user: "a5ee06aa", ...}
```

## 📈 统计用途

收集的匿名数据用于：

1. **使用分析**
   - 了解功能使用频率
   - 识别最受欢迎的分析类型
   - 优化软件性能

2. **技术支持**
   - 了解不同平台的兼容性
   - 优化对不同操作系统的支持
   - 改进错误处理

3. **功能开发**
   - 决定新功能优先级
   - 改进用户界面设计
   - 优化报告生成速度

## ❓ 常见问题

### Q: 统计功能是强制的吗？
A: 不是，您可以随时通过 `enable_analytics=False` 或环境变量禁用。

### Q: 数据会被分享给第三方吗？
A: 不会，所有数据仅用于改进 OmicVerse，不会分享给任何第三方。

### Q: 如何验证没有个人信息被收集？
A: 您可以运行测试脚本查看具体收集的数据，或查看生成的HTML源码。

### Q: 统计服务器在哪里？
A: 目前使用 `analytics.omicverse.org`，如果该服务不可用，统计功能会静默失败，不影响报告生成。

## 🔧 开发者选项

### 自定义统计端点

```python
# 在 _lazy_report.py 中修改
analytics_endpoint = "https://your-custom-analytics.com/track"
```

### 添加自定义统计字段

```python
# 在 _get_analytics_code 方法中添加
data['custom_field'] = 'custom_value'
```

## 📞 联系我们

如果您对统计功能有任何疑问或建议：

- **GitHub Issues**: [OmicVerse Issues](https://github.com/Starlitnightly/omicverse/issues)
- **文档**: [OmicVerse Documentation](https://omicverse.readthedocs.io/)
- **邮箱**: 通过GitHub联系维护者

---

*最后更新: 2025-05-31*  
*版本: 1.0.0* 