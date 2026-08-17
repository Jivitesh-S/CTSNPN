import requests, re, time
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36', 'Accept-Language': 'en-US,en;q=0.9'}

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","noscript","svg","nav","footer","header","aside","iframe","form"]):
        tag.decompose()
    main = soup.find("main") or soup.body or soup
    lines = []
    for tag in main.find_all(["h1","h2","h3","h4","h5","h6","p","li"]):
        text = tag.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        if len(text) >= 20:
            lines.append(text)
    seen, unique = set(), []
    for line in lines:
        key = line[:80]
        if key in seen: continue
        seen.add(key); unique.append(line)
    return "\n".join(unique)

candidates = {
    'P022': ['https://en.wikipedia.org/wiki/Samsung_Galaxy_S26',
             'https://www.gadgets360.com/mobiles/news/samsung-galaxy-s26-plus-launch-price-india-specifications-features-sale-11135193'],
    'P024': ['https://en.wikipedia.org/wiki/Samsung_Galaxy_Z_Flip_7',
             'https://news.samsung.com/global/samsung-galaxy-z-flip7-a-pocket-sized-ai-powerhouse-with-a-new-edge-to-edge-flexwindow'],
    'P025': ['https://en.wikipedia.org/wiki/Samsung_Galaxy_Z_Flip_7',
             'https://www.gsmarena.com/samsung_galaxy_z_flip7_fe-13110.php'],
    'A019': ['https://www.sammobile.com/news/samsung-galaxy-ring-2-everything-to-know/',
             'https://en.wikipedia.org/wiki/Samsung_Galaxy_Ring'],
}

for pid, urls in candidates.items():
    for u in urls:
        try:
            r = requests.get(u, headers=headers, timeout=25, allow_redirects=True)
            content = extract_text(r.text) if r.status_code == 200 else ''
            print(f'{pid}: {r.status_code} {u} | textlen={len(content)}')
        except Exception as e:
            print(f'{pid}: ERR {u}: {str(e)[:60]}')
        time.sleep(1.5)