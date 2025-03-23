import os
import re
from bs4 import BeautifulSoup

def fix_index_html():
    print("开始修复index.html文件...")
    
    # 读取index.html文件
    with open('index.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # 1. 修复分类链接与实际文件夹匹配问题
    # 首先检查games目录下存在哪些分类文件夹
    game_categories = [d for d in os.listdir('games') if os.path.isdir(os.path.join('games', d))]
    print(f"检测到以下游戏分类: {game_categories}")
    
    # 构建分类映射表
    category_map = {
        'action': 'Action', 
        'adventure': 'Adventure & RPG',
        'shooter': 'Shooter',
        'multiplayer': 'Multiplayer',
        'puzzle': 'Puzzle',
        'sports': 'Sports & Racing',
        'strategy': 'Strategy & Defense',
        'idle': 'Idle'
    }
    
    # 更新侧边栏分类菜单
    # 查找"游戏分类"对应的英文文本并替换
    category_heading = soup.select_one('.mb-6 h3')
    if category_heading and category_heading.string == "游戏分类":
        category_heading.string = "Game Categories"
    
    # 查找"分享"对应的英文文本并替换
    share_heading = soup.select_one('.mb-6 h3:nth-of-type(2)')
    if share_heading and share_heading.string == "分享":
        share_heading.string = "Share"
    
    # 2. 修复游戏卡片分类问题，确保data-category正确设置
    game_cards = soup.select('#games-container .bg-game-card')
    print(f"检测到 {len(game_cards)} 个游戏卡片")
    
    for card in game_cards:
        link = card.select_one('a')
        if link and 'href' in link.attrs:
            href = link['href']
            # 从链接中提取分类
            match = re.search(r'games/([^/]+)/', href)
            if match:
                folder_category = match.group(1)
                # 更新data-category属性
                card['data-category'] = folder_category
                # 更新分类标签显示
                category_span = card.select_one('.absolute.top-2.right-2')
                if category_span:
                    category_span.string = category_map.get(folder_category, folder_category.title())
    
    # 3. 修复filterGamesByCategory JavaScript逻辑
    script_code = """
    document.addEventListener('DOMContentLoaded', function() {
      // 获取所有分类链接
      const categoryLinks = document.querySelectorAll('.category-link');
      
      // 获取所有游戏卡片
      const allGameCards = document.querySelectorAll('#games-container > div');
      
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
      
      // 默认触发"All Games"分类的点击事件
      const allGamesLink = document.querySelector('.category-link[data-category="all-games"]');
      if (allGamesLink) {
        allGamesLink.click();
      }
    });
    """
    
    # 查找含有filterGamesByCategory的脚本标签并替换内容
    filter_script = None
    for script in soup.find_all('script'):
        if script.string and 'filterGamesByCategory' in script.string:
            script.string = script_code
            filter_script = script
            break
    
    # 如果没有找到相关脚本，则添加一个新的脚本标签
    if not filter_script:
        new_script = soup.new_tag('script')
        new_script.string = script_code
        soup.body.append(new_script)
    
    # 4. 修复"加载更多"按钮脚本
    load_more_script = """
    document.addEventListener('DOMContentLoaded', function() {
      // 初始化显示50个游戏
      const gamesPerPage = 50;
      
      // 加载更多游戏的功能
      const loadMoreBtn = document.getElementById('loadMoreBtn');
      if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
          const allGameCards = document.querySelectorAll('#games-container > div');
          const visibleCategory = document.querySelector('.category-link.text-game-accent').dataset.category;
          
          let visibleCount = 0;
          let moreCount = 0;
          
          allGameCards.forEach(card => {
            if (card.style.display === '') {
              visibleCount++;
            }
          });
          
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
    });
    """
    
    # 查找加载更多的脚本并替换
    load_more_found = False
    for script in soup.find_all('script'):
        if script.string and 'loadMoreBtn' in script.string and 'gamesPerPage' in script.string:
            script.string = load_more_script
            load_more_found = True
            break
    
    # 如果没有找到相关脚本，则添加一个新的脚本标签
    if not load_more_found:
        new_load_script = soup.new_tag('script')
        new_load_script.string = load_more_script
        soup.body.append(new_load_script)
    
    # 5. 保存修改后的文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print("修复完成！")

if __name__ == "__main__":
    fix_index_html() 