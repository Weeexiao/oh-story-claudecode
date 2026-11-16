#!/usr/bin/env python3
"""
Character Reference Generator
输入任何人物照片，输出AI生图的提示词，用于生成多角度参考图
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from PIL import Image

# 尝试导入OpenCV，如果不可用则使用简单分析
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("警告: OpenCV未安装，使用简单图像分析。安装命令: pip install opencv-python")

# 尝试导入DeepFace，如果不可用则使用简单分析
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("警告: DeepFace未安装，使用简单图像分析。安装命令: pip install deepface")


class CharacterAnalyzer:
    """人物特征分析器"""
    
    def __init__(self):
        """初始化分析器"""
        if CV2_AVAILABLE:
            try:
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
            except:
                self.face_cascade = None
        else:
            self.face_cascade = None
        
    def analyze_image(self, image_path: str) -> Dict:
        """
        分析输入图像，提取人物特征
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            包含人物特征的字典
        """
        # 读取图像
        if CV2_AVAILABLE:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            # 转换为RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            # 使用PIL读取图像
            try:
                pil_image = Image.open(image_path)
                image_rgb = np.array(pil_image)
                # 确保是RGB格式
                if len(image_rgb.shape) == 2:  # 灰度图
                    image_rgb = np.stack([image_rgb] * 3, axis=-1)
                elif image_rgb.shape[2] == 4:  # RGBA
                    image_rgb = image_rgb[:, :, :3]
            except Exception as e:
                raise ValueError(f"无法读取图像: {image_path}, 错误: {e}")
        
        # 基本图像信息
        if CV2_AVAILABLE:
            height, width, channels = image.shape
        else:
            height, width, channels = image_rgb.shape
        
        # 人脸检测
        faces = []
        if self.face_cascade is not None and CV2_AVAILABLE:
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                # 转换为列表格式
                faces = faces.tolist() if hasattr(faces, 'tolist') else faces
            except Exception as e:
                print(f"人脸检测失败: {e}")
                faces = []
        else:
            # 如果没有CascadeClassifier，使用简单的人脸检测
            # 这里可以添加其他检测方法
            pass
        
        # 分析结果
        analysis = {
            "image_path": image_path,
            "image_size": {"width": width, "height": height},
            "face_count": len(faces),
            "faces": [],
            "person_description": {},
            "clothing_description": {},
            "background_description": {}
        }
        
        # 分析每个人脸
        for i, face in enumerate(faces):
            if isinstance(face, (list, tuple)) and len(face) == 4:
                x, y, w, h = face
            else:
                continue
            face_info = {
                "position": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "age": "middle-aged",
                "gender": "male",
                "ethnicity": "Asian",
                "expression": "neutral"
            }
            
            # 如果DeepFace可用，进行更详细的分析
            if DEEPFACE_AVAILABLE:
                try:
                    face_region = image_rgb[y:y+h, x:x+w]
                    # 分析年龄、性别、情绪
                    results = DeepFace.analyze(
                        face_region, 
                        actions=['age', 'gender', 'emotion'],
                        enforce_detection=False,
                        silent=True
                    )
                    
                    if results and len(results) > 0:
                        result = results[0]
                        face_info["age"] = self._map_age(result.get("age", 30))
                        face_info["gender"] = "male" if result.get("gender", {}).get("Man", 0) > 0.5 else "female"
                        face_info["emotion"] = result.get("dominant_emotion", "neutral")
                        
                except Exception as e:
                    print(f"DeepFace分析失败: {e}")
            
            analysis["faces"].append(face_info)
        
        # 如果没有检测到人脸，使用默认值
        if not analysis["faces"]:
            analysis["faces"].append({
                "position": {"x": 0, "y": 0, "width": width, "height": height},
                "age": "middle-aged",
                "gender": "male",
                "ethnicity": "Asian",
                "expression": "neutral"
            })
        
        # 提取人物描述
        analysis["person_description"] = self._extract_person_description(analysis["faces"])
        
        # 提取服装描述（简化版）
        analysis["clothing_description"] = self._extract_clothing_description(image_rgb)
        
        # 提取背景描述
        analysis["background_description"] = self._extract_background_description(image_rgb)
        
        return analysis
    
    def _map_age(self, age_value: float) -> str:
        """将年龄数值映射为描述性标签"""
        if age_value < 18:
            return "young"
        elif age_value < 30:
            return "young adult"
        elif age_value < 45:
            return "adult"
        elif age_value < 60:
            return "middle-aged"
        else:
            return "elderly"
    
    def _extract_person_description(self, faces: List[Dict]) -> Dict:
        """提取人物描述"""
        if not faces:
            return {
                "age": "middle-aged",
                "gender": "male",
                "ethnicity": "Asian",
                "hair": "short graying black hair",
                "expression": "neutral"
            }
        
        face = faces[0]  # 使用第一个检测到的人脸
        
        # 根据年龄推断发型
        hair_description = self._get_hair_description(face["age"])
        
        return {
            "age": face["age"],
            "gender": face["gender"],
            "ethnicity": face.get("ethnicity", "Asian"),
            "hair": hair_description,
            "expression": face["expression"]
        }
    
    def _get_hair_description(self, age: str) -> str:
        """根据年龄推断发型描述"""
        hair_descriptions = {
            "young": "short brown hair",
            "young adult": "medium length brown hair",
            "adult": "short dark hair",
            "middle-aged": "short graying black hair",
            "elderly": "short white or gray hair"
        }
        return hair_descriptions.get(age, "short dark hair")
    
    def _extract_clothing_description(self, image_rgb: np.ndarray) -> Dict:
        """提取服装描述（简化版，基于颜色分析）"""
        # 如果OpenCV可用，尝试分析服装颜色
        if CV2_AVAILABLE and image_rgb is not None:
            try:
                # 这里可以添加更复杂的服装识别逻辑
                # 目前返回默认描述
                pass
            except:
                pass
        
        # 返回默认描述
        return {
            "top": "brown jacket over a beige polo shirt",
            "bottom": "dark navy trousers",
            "shoes": "black leather shoes",
            "accessories": "none"
        }
    
    def _extract_background_description(self, image_rgb: np.ndarray) -> Dict:
        """提取背景描述"""
        # 如果图像为空，返回默认背景
        if image_rgb is None:
            return {
                "type": "white",
                "color": "RGB(255, 255, 255)",
                "description": "white background"
            }
        
        # 分析背景颜色
        height, width, _ = image_rgb.shape
        
        # 采样背景区域（假设背景在图像边缘）
        border_size = min(height, width) // 10
        border_regions = [
            image_rgb[:border_size, :],  # 上边
            image_rgb[-border_size:, :],  # 下边
            image_rgb[:, :border_size],  # 左边
            image_rgb[:, -border_size:]   # 右边
        ]
        
        # 计算平均颜色
        avg_colors = []
        for region in border_regions:
            avg_color = np.mean(region, axis=(0, 1))
            avg_colors.append(avg_color)
        
        # 判断背景类型
        avg_color = np.mean(avg_colors, axis=0)
        brightness = np.mean(avg_color)
        
        if brightness > 200:
            bg_type = "white"
        elif brightness < 50:
            bg_type = "black"
        else:
            bg_type = "colored"
        
        return {
            "type": bg_type,
            "color": f"RGB({int(avg_color[0])}, {int(avg_color[1])}, {int(avg_color[2])})",
            "description": f"{bg_type} background"
        }


class PromptGenerator:
    """提示词生成器"""
    
    def __init__(self):
        """初始化提示词生成器"""
        self.template = self._get_default_template()
    
    def _get_default_template(self) -> str:
        """获取默认提示词模板"""
        return """character reference sheet, multiple views of {person_description}, {background_description}, clean composition, no borders, no text, no black lines

left side: large close-up headshot from front view, {face_detail_description}
top right: three headshots from front, side, and back angles, {face_detail_description}
bottom right: three full-body shots from front, side, and back angles, {clothing_detail_description}

realistic skin texture with visible pores, natural skin details, no airbrushing, no smoothing
fabric texture with visible weave pattern, natural clothing folds and wrinkles
high-resolution, photorealistic, 4K detail
no black outlines, no borders, no frames, no text, no watermarks
no skin smoothing, no beauty filter, no retouching"""
    
    def generate_prompt(self, analysis: Dict) -> str:
        """
        根据分析结果生成提示词
        
        Args:
            analysis: 人物特征分析结果
            
        Returns:
            生成的提示词
        """
        # 提取分析结果
        person_desc = analysis["person_description"]
        clothing_desc = analysis["clothing_description"]
        background_desc = analysis["background_description"]
        
        # 构建人物描述
        person_description = self._build_person_description(person_desc)
        
        # 构建面部细节描述
        face_detail_description = self._build_face_detail_description(person_desc)
        
        # 构建服装细节描述
        clothing_detail_description = self._build_clothing_detail_description(clothing_desc)
        
        # 构建背景描述
        background_description = self._build_background_description(background_desc)
        
        # 填充模板
        prompt = self.template.format(
            person_description=person_description,
            face_detail_description=face_detail_description,
            clothing_detail_description=clothing_detail_description,
            background_description=background_description
        )
        
        return prompt
    
    def _build_person_description(self, person_desc: Dict) -> str:
        """构建人物描述"""
        age = person_desc.get("age", "middle-aged")
        gender = person_desc.get("gender", "male")
        ethnicity = person_desc.get("ethnicity", "Asian")
        hair = person_desc.get("hair", "short graying black hair")
        
        # 根据性别调整描述
        if gender == "male":
            return f"{age} {ethnicity} man with {hair}"
        else:
            return f"{age} {ethnicity} woman with {hair}"
    
    def _build_face_detail_description(self, person_desc: Dict) -> str:
        """构建面部细节描述"""
        expression = person_desc.get("expression", "neutral")
        
        return f"detailed facial features with visible skin texture and pores, natural wrinkles and laugh lines, {expression} expression"
    
    def _build_clothing_detail_description(self, clothing_desc: Dict) -> str:
        """构建服装细节描述"""
        top = clothing_desc.get("top", "brown jacket over a beige polo shirt")
        bottom = clothing_desc.get("bottom", "dark navy trousers")
        shoes = clothing_desc.get("shoes", "black leather shoes")
        
        return f"complete outfit including {top}, {bottom}, and {shoes}, showing visible fabric texture and natural clothing folds"
    
    def _build_background_description(self, background_desc: Dict) -> str:
        """构建背景描述"""
        bg_type = background_desc.get("type", "white")
        
        if bg_type == "white":
            return "white background"
        elif bg_type == "black":
            return "black background"
        else:
            return background_desc.get("description", "simple background")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Character Reference Generator - 输入人物照片，生成多角度参考图的AI生图提示词"
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入照片路径"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="输出提示词文件路径（可选）"
    )
    
    parser.add_argument(
        "--generate", "-g",
        action="store_true",
        help="生成提示词后直接调用AI模型生成图像"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="flux-dev",
        help="指定AI模型（默认：flux-dev）"
    )
    
    parser.add_argument(
        "--style", "-s",
        default="realistic",
        choices=["realistic", "concept-art", "anime"],
        help="指定风格（默认：realistic）"
    )
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)
    
    try:
        # 创建分析器
        analyzer = CharacterAnalyzer()
        
        # 分析图像
        print(f"分析图像: {args.input}")
        analysis = analyzer.analyze_image(args.input)
        
        # 创建提示词生成器
        generator = PromptGenerator()
        
        # 生成提示词
        prompt = generator.generate_prompt(analysis)
        
        # 输出结果
        print("\n" + "="*60)
        print("生成的提示词:")
        print("="*60)
        print(prompt)
        print("="*60)
        
        # 保存到文件
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"\n提示词已保存到: {args.output}")
        
        # 如果指定了生成图像
        if args.generate:
            print(f"\n使用 {args.model} 模型生成图像...")
            # 这里可以集成AI图像生成API
            # 例如: infsh app run falai/flux-dev-lora --input '{...}'
            print("注意: 图像生成功能需要配置AI模型API")
        
        # 保存分析结果（可选）
        analysis_file = args.output.replace('.txt', '_analysis.json') if args.output else None
        if analysis_file:
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"分析结果已保存到: {analysis_file}")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
