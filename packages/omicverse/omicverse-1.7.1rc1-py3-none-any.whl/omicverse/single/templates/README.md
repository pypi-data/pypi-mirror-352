# OmicVerse HTML报告模板系统

这个目录包含了用于生成scRNA-seq分析报告的HTML模板文件。

## 文件结构

```
templates/
├── README.md              # 本文件
├── report_template.html   # 主HTML模板
├── sections.html          # 各分析部分的模板
├── styles.css            # CSS样式文件
├── script.js             # JavaScript功能文件
├── img/                  # 大学logo图片目录
│   └── placeholder_logo.md  # logo使用说明
└── test_template.py      # 测试脚本
```

## 新增功能：大学Logo展示

### 功能概述
报告底部现在包含了一个"Institutional Collaborations"（机构合作）部分，用于展示合作大学的logo：

- 斯坦福大学 (Stanford University)
- 中山大学 (Sun Yat-sen University)  
- 北京科技大学 (University of Science and Technology Beijing)

### 图片管理
- 系统会自动检测 `templates/img/` 目录下的logo文件
- 如果图片文件不存在，会显示优雅的回退效果（使用🏛️emoji）
- 支持PNG和JPG格式的图片文件

### 需要的文件
将以下logo文件放入 `templates/img/` 目录：
- `stanford-logo.png`
- `sun-yet-logo.png`  
- `ustb-logo.png`

### 自定义Logo
要添加或修改大学logo，请：

1. **添加图片文件**：将logo文件放入 `templates/img/` 目录
2. **修改Python代码**：在 `_lazy_report.py` 的 `_get_university_logos_html()` 方法中更新大学信息
3. **CSS样式**：如需自定义样式，可修改 `.university-logo` 等CSS类

### 响应式设计
- 桌面端：三个logo水平排列
- 平板端：自动换行，调整间距
- 移动端：垂直排列，优化显示效果

## 模板文件说明

### 1. report_template.html
主HTML模板，包含：
- 页面结构框架
- 侧边栏导航
- 概览部分
- 各分析部分的占位符
- **新增：大学logo展示区域**
- 内联CSS和JS（确保独立性）

### 2. sections.html
包含各个分析部分的HTML模板：
- `qc-section-template`: 质量控制部分
- `expression-section-template`: 基因表达部分
- `pca-section-template`: PCA降维部分
- `batch-section-template`: 批次校正部分
- `clustering-section-template`: 聚类分析部分
- `cellcycle-section-template`: 细胞周期部分
- `benchmark-section-template`: 基准测试部分

### 3. styles.css
CSS样式文件，包含：
- 日夜模式主题变量
- 响应式布局
- 组件样式
- 动画效果
- **新增：大学logo相关样式**

### 4. script.js
JavaScript功能文件，包含：
- 主题切换功能
- 导航功能
- 图片切换
- 动画效果

## 使用方法

### 基本使用
```python
import omicverse as ov

# 生成报告（自动包含大学logo）
ov.single.generate_scRNA_report(
    adata, 
    output_path="my_report.html",
    species='human',
    sample_key='batch'
)
```

### 自定义模板目录
```python
# 使用自定义模板目录
ov.single.generate_scRNA_report(
    adata, 
    output_path="my_report.html",
    template_dir="/path/to/custom/templates"
)
```

## 模板变量

模板中使用 `{{variable_name}}` 格式的占位符，主要变量包括：

### 基本信息
- `{{date}}`: 生成日期
- `{{species}}`: 物种信息
- `{{n_cells}}`: 细胞数量
- `{{n_genes}}`: 基因数量
- `{{timestamp}}`: 生成时间戳

### 统计数据
- `{{n_hvgs}}`: 高变基因数量
- `{{median_genes}}`: 每细胞中位基因数
- `{{median_umis}}`: 每细胞中位UMI数
- `{{n_clusters}}`: 聚类数量
- `{{hvg_percentage}}`: 高变基因百分比

### 进度信息
- `{{progress_percentage}}`: 分析进度百分比
- `{{completed_steps}}`: 已完成步骤数
- `{{total_steps}}`: 总步骤数

### 分析部分
- `{{qc_section}}`: 质量控制部分HTML
- `{{expression_section}}`: 基因表达部分HTML
- `{{pca_section}}`: PCA部分HTML
- `{{batch_section}}`: 批次校正部分HTML
- `{{clustering_section}}`: 聚类部分HTML
- `{{cellcycle_section}}`: 细胞周期部分HTML
- `{{benchmark_section}}`: 基准测试部分HTML
- `{{pipeline_steps}}`: 流程步骤表格行
- **新增：`{{university_logos_html}}`**: 动态生成的大学logo HTML

## 自定义模板

### 1. 修改现有模板
直接编辑模板文件中的HTML、CSS或JavaScript代码。

### 2. 创建新的分析部分
在 `sections.html` 中添加新的 `<template>` 标签：

```html
<template id="my-custom-section-template">
    <div id="mycustom" class="card fade-in">
        <div class="card-header">
            <h2 class="card-title"><i class="card-icon">🔬</i> 自定义分析</h2>
        </div>
        <div class="plot-container">
            <img src="data:image/png;base64,{{my_plot}}" class="plot-img">
        </div>
    </div>
</template>
```

### 3. 在Python代码中使用
```python
# 在Python代码中渲染自定义部分
custom_section = generator.render_section('my-custom', 
    my_plot=my_base64_plot
)
```

### 4. 自定义大学Logo
修改 `_lazy_report.py` 中的 `_get_university_logos_html()` 方法：

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

## 主题定制

### 修改颜色方案
在 `styles.css` 或 `report_template.html` 的 `<style>` 标签中修改CSS变量：

```css
:root {
    --primary: #your-color;        /* 主色调 */
    --primary-light: #your-color;  /* 浅主色 */
    --background: #your-color;     /* 背景色 */
    --card: #your-color;           /* 卡片背景 */
    --text: #your-color;           /* 文字色 */
    /* ... 其他颜色变量 */
}
```

### 大学Logo样式定制
```css
.university-logo {
    width: 100px;           /* 调整logo大小 */
    height: 100px;
    border-radius: 50%;     /* 圆形logo */
}

.university-logos h3 {
    color: #custom-color;   /* 自定义标题颜色 */
}
```

### 添加新主题
可以添加新的CSS类来支持更多主题模式。

## 注意事项

1. **模板备用机制**: 如果模板文件不存在，系统会自动回退到内置的基本模板
2. **图片回退机制**: 如果大学logo图片不存在，会显示emoji占位符
3. **字符编码**: 所有模板文件使用UTF-8编码
4. **图片处理**: 图片会自动转换为base64格式嵌入HTML中
5. **响应式设计**: 模板支持移动端和桌面端显示
6. **浏览器兼容**: 支持现代浏览器（Chrome, Firefox, Safari, Edge）
7. **版权注意**: 使用大学logo时请确保符合相关使用规范

## 故障排除

### 模板文件找不到
```
Warning: Template file not found: [Errno 2] No such file or directory: 'templates/report_template.html'
```
- 确保模板文件存在于正确路径
- 检查文件权限
- 使用绝对路径指定 `template_dir`

### 大学Logo不显示
- 检查图片文件是否存在于 `templates/img/` 目录
- 确认文件名是否正确（区分大小写）
- 检查图片文件格式（推荐PNG）
- 查看是否显示了emoji回退效果

### 变量未替换
如果看到 `{{variable_name}}` 未被替换：
- 检查变量名是否正确
- 确保在Python代码中传递了该变量
- 检查模板语法

### 样式问题
- 检查CSS文件是否正确加载
- 确保CSS变量定义正确
- 检查浏览器开发者工具的样式面板

## 贡献

欢迎提交改进建议和新的模板设计！特别欢迎：
- 新的大学logo和合作机构
- 改进的响应式设计
- 更多主题选项
- 国际化支持 

## 📊 统计功能

OmicVerse 包含匿名使用统计功能，帮助我们了解软件使用情况并改进功能。

### 收集的信息

- 📅 报告生成时间
- 🔒 匿名用户ID（基于机器信息的hash，不可逆）
- 💻 操作系统类型
- 🌍 浏览器语言和时区（仅在查看报告时）
- 📈 基本使用统计

### 隐私保护

✅ **完全匿名**：所有用户信息都经过hash处理  
✅ **无个人信息**：不收集姓名、邮箱等个人信息  
✅ **无文件内容**：不收集分析数据或文件内容  
✅ **可选择退出**：您可以随时禁用统计功能  

### 如何禁用统计

```python
# 方法1：在函数调用时禁用
ov.generate_scRNA_report(
    adata, 
    enable_analytics=False  # 禁用统计
)

# 方法2：设置环境变量
import os
os.environ['OMICVERSE_ANALYTICS'] = 'false'
```

### 测试统计功能

```python
# 运行测试脚本
python test_analytics.py
```

这将生成一个测试HTML页面，您可以在浏览器中打开查看统计功能是否正常工作。

---

## 🔧 高级配置 