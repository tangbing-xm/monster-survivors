import os
import re
from bs4 import BeautifulSoup

def validate_games():
    print("开始验证游戏文件并更新首页显示...")
    
    # 获取所有存在的游戏文件
    valid_games = set()
    for root, dirs, files in os.walk('games'):
        for file in files:
            if file.endswith('.html'):
                relative_path = os.path.join(root, file).replace('\\', '/')
                valid_games.add(relative_path)
    
    print(f"找到 {len(valid_games)} 个有效的游戏HTML文件")
    
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
    
    # 检查每个游戏卡片的链接是否有效
    for card in game_cards[:]:  # 使用切片创建副本，避免迭代问题
        link = card.select_one('a')
        if link and 'href' in link.attrs:
            href = link['href']
            game_path = os.path.join(os.getcwd(), href).replace('\\', '/')
            
            # 检查游戏文件是否存在
            if not os.path.exists(game_path):
                # 如果文件不存在，移除该卡片
                game_title = card.select_one('h3').text.strip() if card.select_one('h3') else href
                print(f"游戏文件不存在: {href}, 移除卡片: {game_title}")
                card.decompose()
                removed_count += 1
            else:
                valid_count += 1
    
    # 保存修改后的文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print(f"处理完成! 保留了 {valid_count} 个有效卡片，移除了 {removed_count} 个无效卡片。")
    
    # 添加加载更多按钮（如果不存在）
    load_more_btn = soup.select_one('#loadMoreBtn')
    if not load_more_btn:
        games_container = soup.select_one('#games-container')
        if games_container:
            # 创建加载更多按钮
            load_more_div = soup.new_tag('div', attrs={'class': 'text-center mt-8'})
            load_more_button = soup.new_tag('button', attrs={
                'id': 'loadMoreBtn',
                'class': 'bg-game-accent hover:bg-game-accent-dark text-white font-bold py-2 px-6 rounded-full',
                'style': 'display: none;'  # 初始隐藏，脚本会控制显示
            })
            load_more_button.string = 'Load More Games'
            load_more_div.append(load_more_button)
            
            # 将按钮添加到游戏容器后面
            games_container.insert_after(load_more_div)
            
            print("添加了'Load More Games'按钮")
    
    # 更新首页上的相关JavaScript
    update_filter_script(soup)
    
    # 保存修改后的文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print("更新完成! 首页现在只显示有效的游戏。")

def update_filter_script(soup):
    """更新游戏过滤和加载更多功能的JavaScript"""
    
    filter_script = """
    document.addEventListener('DOMContentLoaded', function() {
      // 获取所有分类链接
      const categoryLinks = document.querySelectorAll('.category-link');
      
      // 获取所有游戏卡片
      const allGameCards = document.querySelectorAll('#games-container > div.bg-game-card');
      
      // 为每个分类链接添加点击事件
      categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
          e.preventDefault();
          
          // 移除所有链接的激活状态
          categoryLinks.forEach(l => {
            l.classList.remove('text-game-accent');
            l.classList.remove('font-bold');
          });
          
          // 为当前点击的链接添加激活状态
          this.classList.add('text-game-accent');
          this.classList.add('font-bold');
          
          const selectedCategory = this.getAttribute('data-category');
          
          // 显示或隐藏游戏卡片
          let visibleCount = 0;
          allGameCards.forEach(card => {
            // 获取卡片的分类
            const cardCategory = card.getAttribute('data-category');
            
            if (selectedCategory === 'all-games') {
              // 显示前50个游戏
              if (visibleCount < 50) {
                card.style.display = '';
                visibleCount++;
              } else {
                card.style.display = 'none';
              }
            } else if (cardCategory === selectedCategory) {
              // 只显示前50个匹配分类的游戏
              if (visibleCount < 50) {
                card.style.display = '';
                visibleCount++;
              } else {
                card.style.display = 'none';
              }
            } else {
              card.style.display = 'none';
            }
          });
          
          // 更新"Load More"按钮状态
          const loadMoreBtn = document.getElementById('loadMoreBtn');
          if (loadMoreBtn) {
            const hiddenCount = Array.from(allGameCards).filter(card => {
              if (selectedCategory === 'all-games') {
                return card.style.display === 'none';
              } else {
                return card.getAttribute('data-category') === selectedCategory && card.style.display === 'none';
              }
            }).length;
            
            if (hiddenCount > 0) {
              loadMoreBtn.style.display = '';
            } else {
              loadMoreBtn.style.display = 'none';
            }
          }
        });
      });
      
      // 加载更多游戏的功能
      const loadMoreBtn = document.getElementById('loadMoreBtn');
      if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
          const allGameCards = document.querySelectorAll('#games-container > div.bg-game-card');
          const visibleCategory = document.querySelector('.category-link.text-game-accent').dataset.category;
          
          let visibleCount = 0;
          let moreCount = 0;
          
          // 计算当前可见的卡片数量
          allGameCards.forEach(card => {
            if (card.style.display === '') {
              visibleCount++;
            }
          });
          
          // 显示更多的卡片
          allGameCards.forEach(card => {
            if (card.style.display === 'none') {
              const cardCategory = card.dataset.category;
              
              if (visibleCategory === 'all-games' || cardCategory === visibleCategory) {
                if (moreCount < 50) {
                  card.style.display = '';
                  moreCount++;
                }
              }
            }
          });
          
          // 如果没有更多卡片要显示，隐藏按钮
          const remainingHidden = Array.from(allGameCards).filter(card => {
            const cardCategory = card.dataset.category;
            return card.style.display === 'none' && 
                  (visibleCategory === 'all-games' || cardCategory === visibleCategory);
          }).length;
          
          if (remainingHidden === 0) {
            this.style.display = 'none';
          }
        });
      }
      
      // 默认触发"All Games"分类的点击事件
      const allGamesLink = document.querySelector('.category-link[data-category="all-games"]');
      if (allGamesLink) {
        allGamesLink.click();
      }
    });
    """
    
    # 查找并更新过滤脚本
    script_updated = False
    for script in soup.find_all('script'):
        if script.string and ('category-link' in script.string or 'filterGamesByCategory' in script.string):
            script.string = filter_script
            script_updated = True
            break
    
    # 如果没有找到脚本，添加一个新的
    if not script_updated:
        new_script = soup.new_tag('script')
        new_script.string = filter_script
        soup.body.append(new_script)
        print("添加了新的游戏过滤脚本")
    else:
        print("更新了现有的游戏过滤脚本")

if __name__ == "__main__":
    validate_games() 