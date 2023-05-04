from datetime import datetime
import pytz
import requests
import re

now = datetime.now()
utc_now = now.astimezone(pytz.timezone('Etc/UTC'))
iso_time = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

sources_dic = {
    'unified.lsrules': 'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
}


ip_regex = r"(?:\d{1,3}\.){3}\d{1,3}"
zero_ip_regex = r"0.0.0.0"
url_regex = r"{ip}\s+(\S+)".format(ip=zero_ip_regex)

for file, url in sources_dic.items():

  r = requests.get(url)
  # 尋找匹配的資料,  0.0.0.0 之後的第一個空白字元之前的字串
  matches = re.findall(r"{url}".format(url=url_regex), r.text, re.MULTILINE)
  
  with open(file, 'w') as f:
      f.write("{\n")
      f.write(f"  \"description\": \"Generated from {url}\",\n")
      f.write(f"  \"name\": \"{file}\",\n")
      f.write(
          f"  \"denied-remote-notes\": \"Retrieved on {iso_time} from list {file}\",\n")
      f.write(f"  \"denied-remote-hosts\": [\n")

      for i, match in enumerate(matches):
         # 這裡可以過濾掉不需要的 ip
         filter_ip = re.findall(r"{ip}".format(ip=ip_regex), match)
         if len(filter_ip) == 0:
            match = '"' + match + '"'
            if i != len(matches) - 1:
               match = match + ','
            f.write(f"    {match}\n")

      f.write("  ]\n")
      f.write("}\n")
