from datetime import datetime
import pytz
import requests
import re
from bs4 import BeautifulSoup


now = datetime.now()
utc_now = now.astimezone(pytz.timezone('Etc/UTC'))
iso_time = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

sources_dic = {
    'unified': 'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
}

ip_regex = r"(?:\d{1,3}\.){3}\d{1,3}"
zero_ip_regex = r"^0.0.0.0"
url_regex = r"{ip}\s+(\S+)".format(ip=zero_ip_regex)    

# 設定每個檔案最多寫入的資料筆數
max_matches_per_file = 100000


for file, url in sources_dic.items():
  r = requests.get(url)
  # 尋找匹配的資料,  0.0.0.0 之後的第一個空白字元之前的字串
  matches = re.findall(r"{url}".format(url=url_regex), r.text, re.MULTILINE)

  # 計數器
  count = 0

  # 檔案編號
  file_num = 1


  for i, match in enumerate(matches):
    # 這裡可以過濾掉不需要的 ip
    filter_ip = re.findall(r"{ip}".format(ip=ip_regex), match)

    if len(filter_ip) == 0:
      match = '"' + match + '"'

      if count % max_matches_per_file == 0:
        with open(f"{file}_{file_num}.lsrules", 'w') as f:
          f.write("{\n")
          f.write(f"  \"description\": \"Generated from {url}\",\n")
          f.write(f"  \"name\": \"{file}\",\n")
          f.write(f"  \"process\": \"any\",\n")
          f.write(f"  \"denied-remote-notes\": \"Retrieved on {iso_time} from list {file} {file_num}\",\n")
          f.write(f"  \"denied-remote-domains\": [\n")
          f.write(f"    {match},\n")
      else:
          # 寫入現有檔案
          with open(f"{file}_{file_num}.lsrules", 'a') as f:
            if i != len(matches) - 1:
              match = match + ','
            f.write(f"    {match}\n")

      count += 1

      # 如果計數器達到最大值，就開啟新檔案
      if count % max_matches_per_file == 0:
        with open(f"{file}_{file_num}.lsrules", 'a') as f:
          f.write("  ]\n")
          f.write("}")
        file_num += 1 


# 寫入最後一個檔案
with open(f"{file}_{file_num}.lsrules", 'a') as f:
  f.write("  ]\n")
  f.write("}")


# --- 更新 index.html ---
# 讀取 index.html
with open('index.html', 'r') as f:
  html = f.read()  

# 使用 BeautifulSoup 解析 html
soup = BeautifulSoup(html, 'html.parser')

# 找到需要更新的元素
th_data_link = soup.find_all('th', {'class': 'data-link'})[0]
th_subscribe_link = soup.find_all('th', {'class': 'subscribe-link'})[0]
th_data_update = soup.find_all('th', {'class': 'data-update'})[0]

# 清空原有的資料
th_data_link.clear()
th_subscribe_link.clear()
th_data_update.clear()

# 創建 ul 元素
ul_data_link = soup.new_tag('ul')
ul_subscribe_link = soup.new_tag('ul')


for i in range(1, file_num+1):
  li_data_link = soup.new_tag('li')
  a_data_link = soup.new_tag('a', href=f"https://raw.githubusercontent.com/lighter/little-snitch-rules/main/unified_{i}.lsrules")
  a_data_link.string = f"unified_{i}.lsrules"
  li_data_link.append(a_data_link)
  ul_data_link.append(li_data_link)
  
  li_subscribe_link = soup.new_tag('li')
  a_subscribe_link = soup.new_tag('a', href=f"x-littlesnitch:subscribe-rules?url=https://raw.githubusercontent.com/lighter/little-snitch-rules/main/unified_{i}.lsrules")
  a_subscribe_link.string = f"subscribe_unified_{i}.lsrules"
  li_subscribe_link.append(a_subscribe_link)
  ul_subscribe_link.append(li_subscribe_link)
  

th_data_link.append(ul_data_link)
th_subscribe_link.append(ul_subscribe_link)
th_data_update.string = iso_time

# 將 soup 物件縮排整齊
html = soup.prettify()

# 寫入 index.html
with open('index.html', 'w') as f:
  f.write(html)