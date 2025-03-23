import os
from bs4 import BeautifulSoup

# 读取index.html文件
with open('index.html', 'r', encoding='utf-8') as file:
    content = file.read()

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(content, 'html.parser')

# 查找Popular Games的section
# 这里找到py-8 bg-gray-900类的section，且内部包含"Popular Games"标题的部分
sections = soup.find_all('section', class_='py-8 bg-gray-900')
for section in sections:
    h2 = section.find('h2', string='Popular Games')
    if h2:
        print("找到Popular Games部分，正在删除...")
        section.decompose()  # 完全删除这个section
        break

# 将修改后的内容写回文件
with open('index.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))

print("完成！已删除Popular Games部分。") 