#!/usr/bin/env python3
"""
测试Character Reference Generator技能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_basic_functionality():
    """测试基本功能"""
    print("测试基本功能...")
    
    # 导入模块
    try:
        from character_reference_generator import CharacterAnalyzer, PromptGenerator
        print("✓ 模块导入成功")
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False
    
    # 测试分析器
    analyzer = CharacterAnalyzer()
    print("✓ 分析器创建成功")
    
    # 测试提示词生成器
    generator = PromptGenerator()
    print("✓ 提示词生成器创建成功")
    
    return True

def test_with_sample_image():
    """使用示例图像测试"""
    print("\n使用示例图像测试...")
    
    # 查找示例图像
    sample_images = [
        r"C:\Users\shizh\.workbuddy\clipboard-images\clipboard-2026-09-16T02-22-59-526Z-985899f9.jpg",
        r"example_image.jpg"
    ]
    
    image_path = None
    for img in sample_images:
        if os.path.exists(img):
            image_path = img
            break
    
    if not image_path:
        print("⚠ 未找到示例图像，跳过图像测试")
        return True
    
    print(f"使用图像: {image_path}")
    
    # 导入模块
    from character_reference_generator import CharacterAnalyzer, PromptGenerator
    
    # 创建分析器
    analyzer = CharacterAnalyzer()
    
    try:
        # 分析图像
        analysis = analyzer.analyze_image(image_path)
        print("✓ 图像分析成功")
        
        # 创建提示词生成器
        generator = PromptGenerator()
        
        # 生成提示词
        prompt = generator.generate_prompt(analysis)
        print("✓ 提示词生成成功")
        
        # 显示生成的提示词
        print("\n生成的提示词:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
        
        # 保存到文件
        output_file = current_dir / "test_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"✓ 提示词已保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Character Reference Generator 技能测试")
    print("=" * 50)
    
    # 测试基本功能
    if not test_basic_functionality():
        print("\n基本功能测试失败")
        return
    
    # 测试示例图像
    if not test_with_sample_image():
        print("\n示例图像测试失败")
        return
    
    print("\n" + "=" * 50)
    print("所有测试通过！")
    print("=" * 50)

if __name__ == "__main__":
    main()
