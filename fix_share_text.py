from bs4 import BeautifulSoup

def fix_wechat_prompt():
    print("开始修复微信分享提示...")
    
    # 读取index.html文件
    with open('index.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # 查找微信分享链接
    wechat_link = None
    for link in soup.select('a'):
        if link.select_one('i.fa-weixin'):
            wechat_link = link
            break
    
    if wechat_link and 'onclick' in wechat_link.attrs:
        # 修改提示文本为英文
        wechat_link['onclick'] = "alert('Please take a screenshot to share on WeChat');return false;"
        print("已修改微信分享提示为英文")
    
    # 保存修改后的文件
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    
    print("微信分享提示修复完成！")

if __name__ == "__main__":
    fix_wechat_prompt() 