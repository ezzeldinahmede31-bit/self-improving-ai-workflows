"""TikTok lane of competitor watch: headed Chromium (Xvfb-safe) scrapes public
creator pages, ranks by plays, Nemotron picks imitable formats, Telegram digest.

Usage:
  tiktok_watch.py --dry-run   # print only
  tiktok_watch.py              # full run + Telegram send
Needs: display (real :0 or xvfb-run). Secrets from .env: NVIDIA_API_KEY,
TREND_RADAR_BOT_TOKEN, CHAT_ID_TREND_RADAR.
"""
import asyncio
import json
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HANDLES = ['jerry_rdh', 'labtechlee', 'cooperjay', 'meshia_d', 'haleybdaviss']

CLEAN = re.compile(r'[_*\[\]()~`>#+=|{}.!-]')


def getenv(name):
    for line in open(os.path.join(BASE, '.env'), encoding='utf-8'):
        if line.startswith(name + '='):
            return line.strip().split('=', 1)[1]
    raise RuntimeError('missing env ' + name)


def parse_count(s):
    s = (s or '').strip().upper().replace(',', '')
    try:
        if s.endswith('M'):
            return int(float(s[:-1]) * 1000000)
        if s.endswith('K'):
            return int(float(s[:-1]) * 1000)
        return int(float(s))
    except ValueError:
        return 0


async def fetch_handle(browser, handle, per=8):
    ctx = await browser.new_context(
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
        viewport={'width': 1366, 'height': 768}, locale='en-US',
        timezone_id='Africa/Cairo')
    page = await ctx.new_page()
    await page.goto('https://www.tiktok.com/@%s' % handle,
                    wait_until='domcontentloaded', timeout=60000)
    await page.wait_for_timeout(14000)
    for _ in range(5):
        await page.mouse.wheel(0, 2500)
        await page.wait_for_timeout(2500)
    items = await page.eval_on_selector_all(
        'a[href*="/video/"]',
        '''els => els.map(a => {
            const img = a.querySelector('img');
            const box = a.closest('div[data-e2e]') || a.parentElement;
            return {url: a.href, alt: img ? (img.getAttribute('alt') || '') : '',
                    box: (box ? box.innerText : '') || ''};
        })''')
    seen, videos = set(), []
    for it in items:
        m = re.search(r'/video/(\d+)', it['url'])
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        first_line = (it['box'].split('\n')[0] if it['box'] else '').strip()
        plays = parse_count(first_line)
        desc = (it['alt'] or it['box'].replace('\n', ' ')).strip()[:140]
        if not desc and plays == 0:
            continue
        videos.append({'url': 'https://www.tiktok.com/@%s/video/%s' % (handle, m.group(1)),
                       'desc': desc or first_line, 'plays': plays})
        if len(videos) >= per:
            break
    videos.sort(key=lambda v: -v['plays'])
    await page.context.close()
    return {'creator': handle, 'videos': videos}


async def collect():
    from playwright.async_api import async_playwright
    out = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'])
        ctx = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
            viewport={'width': 1366, 'height': 768}, locale='en-US',
            timezone_id='Africa/Cairo')
        _warm = await ctx.new_page()
        await _warm.close()
        for h in HANDLES:
            try:
                out.append(await fetch_handle(browser, h))
            except Exception as e:
                out.append({'creator': h, 'error': str(e)[:120], 'videos': []})
        await browser.close()
    return out


def analyze(data):
    key = getenv('NVIDIA_API_KEY')
    lines = []
    for ch in data:
        for v in ch.get('videos', [])[:3]:
            lines.append('%s | %s (%d plays) %s' % (ch['creator'], v['desc'], v['plays'], v['url']))
    prompt = ('Top TikTok dental-creator videos (creator | caption + plays). Pick top 5 formats '
              'worth structure-level imitation for Egyptian dental clinics. Reply numbered list '
              'only, Arabic: 1. [creator: video] - [format] - [adaptation].\n' + '\n'.join(lines))
    body = json.dumps({'model': 'nvidia/nemotron-3.5-lightning-30b-a3b', 'temperature': 0.2,
                       'max_tokens': 1500,
                       'messages': [{'role': 'user', 'content': prompt}]}).encode()
    req = urllib.request.Request('https://integrate.api.nvidia.com/v1/chat/completions',
                                 data=body,
                                 headers={'Authorization': 'Bearer ' + key,
                                          'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    return r['choices'][0]['message']['content']


def send(text):
    tok = getenv('TREND_RADAR_BOT_TOKEN')
    chat = getenv('CHAT_ID_TREND_RADAR')
    body = json.dumps({'chat_id': chat, 'text': CLEAN.sub('', text)[:3800]}).encode()
    req = urllib.request.Request('https://api.telegram.org/bot%s/sendMessage' % tok,
                                 data=body, headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=60)).get('ok', False)


def main():
    dry = '--dry-run' in sys.argv
    data = asyncio.run(collect())
    ok = sum(1 for c in data if c.get('videos'))
    print('creators ok: %d/%d' % (ok, len(data)))
    for c in data:
        for v in c.get('videos', [])[:3]:
            print('-', c['creator'], '|', v['desc'][:60], '| plays:', v['plays'])
    if dry:
        return
    digest = 'مرصد تيك توك للمنافسين\n\n' + analyze(data)
    print('sent:', send(digest))


if __name__ == '__main__':
    main()
