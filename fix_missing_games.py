import os
import re
from bs4 import BeautifulSoup

def fix_missing_games():
    print("开始检查并移除不存在游戏文件的游戏卡片...")
    
    # 读取index.html文件
    with open('index.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # 获取所有游戏卡片
    game_cards = soup.select('#games-container .bg-game-card')
    print(f"检测到 {len(game_cards)} 个游戏卡片")
    
    # 记录移除的卡片数量
    removed_count = 0
    valid_count = 0
    
    # 检查每个游戏卡片的链接是否存在
    for card in game_cards:
        link = card.select_one('a')
        if link and 'href' in link.attrs:
            href = link['href']
            game_path = os.path.join(os.getcwd(), href)
            
            # 检查游戏文件是否存在
            if not os.path.exists(game_path):
                # 如果文件不存在，移除该卡片
                game_title = card.select_one('h3').text if card.select_one('h3') else href
                print(f"游戏文件不存在: {href}, 移除卡片: {game_title}")
                card.decompose()
                removed_count += 1
            else:
                valid_count += 1
    
    # 保存修改后的文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print(f"处理完成! 共检查了 {removed_count + valid_count} 个游戏卡片，移除了 {removed_count} 个无效卡片，保留了 {valid_count} 个有效卡片。")

if __name__ == "__main__":
    fix_missing_games() 