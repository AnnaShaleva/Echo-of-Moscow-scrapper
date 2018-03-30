# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import os
import re

def extract_text(soup, directory):
    ads_count = 0
    div_teg = soup.find("div", "typical dialog _ga1_on_ contextualizable include-relap-widget")
    if not div_teg:
        print('failed\n')
        return False, ads_count
    p_list = div_teg.find_all('p')
    isB = False
    for p in p_list:
        if (p.find('b')):
            isB = True
            break
    if not isB:
        print('failed\n')
        return False, ads_count
    else:
        text = []
        with open(directory + '/text.txt', 'w', encoding='utf-8') as f:
        #with open(directory + '/text.txt', 'w') as f:
            for p in p_list:
                b = p.find('b')
                if b:
                    line = str(p.text).replace(b.text, '')
                else:
                    line = str(p.text)
                if not 'НОВОСТИ' in line and not 'РЕКЛАМА' in line:
                    text.append(line)
                    f.write(line)
                else:
                    ads_count = ads_count + 1
        f.close()
        print("done")
        return text, ads_count

def create_page_url(url, directory):
    with open(directory + '/page_url.txt', 'w', encoding='utf-8') as f:
        f.write(url)
    f.close()
    print('done')

def extract_audio(soup, directory):
    href = soup.find("a", "load iblock", href=re.compile("^https://cdn.echo.msk.ru/snd/"))["href"]
    with open(directory + '/audio_url.txt', 'w', encoding='utf-8') as f:
        f.write(str(href) + '\n')
    f.close()
    print("done")
    return href

def download_audio(href, directory):
    audio = requests.get(href)
    with open(directory + '/audio.mp3', 'wb') as f:
        f.write(audio.content)
    f.close()
    print('done')

def sample_text_dots(text, directory): #разбивает текст на части по знакам препинания
    data = []
    pattern = re.compile("(?<!\d)[,.!?()]|[,.!?()](?!\d)")
    for line in text:
        s = [x for x in pattern.split(line) if x]
        for element in s:
            data.append(element)
    text = list(str(line).strip() for line in data if str(line).strip())
    file = open(directory+'/in_dots.txt', 'w', encoding='utf8')
    for element in text:
        file.write(element + '\n')
    file.close()
    print('done\n')

def sample_text_coef(text, directory, min_len): #разбивает текст на части с заданным количеством слов min_len
    data = []
    for line in text:
        line = line.split(' ')
        k = 0
        s = ''
        for word in line:
            k = k + 1
            s = s + word + ' '
            if (k != 0 and k % min_len == 0) or word == line[-1]:
                data.append(str(s).strip())
                s = ''
    text = list(str(line).strip() for line in data if str(line).strip())
    file = open(directory + '/in_coef.txt', 'w', encoding='utf8')
    for element in text:
        file.write(element + '\n')
    file.close()
    print('done\n')

count = 0;
valid_urls = []
for url in list(open('urls.txt', 'rt')):
    count = count + 1
    r = requests.get(url.replace('\n', '').replace('\r', ''))
    soup = BeautifulSoup(r.text, 'html.parser')
    directory = './data/{}'.format(count)
    if not os.path.exists(directory):
        os.makedirs(directory) #последняя папка может быть пустая
    print("{}:\nextracting text".format(count))
    text, ads_count = extract_text(soup, directory)
    if text:
        print("creating page_url.txt")
        create_page_url(url, directory)
        print("extracting audio href")
        audio_url = extract_audio(soup, directory)
        print('downloading audio')
        download_audio(audio_url, directory)
        print('writing in.txt')
        text_coef = sample_text_coef(text, directory, min_len = 5) # есть два разных метода разбиения текста
        text_dot = sample_text_dots(text, directory)
        print('writing ads_count.txt')
        with open(directory + '/ads_count.txt', 'wb') as f:
            f.write(str(ads_count).encode())
        f.close()
        valid_urls.append(url)
    else:
        count = count - 1
print("creating valid_urls.txt")
with open('./data/valid_urls.txt', 'wb') as f:
    for line in valid_urls:
        s = line + '\n'
        f.write(s.encode())
f.close()
print("done")

