import os
import re
import shutil
from bs4 import BeautifulSoup
import requests
import time
import random
from urllib.parse import urlparse

# 游戏分类映射表
category_mapping = {
    'Action': 'action',
    'Puzzle': 'puzzle',
    'Strategy': 'strategy',
    'Adventure': 'adventure',
    'Sport': 'sports',
    'Racing': 'sports',
    'Multiplayer': 'multiplayer',
    'Idle': 'idle',
    'Shooter': 'shooter',
    'Jump & Run': 'action',
    'Arcade': 'action',
    'Match 3': 'puzzle',
    'Bubble Shooter': 'puzzle',
    'Quiz': 'puzzle',
    'Cards': 'puzzle',
    'Girls': 'adventure'
}

# 创建games目录下的分类文件夹
def create_category_folders():
    # 确保games目录存在
    if not os.path.exists('games'):
        os.makedirs('games')
    
    # 创建各分类目录
    for category in set(category_mapping.values()):
        category_path = f'games/{category}'
        if not os.path.exists(category_path):
            os.makedirs(category_path)
            print(f'创建目录：{category_path}')

# 从HTML5games.com获取游戏分类
def get_game_category(url):
    try:
        # 从URL中提取游戏名称
        game_name = url.split('/')[-2].replace('-', ' ')
        
        # 随机延迟，避免请求过于频繁
        time.sleep(random.uniform(0.5, 1.5))
        
        # 发送请求获取页面内容
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找分类信息
            category_links = soup.select('a[href^="/"][i^="icon-category-"]')
            if category_links:
                # 选择第一个分类
                for link in category_links:
                    text = link.text.strip()
                    if text and text != 'New' and text != 'Best':
                        print(f"游戏 {game_name} 分类: {text}")
                        return text
        
        print(f"无法获取 {game_name} 的分类，使用默认分类：Action")
        return 'Action'  # 默认分类
    except Exception as e:
        print(f"获取游戏分类出错：{str(e)}，使用默认分类：Action")
        return 'Action'  # 默认分类

# 处理游戏文本链接文件
def process_game_links():
    game_data = {}
    
    # 读取游戏文本链接文件
    with open('game_textarea_links.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用正则表达式提取游戏页面URL和iframe链接
    pattern = r'游戏页面: (https://html5games\.com/Game/([^/]+)/[^\n]+)\n+Textarea链接: ([^\n]+)'
    matches = re.findall(pattern, content)
    
    for match in matches:
        game_url = match[0]
        game_name = match[1].replace('-', '_').lower()
        iframe_url = match[2]
        
        # 获取游戏分类
        category = get_game_category(game_url)
        mapped_category = category_mapping.get(category, 'action')
        
        # 存储游戏信息
        game_data[game_name] = {
            'original_url': game_url,
            'iframe_url': iframe_url,
            'category': mapped_category
        }
        
    return game_data

# 重新组织游戏文件
def reorganize_games(game_data):
    # 首先处理games目录下的文件
    for category_dir in os.listdir('games'):
        category_path = os.path.join('games', category_dir)
        if os.path.isdir(category_path):
            for game_file in os.listdir(category_path):
                if game_file.endswith('.html'):
                    game_name = os.path.splitext(game_file)[0]
                    
                    # 如果在游戏数据中找到了这个游戏
                    if game_name in game_data:
                        new_category = game_data[game_name]['category']
                        # 如果分类需要改变
                        if category_dir != new_category:
                            old_path = os.path.join(category_path, game_file)
                            new_path = os.path.join('games', new_category, game_file)
                            
                            # 确保目标文件夹存在
                            os.makedirs(os.path.dirname(new_path), exist_ok=True)
                            
                            try:
                                shutil.move(old_path, new_path)
                                print(f"移动 {game_file} 从 {category_dir} 到 {new_category}")
                            except Exception as e:
                                print(f"移动文件时出错: {str(e)}")
    
    # 处理大写字母开头的目录中的HTML文件
    for root, dirs, files in os.walk('.'):
        if os.path.basename(root).istitle() and os.path.basename(root) != 'games':
            for file in files:
                if file.endswith('.html'):
                    game_name = os.path.splitext(file)[0].replace('-', '_').lower()
                    
                    # 根据文件名确定分类
                    if game_name in game_data:
                        category = game_data[game_name]['category']
                    else:
                        # 如果没有匹配的游戏数据，根据目录名判断
                        dir_name = os.path.basename(root)
                        category = category_mapping.get(dir_name, 'action')
                    
                    old_path = os.path.join(root, file)
                    new_file_name = game_name + '.html'
                    new_path = os.path.join('games', category, new_file_name)
                    
                    # 确保目标文件夹存在
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    try:
                        shutil.copy(old_path, new_path)
                        print(f"复制 {file} 到 {category}/{new_file_name}")
                    except Exception as e:
                        print(f"复制文件时出错: {str(e)}")

# 主函数
def main():
    print("开始重新组织游戏文件...")
    
    # 创建分类文件夹
    create_category_folders()
    
    # 处理游戏链接获取分类
    print("正在获取游戏分类信息...")
    game_data = process_game_links()
    print(f"共获取到 {len(game_data)} 个游戏的分类信息")
    
    # 重新组织游戏文件
    print("开始重新组织游戏文件...")
    reorganize_games(game_data)
    
    print("游戏文件重组完成！")

if __name__ == "__main__":
    main() 