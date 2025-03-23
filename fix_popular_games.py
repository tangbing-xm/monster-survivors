import os
import random
import re
import glob
from bs4 import BeautifulSoup

# 函数：从games文件夹中获取所有游戏HTML文件的路径
def get_all_game_files():
    all_games = []
    for category in ["action", "puzzle", "strategy", "adventure", "sports", "multiplayer", "idle", "shooter"]:
        category_path = f"games/{category}"
        if os.path.exists(category_path):
            game_files = glob.glob(f"{category_path}/*.html")
            all_games.extend(game_files)
    return all_games

# 函数：获取images文件夹中的所有图片
def get_all_images():
    images = {}
    if os.path.exists("images 3"):
        image_files = glob.glob("images 3/*.jpg")
        for image_path in image_files:
            image_name = os.path.basename(image_path).split('.')[0].lower()
            images[image_name] = image_path
    return images

# 函数：标准化文本以便匹配
def normalize_text(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

# 函数：匹配游戏名称与图片
def find_matching_image(game_title, images_dict):
    normalized_title = normalize_text(game_title)
    
    # 直接匹配
    for image_name, image_path in images_dict.items():
        if normalize_text(image_name) == normalized_title:
            return image_path
    
    # 部分匹配
    for image_name, image_path in images_dict.items():
        if normalize_text(image_name) in normalized_title or normalized_title in normalize_text(image_name):
            return image_path
    
    # 如果找不到匹配，返回随机图片
    return random.choice(list(images_dict.values())) if images_dict else None

# 函数：获取游戏信息（标题、分类、URL等）
def get_game_info(game_file_path, images_dict):
    try:
        category = game_file_path.split('/')[1]  # 从路径获取分类
        filename = os.path.basename(game_file_path)
        game_id = os.path.splitext(filename)[0]  # 获取不带扩展名的文件名
        
        # 从文件中提取游戏标题和iframe URL
        with open(game_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # 提取标题
        title_tag = soup.find('h1', class_='text-3xl')
        title = title_tag.string.strip() if title_tag else game_id.replace('_', ' ').title()
        
        # 提取iframe URL
        iframe = soup.find('iframe')
        iframe_url = iframe['src'] if iframe else None
        
        # 提取评分
        rating_tag = soup.select_one('.fa-star + span')
        rating = rating_tag.string.strip() if rating_tag else "{:.1f}".format(random.uniform(3.0, 5.0))
        
        # 提取游戏次数
        plays_tag = soup.select_one('.fa-play + span')
        plays = plays_tag.string.strip() if plays_tag else f"{random.randint(1, 10)}.{random.randint(1, 9)}k"
        
        # 查找匹配的图片
        image_path = find_matching_image(title, images_dict)
        
        # 如果找不到匹配的图片，使用默认图片
        if not image_path:
            colors = {
                "action": "ff5252", "puzzle": "4caf50", "strategy": "2196f3",
                "adventure": "9c27b0", "sports": "ff9800", "multiplayer": "795548", 
                "idle": "607d8b", "shooter": "f44336"
            }
            color = colors.get(category, "7f5af0")
            image_path = f"https://via.placeholder.com/300x200/{color}/ffffff?text={title}"
        
        return {
            "title": title,
            "category": category,
            "file_path": game_file_path,
            "relative_path": game_file_path,  # 相对路径
            "iframe_url": iframe_url,
            "thumbnail": image_path,
            "rating": rating,
            "plays": plays
        }
    except Exception as e:
        print(f"处理游戏文件 {game_file_path} 时出错: {e}")
        return None

# 生成Popular Games区域的HTML
def generate_popular_games_html(game_info_list, count=8):
    selected_games = random.sample(game_info_list, min(count, len(game_info_list)))
    
    html = '''
    <section class="py-8 bg-gray-900">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-3xl font-bold">Popular Games</h2>
          <div class="flex items-center">
            <span class="mr-3">Sort by:</span>
            <select class="bg-gray-800 text-white py-2 px-4 rounded">
              <option>Most Played</option>
              <option>Highest Rated</option>
              <option>Newest</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
    '''
    
    for game in selected_games:
        # 确定分类按钮颜色
        category_colors = {
            "action": "bg-red-500", 
            "puzzle": "bg-green-500", 
            "strategy": "bg-blue-500",
            "adventure": "bg-purple-500", 
            "sports": "bg-orange-500", 
            "multiplayer": "bg-yellow-500", 
            "idle": "bg-gray-500", 
            "shooter": "bg-pink-500"
        }
        color_class = category_colors.get(game['category'], "bg-game-accent")
        
        # 格式化分类名称
        if game['category'] == "strategy":
            category_display = "Strategy & Defense"
        elif game['category'] == "adventure":
            category_display = "Adventure & RPG"
        elif game['category'] == "sports":
            category_display = "Sports & Racing"
        else:
            category_display = game['category'].title()
        
        html += f'''
          <div class="game-card bg-game-card rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300">
            <a href="{game['relative_path']}" class="block">
              <div class="relative">
                <img src="{game['thumbnail']}" alt="{game['title']}" class="w-full h-48 object-cover">
                <div class="absolute top-2 right-2">
                  <span class="{color_class} text-white text-xs px-3 py-1 rounded-full">{category_display}</span>
                </div>
              </div>
              <div class="p-4">
                <h3 class="font-bold text-xl mb-2 text-white">{game['title']}</h3>
                <div class="flex justify-between items-center">
                  <div class="flex items-center">
                    <i class="fas fa-star text-yellow-400 mr-1"></i>
                    <span>{game['rating']}</span>
                  </div>
                  <div class="flex items-center">
                    <i class="fas fa-play text-gray-400 mr-1"></i>
                    <span>{game['plays']}</span>
                  </div>
                </div>
              </div>
            </a>
          </div>
        '''
    
    html += '''
        </div>
      </div>
    </section>
    '''
    
    return html

# 修复分类过滤功能的JavaScript
def generate_category_filter_js():
    return '''
    <script>
      document.addEventListener('DOMContentLoaded', function() {
        // 获取所有分类按钮
        const categoryButtons = document.querySelectorAll('.category-btn');
        
        // 获取所有游戏卡片
        const allGameCards = document.querySelectorAll('#games-container > div');
        
        // 为每个分类按钮添加点击事件
        categoryButtons.forEach(button => {
          button.addEventListener('click', function() {
            // 移除所有按钮的活动状态
            categoryButtons.forEach(btn => {
              btn.classList.remove('bg-game-accent');
              btn.classList.remove('text-white');
              btn.classList.add('bg-gray-800');
              btn.classList.add('text-gray-300');
            });
            
            // 为当前点击的按钮添加活动状态
            this.classList.remove('bg-gray-800');
            this.classList.remove('text-gray-300');
            this.classList.add('bg-game-accent');
            this.classList.add('text-white');
            
            const selectedCategory = this.getAttribute('data-category');
            
            // 显示或隐藏游戏卡片
            allGameCards.forEach(card => {
              if (selectedCategory === 'all') {
                card.classList.remove('hidden');
              } else {
                if (card.getAttribute('data-category') === selectedCategory) {
                  card.classList.remove('hidden');
                } else {
                  card.classList.add('hidden');
                }
              }
            });
            
            // 隐藏超过50个的卡片
            let visibleCount = 0;
            allGameCards.forEach(card => {
              if (!card.classList.contains('hidden')) {
                visibleCount++;
                if (visibleCount > 50) {
                  card.style.display = 'none';
                } else {
                  card.style.display = '';
                }
              }
            });
            
            // 更新"Load More"按钮状态
            const loadMoreBtn = document.getElementById('loadMoreBtn');
            if (loadMoreBtn) {
              const hiddenCards = Array.from(allGameCards).filter(card => 
                !card.classList.contains('hidden') && card.style.display === 'none'
              );
              
              if (hiddenCards.length > 0) {
                loadMoreBtn.classList.remove('hidden');
              } else {
                loadMoreBtn.classList.add('hidden');
              }
            }
          });
        });
        
        // "Load More"按钮功能
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
          loadMoreBtn.addEventListener('click', function() {
            const hiddenCards = Array.from(allGameCards).filter(card => 
              !card.classList.contains('hidden') && card.style.display === 'none'
            );
            
            // 显示接下来的50个卡片
            hiddenCards.slice(0, 50).forEach(card => {
              card.style.display = '';
            });
            
            // 如果没有更多卡片要显示，隐藏按钮
            if (hiddenCards.length <= 50) {
              loadMoreBtn.classList.add('hidden');
            }
          });
        }
      });
    </script>
    '''

# 主函数
try:
    # 1. 读取index.html文件
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 2. 获取所有游戏文件和图片
    all_game_files = get_all_game_files()
    all_images = get_all_images()
    
    print(f"找到 {len(all_game_files)} 个游戏文件")
    print(f"找到 {len(all_images)} 张游戏图片")
    
    if not all_game_files:
        print("警告：未找到游戏文件，请确保games文件夹中有游戏HTML文件")
    
    # 3. 为所有游戏文件获取游戏信息
    game_info_list = []
    for game_file in all_game_files:
        info = get_game_info(game_file, all_images)
        if info:
            game_info_list.append(info)

    # 4. 查找并移除现有的Popular Games区域（如果存在）
    popular_section = soup.find("section", class_="py-8 bg-gray-900")
    if popular_section:
        popular_section.decompose()
    
    # 5. 生成新的Popular Games区域
    if game_info_list:
        popular_games_html = generate_popular_games_html(game_info_list)
        # 在Weekly Badge Challenge区域后插入新的Popular Games区域
        weekly_badge_section = soup.find("section", class_="py-4 bg-gray-900")
        if weekly_badge_section:
            new_popular_section = BeautifulSoup(popular_games_html, 'html.parser')
            weekly_badge_section.insert_after(new_popular_section)
    
    # 6. 更新游戏容器中的游戏卡片
    games_container = soup.find(id="games-container")
    if games_container:
        # 清空现有内容
        games_container.clear()
        
        # 添加游戏卡片
        for i, game_info in enumerate(game_info_list):
            # 创建新的游戏卡片
            new_card = soup.new_tag('div')
            new_card['class'] = 'bg-game-card rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300'
            new_card['data-category'] = game_info['category']
            
            # 如果是第50个之后的游戏，设置为隐藏
            if i >= 50:
                new_card['style'] = 'display: none;'
            
            # 创建游戏卡片的HTML
            card_html = f'''
            <a href="{game_info['relative_path']}" class="block">
              <div class="relative">
                <img src="{game_info['thumbnail']}" alt="{game_info['title']}" class="w-full h-40 object-cover">
                <span class="absolute top-2 right-2 bg-game-accent text-white text-xs px-2 py-1 rounded">{game_info['category'].title()}</span>
              </div>
              <div class="p-4">
                <h3 class="font-bold text-white mb-2 truncate">{game_info['title']}</h3>
                <div class="flex justify-between items-center">
                  <div class="flex items-center">
                    <i class="fas fa-star text-yellow-400 mr-1"></i>
                    <span class="text-gray-300 text-sm">{game_info['rating']}</span>
                  </div>
                  <div class="flex items-center">
                    <i class="fas fa-play text-gray-400 mr-1"></i>
                    <span class="text-gray-300 text-sm">{game_info['plays']}</span>
                  </div>
                </div>
              </div>
            </a>
            '''
            new_card.append(BeautifulSoup(card_html, 'html.parser'))
            
            # 添加到游戏容器
            games_container.append(new_card)
        
        print(f"已更新 games-container 中的 {min(len(game_info_list), 50)} 个游戏卡片（总共 {len(game_info_list)} 个）")
    else:
        print("错误：找不到游戏容器 (id='games-container')")
    
    # 7. 更新特色游戏
    if game_info_list:
        # 随机选择3个游戏作为特色游戏
        featured_games = random.sample(game_info_list, min(3, len(game_info_list)))
        
        # 找到特色游戏部分
        featured_section = soup.find("section", class_="py-6 bg-game-card")
        if featured_section:
            featured_game_divs = featured_section.find_all("div", class_="featured-game")
            
            # 更新每个特色游戏
            for i, featured_div in enumerate(featured_game_divs):
                if i < len(featured_games):
                    game_info = featured_games[i]
                    
                    # 更新图片
                    img_tag = featured_div.find("img")
                    if img_tag:
                        img_tag["src"] = game_info["thumbnail"]
                        img_tag["alt"] = game_info["title"]
                    
                    # 更新标题和描述
                    title_tag = featured_div.find("h3")
                    if title_tag:
                        title_tag.string = game_info["title"]
                    
                    # 更新"Play Now"链接
                    play_now_link = featured_div.find("a", class_="bg-white")
                    if play_now_link:
                        play_now_link["href"] = game_info["relative_path"]
                    
                    # 添加随机徽章（保持现有的徽章设置）
                    badge_div = featured_div.find("div", class_="badge")
                    if badge_div:
                        badges = ["badge-hot", "badge-new", "badge-featured"]
                        badge_texts = {"badge-hot": "HOT", "badge-new": "NEW", "badge-featured": "FEATURED"}
                        
                        current_badge_class = None
                        for badge_class in badges:
                            if badge_class in badge_div["class"]:
                                current_badge_class = badge_class
                                break
                        
                        if current_badge_class:
                            badge_div.string = badge_texts.get(current_badge_class, "FEATURED")
            
            print(f"已更新 {min(len(featured_games), 3)} 个特色游戏")
        else:
            print("警告：找不到特色游戏部分")
    
    # 8. 修复分类按钮的功能
    # 移除旧的分类过滤脚本
    old_scripts = soup.find_all("script")
    for script in old_scripts:
        if "categoryButtons" in script.text and "allGameCards" in script.text:
            script.decompose()
            
    # 9. 移除示例游戏数据加载函数
    for script in soup.find_all("script"):
        script_content = script.string if script.string else ''
        if "loadGameData" in script_content:
            # 替换整个脚本内容，而不是尝试只替换部分内容
            new_content = """
  document.addEventListener('DOMContentLoaded', function() {
    // 初始化显示50个游戏
    const gamesPerPage = 50;
    let currentlyShown = 50;
    
    // 加载更多游戏的功能
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', function() {
        const allGameCards = document.querySelectorAll('#games-container > div');
        const visibleCategory = document.querySelector('.category-link.text-game-accent').dataset.category;
        
        // 计算当前分类中隐藏的游戏卡片
        const hiddenCards = Array.from(allGameCards).filter(card => {
          if (visibleCategory === 'all-games') {
            return card.style.display === 'none';
          } else {
            return card.dataset.category === visibleCategory.replace('-', '') && card.style.display === 'none';
          }
        });
        
        // 显示接下来的50个卡片
        hiddenCards.slice(0, 50).forEach(card => {
          card.style.display = '';
        });
        
        // 如果没有更多卡片要显示，隐藏按钮
        if (hiddenCards.length <= 50) {
          this.style.display = 'none';
        }
      });
    }
  });
"""
            script.string = new_content
            break  # 只替换第一个包含loadGameData的脚本
    
    # 10. 添加新的分类过滤脚本
    new_script = soup.new_tag("script")
    new_script.string = '''
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
            if (selectedCategory === 'all-games') {
              card.classList.remove('hidden');
              // 只显示前50个游戏
              if (visibleCount < 50) {
                card.style.display = '';
                visibleCount++;
              } else {
                card.style.display = 'none';
              }
            } else {
              const cardCategory = card.getAttribute('data-category');
              if (cardCategory === selectedCategory.replace('-', '')) {
                card.classList.remove('hidden');
                // 只显示前50个匹配分类的游戏
                if (visibleCount < 50) {
                  card.style.display = '';
                  visibleCount++;
                } else {
                  card.style.display = 'none';
                }
              } else {
                card.classList.add('hidden');
                card.style.display = 'none';
              }
            }
          });
          
          // 更新"Load More"按钮状态
          const loadMoreBtn = document.getElementById('loadMoreBtn');
          if (loadMoreBtn) {
            const hiddenCount = Array.from(allGameCards).filter(card => 
              !card.classList.contains('hidden') && card.style.display === 'none'
            ).length;
            
            if (hiddenCount > 0) {
              loadMoreBtn.style.display = '';
            } else {
              loadMoreBtn.style.display = 'none';
            }
          }
        });
      });
    });
    '''
    soup.body.append(new_script)
    
    # 11. 保存修改后的HTML
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    
    print("首页游戏展示和分类过滤功能已更新完成！")
except Exception as e:
    import traceback
    print(f"处理过程中出错: {e}")
    print(traceback.format_exc()) 