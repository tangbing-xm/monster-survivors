import os
import re
from bs4 import BeautifulSoup

def fix_featured_games():
    print("开始检查并修复Featured Games部分的游戏链接...")
    
    # 获取所有存在的游戏文件
    valid_games = {}
    for root, dirs, files in os.walk('games'):
        for file in files:
            if file.endswith('.html'):
                category = os.path.basename(root)
                game_name = file.replace('.html', '')
                valid_games[f"{category}/{game_name}"] = os.path.join(root, file).replace('\\', '/')
    
    print(f"找到 {len(valid_games)} 个有效的游戏HTML文件")
    
    # 读取index.html文件
    with open('index.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # 获取Featured Games部分
    featured_games_section = soup.select_one('section.py-6.bg-game-card')
    featured_links = featured_games_section.select('.featured-overlay a')
    
    fixed_count = 0
    for link in featured_links:
        if 'href' in link.attrs:
            href = link['href']
            # 检查游戏文件是否存在
            game_path = os.path.join(os.getcwd(), href).replace('\\', '/')
            
            if not os.path.exists(game_path):
                game_name = link.parent.parent.select_one('h3').text.strip()
                print(f"游戏文件不存在: {href}, 游戏名称: {game_name}")
                
                # 尝试找到类似名称的游戏或随机选择一个有效游戏
                replacement_found = False
                
                # 首先尝试找到相似名称的游戏
                game_name_lower = game_name.lower().replace(' ', '_')
                for key in valid_games:
                    if game_name_lower in key:
                        new_href = f"games/{key}.html"
                        link['href'] = new_href
                        replacement_found = True
                        print(f"找到相似名称的替代游戏: {new_href}")
                        break
                
                # 如果没有找到相似名称的游戏，从相同分类中选择
                if not replacement_found:
                    current_category = href.split('/')[1]
                    category_games = [g for g in valid_games if g.startswith(current_category)]
                    
                    if category_games:
                        # 选择该分类的第一个游戏
                        replacement_game = category_games[0]
                        new_href = f"games/{replacement_game}.html"
                        link['href'] = new_href
                        replacement_found = True
                        print(f"从同一分类选择替代游戏: {new_href}")
                
                # 如果还是没找到，随机选择一个有效游戏
                if not replacement_found:
                    import random
                    random_game = random.choice(list(valid_games.keys()))
                    new_href = f"games/{random_game}.html"
                    link['href'] = new_href
                    print(f"随机选择替代游戏: {new_href}")
                
                fixed_count += 1
                
                # 更新游戏图片和描述
                game_container = link.parent.parent
                game_title = os.path.basename(new_href).replace('.html', '').replace('_', ' ').title()
                title_element = game_container.select_one('h3')
                if title_element:
                    title_element.string = game_title
                
                # 更新图片（如果是相同文件名）
                img_element = game_container.select_one('img')
                if img_element:
                    img_element['alt'] = game_title
    
    # 保存修改后的文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    if fixed_count > 0:
        print(f"处理完成! 修复了 {fixed_count} 个Featured Games链接。")
    else:
        print("处理完成! 所有Featured Games链接都是有效的。")

if __name__ == "__main__":
    fix_featured_games() 