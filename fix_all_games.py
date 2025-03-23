import os
import re
from bs4 import BeautifulSoup

def fix_all_games():
    print("开始执行全站游戏链接检查与修复...")
    
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
    
    # 1. 修复Featured Games部分
    fix_featured_games(soup, valid_games)
    
    # 2. 修复普通游戏卡片
    fix_game_cards(soup, valid_games)
    
    # 3. 更新游戏过滤和加载更多功能的JavaScript
    update_filter_script(soup)
    
    # 保存修改后的文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print("全站游戏链接检查与修复完成!")

def fix_featured_games(soup, valid_games):
    """修复特色游戏区域的链接"""
    print("\n开始修复Featured Games部分...")
    
    featured_games_section = soup.select_one('section.py-6.bg-game-card')
    if not featured_games_section:
        print("未找到Featured Games部分")
        return
    
    featured_links = featured_games_section.select('.featured-overlay a')
    
    fixed_count = 0
    for link in featured_links:
        if 'href' in link.attrs:
            href = link['href']
            game_path = os.path.join(os.getcwd(), href).replace('\\', '/')
            
            if not os.path.exists(game_path):
                game_name = link.parent.parent.select_one('h3').text.strip()
                print(f"特色游戏文件不存在: {href}, 游戏名称: {game_name}")
                
                # 修复链接和相关信息
                fixed_count += fix_game_link(link, valid_games, href, game_name)
    
    if fixed_count > 0:
        print(f"修复了 {fixed_count} 个Featured Games链接")
    else:
        print("所有Featured Games链接都是有效的")

def fix_game_cards(soup, valid_games):
    """修复普通游戏卡片的链接"""
    print("\n开始修复游戏卡片...")
    
    game_cards = soup.select('#games-container .bg-game-card')
    if not game_cards:
        print("未找到游戏卡片")
        return
    
    print(f"检测到 {len(game_cards)} 个游戏卡片")
    
    removed_count = 0
    fixed_count = 0
    
    for card in game_cards[:]:  # 使用切片创建副本，避免迭代问题
        link = card.select_one('a')
        if link and 'href' in link.attrs:
            href = link['href']
            game_path = os.path.join(os.getcwd(), href).replace('\\', '/')
            
            if not os.path.exists(game_path):
                game_title = card.select_one('h3').text.strip() if card.select_one('h3') else href
                
                # 策略1：尝试修复链接
                if fix_game_link(link, valid_games, href, game_title):
                    fixed_count += 1
                    print(f"修复了游戏卡片链接: {game_title}")
                else:
                    # 策略2：如果无法修复，删除此卡片
                    print(f"无法修复，移除卡片: {game_title}")
                    card.decompose()
                    removed_count += 1
    
    print(f"游戏卡片处理结果: 修复了 {fixed_count} 个链接，移除了 {removed_count} 个无法修复的卡片")

def fix_game_link(link, valid_games, href, game_name):
    """尝试修复一个游戏链接，成功返回True，失败返回False"""
    replacement_found = False
    
    # 1. 首先尝试找到相似名称的游戏
    game_name_lower = game_name.lower().replace(' ', '_')
    for key in valid_games:
        if game_name_lower in key or key.split('/')[1] in game_name_lower:
            new_href = f"games/{key}.html"
            link['href'] = new_href
            replacement_found = True
            print(f"  找到相似名称的替代游戏: {new_href}")
            
            # 更新游戏标题
            game_container = link.parent
            if game_container.name != 'div':  # 如果父元素不是div，可能是featured game区域
                game_container = game_container.parent
            
            title_element = game_container.select_one('h3')
            if title_element:
                new_title = key.split('/')[1].replace('_', ' ').title()
                title_element.string = new_title
            
            break
    
    # 2. 如果没有找到相似名称的游戏，从相同分类中选择
    if not replacement_found:
        try:
            current_category = href.split('/')[1]
            category_games = [g for g in valid_games if g.startswith(current_category)]
            
            if category_games:
                # 选择该分类的第一个游戏
                replacement_game = category_games[0]
                new_href = f"games/{replacement_game}.html"
                link['href'] = new_href
                replacement_found = True
                print(f"  从同一分类选择替代游戏: {new_href}")
                
                # 更新游戏标题
                game_container = link.parent
                if game_container.name != 'div':
                    game_container = game_container.parent
                
                title_element = game_container.select_one('h3')
                if title_element:
                    new_title = replacement_game.split('/')[1].replace('_', ' ').title()
                    title_element.string = new_title
        except:
            pass
    
    # 3. 如果还是没找到，随机选择一个有效游戏
    if not replacement_found:
        import random
        random_game = random.choice(list(valid_games.keys()))
        new_href = f"games/{random_game}.html"
        link['href'] = new_href
        print(f"  随机选择替代游戏: {new_href}")
        
        # 更新游戏标题
        game_container = link.parent
        if game_container.name != 'div':
            game_container = game_container.parent
        
        title_element = game_container.select_one('h3')
        if title_element:
            new_title = random_game.split('/')[1].replace('_', ' ').title()
            title_element.string = new_title
        
        replacement_found = True
    
    return replacement_found

def update_filter_script(soup):
    """更新游戏过滤和加载更多功能的JavaScript"""
    print("\n更新游戏过滤和加载脚本...")
    
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
          const activeLink = document.querySelector('.category-link.text-game-accent');
          const visibleCategory = activeLink ? activeLink.dataset.category : 'all-games';
          
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
    
    # 检查并添加加载更多按钮（如果不存在）
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

if __name__ == "__main__":
    fix_all_games() 