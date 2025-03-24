#!/usr/bin/env python3
import os
import re

def fix_back_to_home_links():
    """修复所有游戏页面中的'Back to Home'链接"""
    # 游戏分类目录
    categories = ['action', 'adventure', 'puzzle', 'strategy', 'sports', 'shooter', 'multiplayer', 'idle']
    games_dir = os.path.join(os.getcwd(), 'games')
    
    # 记录处理的文件数量
    fixed_count = 0
    
    # 遍历所有游戏分类
    for category in categories:
        category_path = os.path.join(games_dir, category)
        if not os.path.isdir(category_path):
            print(f"警告: 找不到分类目录 {category_path}")
            continue
        
        # 处理分类下的所有游戏文件
        for game_file in os.listdir(category_path):
            if not game_file.endswith('.html'):
                continue
                
            file_path = os.path.join(category_path, game_file)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复导航栏链接
            content = re.sub(r'<a href="index\.html"', '<a href="../../index.html"', content)
            
            # 修复"Back to Home"链接
            content = re.sub(
                r'<a href="index\.html" class="text-gray-400 hover:text-game-accent">',
                '<a href="../../index.html" class="text-gray-400 hover:text-game-accent">',
                content
            )
            
            # 保存修改后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            fixed_count += 1
            
    print(f"已修复 {fixed_count} 个游戏页面中的'Back to Home'链接")

if __name__ == "__main__":
    fix_back_to_home_links() 