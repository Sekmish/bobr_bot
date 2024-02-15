from bs4 import BeautifulSoup

html = '<img width="640" height="590" src="https://sysert.life/wp-content/uploads/2022/10/marshruty-1.jpg" class="vc_single_image-img attachment-large" alt="Расписание маршрута №113 Бобровский-Екатеринбург" loading="lazy" title="Расписание маршрута №113 Бобровский-Екатеринбург">'
soup = BeautifulSoup(html, 'html.parser')
img_tag = soup.find('img')
src = img_tag['src']
print(src)