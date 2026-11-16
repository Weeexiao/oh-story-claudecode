---
name: character-reference-generator
description: "生成人物多角度参考图的AI生图提示词。输入任何人物照片，输出能生成多角度角色参考图（如九宫格、三视图）的详细提示词。用于角色一致性参考、人物设定参考图准备；触发词：人物参考图、多角度参考、角色参考、参考图提示词。"
---

# Character Reference Generator

生成人物多角度参考图的AI生图提示词。输入任何人物照片，输出能生成类似"赵叔-夹克装.png"样式的详细提示词。

## 功能

1. **分析输入照片**：识别照片中的人物特征（年龄、性别、发型、服装、表情等）
2. **生成详细提示词**：创建用于生成多角度参考图的AI生图提示词
3. **多角度布局**：包含正面、侧面、背面的头部特写和全身视图
4. **真实质感**：强调真实皮肤纹理、毛孔、服装布料质感
5. **避免元素**：不包含边框、文字、黑色线条、磨皮效果

## 快速开始

```bash
# 1. 安装依赖（可选，脚本会在缺少依赖时使用简单分析）
pip install opencv-python pillow numpy

# 2. 运行脚本
python character_reference_generator.py --input "path/to/your/photo.jpg"

# 3. 保存提示词到文件
python character_reference_generator.py --input "path/to/your/photo.jpg" --output "prompt.txt"
```

### 示例输出文件

查看 `example_output.txt` 获取实际生成的提示词示例。

## 使用方法

### 基本用法

```bash
# 分析照片并生成提示词
python character_reference_generator.py --input "path/to/photo.jpg"

# 指定输出文件
python character_reference_generator.py --input "path/to/photo.jpg" --output "prompt.txt"

# 生成提示词并直接使用
python character_reference_generator.py --input "path/to/photo.jpg" --generate
```

### 参数说明

- `--input` 或 `-i`：输入照片路径（必需）
- `--output` 或 `-o`：输出提示词文件路径（可选）
- `--generate` 或 `-g`：生成提示词后直接调用AI模型生成图像（可选）
- `--model` 或 `-m`：指定AI模型（默认：flux-dev）
- `--style` 或 `-s`：指定风格（默认：realistic）

## 提示词结构

生成的提示词包含以下部分：

### 1. 基础描述模板

```
character reference sheet, multiple views of [人物描述], white background, clean composition, no borders, no text, no black lines
```

### 2. 多角度视图布局

```
left side: large close-up headshot from front view
top right: three headshots from front, side, and back angles
bottom right: three full-body shots from front, side, and back angles
each headshot positioned directly above the corresponding full-body view
```

### 3. 真实质感要求

```
realistic skin texture with visible pores, natural skin details, no airbrushing, no smoothing
fabric texture with visible weave pattern, natural clothing folds and wrinkles
high-resolution, photorealistic, 4K detail
```

### 4. 避免元素

```
no black outlines, no borders, no frames, no text, no watermarks, no signatures
no cartoon style, no anime style, no illustration style
no skin smoothing, no beauty filter, no retouching
```

## 技术实现

### 特征分析模块

使用计算机视觉技术分析输入照片：

1. **人脸检测**：定位人脸位置和角度
2. **特征提取**：识别年龄、性别、表情
3. **服装分析**：识别服装类型、颜色、材质
4. **发型分析**：识别发型、发色、长度

### 提示词生成模块

基于分析结果生成详细提示词：

1. **人物描述**：年龄、性别、体型、肤色
2. **发型描述**：颜色、长度、风格、细节
3. **服装描述**：上衣、裤子、鞋子、配饰
4. **表情描述**：默认表情、情绪状态
5. **布局描述**：多角度视图的具体安排
6. **质量要求**：分辨率、细节层次、风格

### 示例输出

输入照片：一位穿着棕色夹克的中年男性

输出提示词：
```
character reference sheet, multiple views of middle-aged Asian man with short graying black hair, white background, clean composition, no borders, no text, no black lines

left side: large close-up headshot from front view, detailed facial features with visible skin texture and pores, natural wrinkles and laugh lines, neutral expression
top right: three headshots from front, side, and back angles, detailed facial features with visible skin texture and pores, natural wrinkles and laugh lines, neutral expression
bottom right: three full-body shots from front, side, and back angles, complete outfit including brown jacket over a beige polo shirt, dark navy trousers, and black leather shoes, showing visible fabric texture and natural clothing folds

realistic skin texture with visible pores, natural skin details, no airbrushing, no smoothing
fabric texture with visible weave pattern, natural clothing folds and wrinkles
high-resolution, photorealistic, 4K detail
no black outlines, no borders, no frames, no text, no watermarks
no skin smoothing, no beauty filter, no retouching
```

## 高级功能

### 批量处理

```bash
# 处理整个文件夹的照片
python character_reference_generator.py --input-dir "photos/" --output-dir "prompts/"

# 批量生成图像
python character_reference_generator.py --input-dir "photos/" --generate --output-dir "images/"
```

### 自定义模板

```bash
# 使用自定义提示词模板
python character_reference_generator.py --input "photo.jpg" --template "custom_template.txt"

# 调整布局比例
python character_reference_generator.py --input "photo.jpg" --layout "large-left-3x3"
```

### 风格选项

```bash
# 写实风格（默认）
python character_reference_generator.py --input "photo.jpg" --style realistic

# 概念艺术风格
python character_reference_generator.py --input "photo.jpg" --style concept-art

# 动漫风格
python character_reference_generator.py --input "photo.jpg" --style anime
```

## 与AI图像生成工具结合使用

### 使用FLUX模型

```bash
# 生成提示词
python character_reference_generator.py --input "photo.jpg" --output "prompt.txt"

# 使用inference.sh生成图像
infsh app run falai/flux-dev-lora --input '{
  "prompt": "'$(cat prompt.txt)'",
  "width": 1024,
  "height": 1024
}'
```

### 使用MiniMax H3

```bash
# 生成提示词
python character_reference_generator.py --input "photo.jpg" --output "prompt.txt"

# 使用MiniMax H3生成视频（需要配置API）
# 提示词可用于生成角色参考视频
```

### 使用Stable Diffusion

```bash
# 生成提示词
python character_reference_generator.py --input "photo.jpg" --output "prompt.txt"

# 使用Automatic1111 WebUI
# 将提示词粘贴到正向提示词框中
```

## 依赖项

### 基础依赖（必需）
```bash
pip install pillow numpy
```

### 可选依赖（增强分析能力）
```bash
# OpenCV（用于人脸检测和颜色分析）
pip install opencv-python

# DeepFace（用于年龄、性别、情绪分析）
pip install deepface tensorflow
```

### 使用虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 提示词优化建议

### 调整人物描述
- 如果自动生成的描述不准确，可以手动修改人物描述部分
- 添加更多细节：如"with a warm smile"、"wearing glasses"等

### 调整布局
- 修改"left side"、"top right"、"bottom right"部分来改变布局
- 可以添加更多视角，如"three-quarter view"

### 调整质感要求
- 根据需要修改"realistic skin texture"部分
- 可以添加"studio lighting"、"professional photography"等关键词

### 避免元素
- 根据需要修改"no black outlines"部分
- 可以添加"no text"、"no watermarks"、"no signatures"等

## 注意事项

1. 输入照片应清晰，光线充足
2. 人物应占据照片的主要部分
3. 背景相对简单效果更好
4. 生成的提示词可用于各种AI图像生成模型
5. 建议使用高分辨率模型（如FLUX、Stable Diffusion XL）获得最佳效果
6. 提示词可能需要根据具体AI模型进行微调
7. 对于复杂场景，可能需要多次生成和调整

## 相关技能

- `character-design-sheet`：更全面的角色设计表生成
- `minimax-h3-storyboard-director`：MiniMax H3视频生成提示词
- `ai-image-generation`：AI图像生成基础技能

## 更新日志

### v1.0.0
- 初始版本
- 基本特征分析和提示词生成
- 支持多角度布局
- 真实质感要求
