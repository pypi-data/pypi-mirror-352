# 大学Logo功能指南

## 概述

已在OmicVerse HTML报告系统中成功添加了大学合作机构logo展示功能。报告底部现在包含"Institutional Collaborations"部分，展示三所大学的logo。

**🔥 重要更新：现在使用base64编码嵌入图片，完全解决了logo显示问题！**

## 添加的大学

1. **斯坦福大学 (Stanford University)**
   - 文件名: `stanford-logo.png`
   - 显示名称: "Stanford University"

2. **中山大学 (Sun Yat-sen University)**
   - 文件名: `sun-yet-logo.png`
   - 显示名称: "Sun Yat-sen University"

3. **北京科技大学 (University of Science and Technology Beijing)**
   - 文件名: `ustb-logo.png`
   - 显示名称: "Beijing University of Science and Technology"

## 实现的功能

### ✅ Base64图片嵌入（核心功能）
- **自动转换**: 图片文件自动转换为base64编码
- **完美兼容**: 无论HTML文件在哪里打开都能正常显示
- **优化处理**: 自动调整图片大小，处理透明背景
- **性能优化**: 压缩优化，减小文件大小

### ✅ 智能回退机制
- 如果图片文件存在，自动转换为base64格式嵌入
- 如果base64转换失败，显示emoji回退效果（🏛️）
- 如果图片文件不存在，显示emoji占位符

### ✅ 响应式设计
- **桌面端**: 三个logo水平排列，间距40px
- **平板端**: 自动换行，调整间距为20px，logo缩小到60x60px
- **移动端**: 垂直排列，间距15px

### ✅ 交互效果
- 鼠标悬停时logo有轻微上移动画
- 背景色变化为主题色
- 阴影效果增强

### ✅ 主题适配
- 支持日间/夜间模式切换
- 颜色和样式自动适配当前主题

## 技术实现

### Base64转换流程
1. **图片读取**: 使用PIL读取图片文件
2. **格式处理**: 自动处理RGBA、透明背景等格式
3. **尺寸优化**: 调整为200x200像素，保持比例
4. **编码转换**: 转换为PNG格式的base64字符串
5. **HTML嵌入**: 使用 `data:image/png;base64,` 格式嵌入

### 关键技术特点
- **无外部依赖**: logo图片完全嵌入HTML，无需外部文件
- **跨平台兼容**: 在任何设备、任何浏览器中都能正常显示
- **优雅降级**: 多层回退机制确保总能显示内容
- **性能优化**: 图片压缩和尺寸优化

## 文件修改

### 1. Python代码 (`_lazy_report.py`)
- 添加 `img_to_base64()` 内部函数
- 更新 `_get_university_logos_html()` 方法使用base64转换
- 实现完整的错误处理和回退机制
- 在 `render_main()` 中自动生成logo HTML

### 2. HTML模板 (`report_template.html`)
- 添加大学logo展示区域
- 使用 `{{university_logos_html}}` 变量动态插入内容
- 包含完整的CSS样式和回退样式

### 3. CSS样式 (`styles.css`)
- `.university-logos` - 容器样式
- `.university-item` - 单个大学项目样式
- `.university-logo` - logo图片样式
- `.university-logo-fallback` - 回退样式
- `.university-name` - 大学名称样式
- 完整的响应式media queries

### 4. 测试图片
- 已包含三个示例logo图片用于测试
- 自动生成的圆形设计logo
- 使用各大学的代表色彩

## 使用方法

### 基本使用
无需任何额外配置，生成报告时会自动包含大学logo：

```python
import omicverse as ov

ov.single.generate_scRNA_report(
    adata, 
    output_path="report.html",
    species='human'
)
```

### 添加实际Logo图片
1. 将logo文件放入 `omicverse/single/templates/img/` 目录
2. 文件名必须为: `stanford-logo.png`, `sun-yet-logo.png`, `ustb-logo.png`
3. 推荐格式: PNG (支持透明背景)
4. 推荐尺寸: 至少200x200像素
5. **自动处理**: 系统会自动转换为base64格式

### 自定义Logo
修改 `_lazy_report.py` 中的 `universities` 列表：

```python
universities = [
    {
        'name': 'Your University<br>Name',
        'filename': 'your-logo.png',
        'alt': 'Your University',
        'fallback_emoji': '🎓'
    },
    # ... 其他大学
]
```

## 技术特性

- **🚀 零依赖显示**: 图片完全嵌入HTML，无需外部文件
- **🔄 智能转换**: 自动base64编码，处理各种图片格式
- **📱 响应式适配**: 完美支持移动端和桌面端
- **🎨 优雅降级**: 多层回退机制保证总能显示内容
- **⚡ 性能优化**: 图片压缩和尺寸优化
- **🌓 主题支持**: 完美适配日夜模式切换
- **♿ 无障碍访问**: 完整的alt属性和语义化标签

## 样式定制

### 调整Logo大小
```css
.university-logo {
    width: 100px;  /* 默认80px */
    height: 100px;
}
```

### 修改布局间距
```css
.logos-container {
    gap: 60px;  /* 默认40px */
}
```

### 自定义悬停效果
```css
.university-item:hover {
    transform: translateY(-5px);  /* 默认-2px */
}
```

## 注意事项

1. **版权遵守**: 使用大学logo时请确保符合各校品牌使用规范
2. **文件命名**: 严格按照指定文件名，区分大小写
3. **图片质量**: 建议使用高分辨率图片以确保显示效果
4. **文件大小**: 建议原始图片控制在2MB以内，系统会自动优化
5. **格式支持**: 支持PNG、JPG等常见格式，PNG推荐（支持透明背景）

## 故障排除

### Logo不显示
- ✅ **已解决**: 使用base64嵌入，不再有路径问题
- 检查文件路径: `templates/img/[文件名]`
- 确认文件名拼写正确
- 查看是否显示了emoji回退效果

### Base64转换失败
- 检查图片文件是否损坏
- 确认PIL库是否正确安装
- 查看控制台错误信息
- 验证图片格式是否支持

### 样式异常
- 检查CSS文件是否正确加载
- 确认浏览器支持CSS Grid和Flexbox
- 清除浏览器缓存

### 响应式问题
- 测试不同屏幕尺寸
- 检查media query断点
- 验证viewport meta标签

## 测试验证

### 快速测试方法
系统已包含测试logo图片，可以直接验证功能：

```python
# 生成测试报告
import omicverse as ov
ov.single.generate_scRNA_report(test_adata, output_path="test_report.html")
# 打开test_report.html查看底部logo显示效果
```

### 验证要点
- [ ] 是否显示三个大学logo
- [ ] 图片是否清晰无模糊
- [ ] 悬停效果是否正常
- [ ] 移动端显示是否正确
- [ ] 夜间模式是否适配

---

**✨ 功能已完全实现并解决显示问题！现在使用base64嵌入确保logo在任何环境下都能正常显示。** 