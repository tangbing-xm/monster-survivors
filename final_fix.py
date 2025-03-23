import os
import re
from bs4 import BeautifulSoup

def final_fix():
    print("开始最终修复index.html文件...")
    
    # 读取index.html文件
    with open('index.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # 1. 确保分类侧边栏的结构正确
    # 首先获取游戏分类父元素
    sidebar_category_div = soup.select_one('.mb-6')
    category_heading = None
    
    for h3 in soup.select('.mb-6 h3'):
        if h3.string == "Game Categories":
            category_heading = h3
            sidebar_category_div = h3.parent
            break
    
    if sidebar_category_div:
        # 获取或创建分类列表
        category_list = sidebar_category_div.select_one('ul')
        if not category_list:
            category_list = soup.new_tag('ul', attrs={'class': 'space-y-2'})
            sidebar_category_div.append(category_list)
        
        # 先清空所有现有链接
        for li in category_list.select('li'):
            li.decompose()
        
        # 检查games目录下存在哪些分类文件夹
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
        
        # 添加"All Games"分类
        all_games_li = soup.new_tag('li')
        all_games_a = soup.new_tag('a', attrs={
            'class': 'hover:text-game-accent transition-colors duration-200 category-link text-game-accent font-bold',
            'data-category': 'all-games',
            'href': 'javascript:void(0);'
        })
        all_games_a.string = 'All Games'
        all_games_li.append(all_games_a)
        category_list.append(all_games_li)
        
        # 添加主要分类
        main_categories = ['action', 'shooter', 'multiplayer', 'adventure', 'sports']
        secondary_categories = ['strategy', 'puzzle', 'idle']
        
        for category in main_categories:
            if category in game_categories:
                li = soup.new_tag('li')
                a = soup.new_tag('a', attrs={
                    'class': 'hover:text-game-accent transition-colors duration-200 category-link',
                    'data-category': category,
                    'href': 'javascript:void(0);'
                })
                display_name = category_map.get(category, category.title())
                a.string = display_name
                li.append(a)
                category_list.append(li)
        
        # 添加"More"下拉菜单
        more_li = soup.new_tag('li', attrs={'class': 'relative group'})
        more_a = soup.new_tag('a', attrs={'class': 'flex items-center hover:text-game-accent', 'href': '#'})
        more_a.string = 'More '
        more_icon = soup.new_tag('i', attrs={'class': 'fas fa-chevron-down ml-1 text-xs'})
        more_a.append(more_icon)
        more_li.append(more_a)
        
        # 创建下拉菜单
        dropdown_div = soup.new_tag('div', attrs={'class': 'absolute left-0 mt-2 w-48 bg-game-card rounded-md shadow-lg hidden group-hover:block z-10'})
        dropdown_ul = soup.new_tag('ul', attrs={'class': 'py-2'})
        
        # 添加次要分类
        for category in secondary_categories:
            if category in game_categories:
                li = soup.new_tag('li')
                a = soup.new_tag('a', attrs={
                    'class': 'block px-4 py-2 hover:bg-gray-800 hover:text-game-accent transition-colors duration-200 category-link',
                    'data-category': category,
                    'href': 'javascript:void(0);'
                })
                display_name = category_map.get(category, category.title())
                a.string = display_name
                li.append(a)
                dropdown_ul.append(li)
        
        dropdown_div.append(dropdown_ul)
        more_li.append(dropdown_div)
        category_list.append(more_li)
    
    # 2. 将"分享"更改为"Share"
    # 查找"分享"对应的英文文本并替换
    for h3 in soup.select('.mb-6 h3'):
        if h3.string == "分享":
            h3.string = "Share"
            break
    
    # 3. 确保脚本正确
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
    
    # 替换filterGamesByCategory脚本
    filter_script = None
    for script in soup.find_all('script'):
        if script.string and 'category-link' in script.string and 'data-category' in script.string:
            script.string = script_code
            filter_script = script
            break
    
    # 如果没有找到相关脚本，则添加一个新的脚本标签
    if not filter_script:
        new_script = soup.new_tag('script')
        new_script.string = script_code
        soup.body.append(new_script)
    
    # 4. 保存修改后的文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print("最终修复完成！")

if __name__ == "__main__":
    final_fix() 