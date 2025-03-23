import os
import re
import shutil
from bs4 import BeautifulSoup

# 游戏分类映射表 (根据常见的游戏类型进行推断)
category_mapping = {
    # 动作类游戏关键词
    'rush': 'action',
    'fury': 'action',
    'jump': 'action',
    'run': 'action',
    'ninja': 'action',
    'fight': 'action',
    'battle': 'action',
    'adventure': 'adventure',
    'hero': 'action',
    'warrior': 'action',
    
    # 益智类游戏关键词
    'puzzle': 'puzzle',
    'match': 'puzzle',
    'connect': 'puzzle',
    'bubble': 'puzzle',
    'jigsaw': 'puzzle',
    'mahjong': 'puzzle',
    'card': 'puzzle',
    'chess': 'puzzle',
    'solitaire': 'puzzle',
    'word': 'puzzle',
    'quiz': 'puzzle',
    'tangram': 'puzzle',
    
    # 射击类游戏关键词
    'shoot': 'shooter',
    'gun': 'shooter',
    'sniper': 'shooter',
    'missile': 'shooter',
    'archery': 'shooter',
    'arrow': 'shooter',
    
    # 多人游戏关键词
    'multi': 'multiplayer',
    'vs': 'multiplayer',
    'duel': 'multiplayer',
    'team': 'multiplayer',
    'hockey': 'multiplayer',
    
    # 运动和赛车游戏关键词
    'sport': 'sports',
    'soccer': 'sports',
    'football': 'sports',
    'basketball': 'sports',
    'racing': 'sports',
    'car': 'sports',
    'bike': 'sports',
    'moto': 'sports',
    'billiard': 'sports',
    'tennis': 'sports',
    
    # 策略游戏关键词
    'strategy': 'strategy',
    'tower': 'strategy',
    'defense': 'strategy',
    'kingdom': 'strategy',
    'castle': 'strategy',
    'war': 'strategy',
    
    # 闲置游戏关键词
    'idle': 'idle',
    'click': 'idle',
    'tycoon': 'idle',
    'manage': 'idle',
    'build': 'idle'
}

# 创建games目录下的分类文件夹
def create_category_folders():
    # 确保games目录存在
    if not os.path.exists('games'):
        os.makedirs('games')
    
    # 创建各分类目录
    categories = ['action', 'puzzle', 'strategy', 'adventure', 'sports', 'multiplayer', 'idle', 'shooter']
    for category in categories:
        category_path = f'games/{category}'
        if not os.path.exists(category_path):
            os.makedirs(category_path)
            print(f'创建目录：{category_path}')

# 判断游戏名称的分类
def determine_category(game_name):
    game_name_lower = game_name.lower()
    
    # 尝试根据游戏名称中的关键词判断分类
    for keyword, category in category_mapping.items():
        if keyword in game_name_lower:
            return category
    
    # 如果没有匹配的关键词，则根据特定规则判断
    if any(word in game_name_lower for word in ['3d', 'surfer', 'escape']):
        return 'action'
    elif any(word in game_name_lower for word in ['princess', 'makeup', 'dress', 'fashion', 'hair', 'girl']):
        return 'adventure'  # 女孩类游戏通常是冒险或益智类
    elif any(word in game_name_lower for word in ['dog', 'cat', 'pet', 'animal']):
        return 'adventure'  # 宠物类游戏通常是冒险类
    
    # 默认分类
    return 'action'

# 处理游戏文本链接文件
def process_game_links():
    game_data = {}
    
    # 读取游戏文本链接文件
    with open('game_textarea_links.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用正则表达式提取游戏名称和iframe链接
    pattern = r'游戏页面: https://html5games\.com/Game/([^/]+)/[^\n]+\n+Textarea链接: ([^\n]+)'
    matches = re.findall(pattern, content)
    
    for match in matches:
        game_name = match[0]
        iframe_url = match[1]
        
        # 将游戏名称转换为文件名格式
        file_name = game_name.replace('-', '_').lower()
        
        # 根据游戏名称判断分类
        category = determine_category(game_name)
        
        # 存储游戏信息
        game_data[file_name] = {
            'original_name': game_name,
            'iframe_url': iframe_url,
            'category': category
        }
    
    return game_data

# 重新组织游戏文件
def reorganize_games(game_data):
    # 存储移动过的文件记录，避免重复处理
    processed_files = set()
    
    # 首先处理games目录下的文件
    for category_dir in os.listdir('games'):
        category_path = os.path.join('games', category_dir)
        if os.path.isdir(category_path):
            for game_file in os.listdir(category_path):
                if game_file.endswith('.html'):
                    game_name = os.path.splitext(game_file)[0]
                    
                    # 标记为已处理
                    processed_files.add(game_file)
                    
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
    
    # 处理可能存在于其他目录的HTML文件
    for root, dirs, files in os.walk('.'):
        dir_name = os.path.basename(root)
        
        # 跳过games文件夹以及隐藏文件夹
        if 'games' in root.split(os.sep) or dir_name.startswith('.'):
            continue
        
        # 处理其他文件夹中的HTML文件
        for file in files:
            if file.endswith('.html') and file not in processed_files:
                # 转换文件名为标准格式
                game_name = os.path.splitext(file)[0].replace('-', '_').lower()
                
                # 根据数据确定分类，如果没有，则根据文件名判断
                if game_name in game_data:
                    category = game_data[game_name]['category']
                else:
                    # 根据文件名或目录名判断分类
                    if dir_name.lower() in [cat.lower() for cat in category_mapping.values()]:
                        # 根据目录名判断
                        category = dir_name.lower()
                        if category == 'action' or category == 'shooter':
                            category = 'action'
                        elif category == 'racing':
                            category = 'sports'
                    else:
                        # 根据文件名判断
                        category = determine_category(game_name)
                
                # 准备移动文件
                old_path = os.path.join(root, file)
                new_file_name = game_name.replace('-', '_').lower() + '.html'
                new_path = os.path.join('games', category, new_file_name)
                
                # 确保目标文件夹存在
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                
                try:
                    # 复制而不是移动，因为可能有多个引用
                    shutil.copy2(old_path, new_path)
                    print(f"复制 {file} 到 games/{category}/{new_file_name}")
                    processed_files.add(new_file_name)
                except Exception as e:
                    print(f"复制文件时出错: {str(e)}")

# 更新游戏文件中的链接
def update_game_links():
    # 第一阶段：更新index.html中的游戏链接
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            index_content = file.read()
        
        # 更新从大写开头目录的链接到games目录
        pattern = r'href="([A-Z][^"]+)/([^"]+\.html)"'
        
        def replace_link(match):
            dir_name = match.group(1)
            file_name = match.group(2)
            game_name = os.path.splitext(file_name)[0].replace('-', '_').lower()
            
            # 根据目录名确定分类
            if 'Action' in dir_name or 'Shooter' in dir_name:
                category = 'action'
            elif 'Puzzle' in dir_name:
                category = 'puzzle'
            elif 'Strategy' in dir_name or 'Defense' in dir_name:
                category = 'strategy'
            elif 'Adventure' in dir_name or 'RPG' in dir_name:
                category = 'adventure'
            elif 'Sports' in dir_name or 'Racing' in dir_name:
                category = 'sports'
            elif 'Multiplayer' in dir_name:
                category = 'multiplayer'
            elif 'Idle' in dir_name:
                category = 'idle'
            else:
                category = 'action'
            
            return f'href="games/{category}/{game_name}.html"'
        
        updated_content = re.sub(pattern, replace_link, index_content)
        
        # 写回文件
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print("已更新index.html中的游戏链接")
    except Exception as e:
        print(f"更新index.html链接时出错: {str(e)}")

# 主函数
def main():
    print("开始重新组织游戏文件...")
    
    # 创建分类文件夹
    create_category_folders()
    
    # 处理游戏链接获取分类
    print("正在解析游戏链接文件...")
    game_data = process_game_links()
    print(f"共解析到 {len(game_data)} 个游戏信息")
    
    # 重新组织游戏文件
    print("开始重新组织游戏文件...")
    reorganize_games(game_data)
    
    # 更新HTML文件中的链接
    print("更新游戏链接...")
    update_game_links()
    
    print("游戏文件重组完成！")

if __name__ == "__main__":
    main() 