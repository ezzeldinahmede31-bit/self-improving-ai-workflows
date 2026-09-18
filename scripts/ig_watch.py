"""Instagram lane of competitor watch: headed Chromium with the owner's saved
session reads public reels grids, visits top reels for captions, Nemotron
picks imitable formats, Telegram digest.

Usage:
  ig_watch.py --dry-run
  ig_watch.py
Needs: memory/.sessions/instagram_profile (one-time visible IG login),
display (real :0 or xvfb-run). Secrets from .env.
"""
import asyncio
import json
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROFILES = ['jerry_rdh', 'dentalchick_', 'meshia_d']

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


async def fetch_profile(ctx, handle):
    pg = await ctx.new_page()
    try:
        await pg.goto('https://www.instagram.com/%s/reels/' % handle,
                      wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_timeout(14000)
        for _ in range(4):
            await pg.mouse.wheel(0, 2500)
            await pg.wait_for_timeout(2500)
        hrefs = await pg.eval_on_selector_all(
            'a[href*="/reel/"]',
            'els => els.map(a => a.getAttribute("href") || "")')
        counts = await pg.eval_on_selector_all(
            'a[href*="/reel/"]',
            'els => els.map(a => (a.innerText || "").trim().split("\\n")[0])')
        items = []
        seen = set()
        for h, c in zip(hrefs, counts):
            m = re.search(r'/reel/([\w\-_]+)', h)
            if not m or m.group(1) in seen:
                continue
            seen.add(m.group(1))
            items.append({'code': m.group(1), 'plays': parse_count(c)})
            if len(items) >= 10:
                break
        items.sort(key=lambda v: -v['plays'])
        top = []
        for it in items[:3]:
            try:
                await pg.goto('https://www.instagram.com/reel/%s/' % it['code'],
                              wait_until='domcontentloaded', timeout=45000)
                await pg.wait_for_timeout(7000)
                text = await pg.inner_text('body')
                text = re.sub(r'\s+', ' ', text)
                m2 = re.search(r'([\d,]+)\s+likes?', text)
                likes = m2.group(1) if m2 else '?'
                cap = text[:400]
                top.append({'url': 'https://www.instagram.com/reel/%s/' % it['code'],
                            'plays': it['plays'], 'likes': likes, 'caption': cap})
            except Exception:
                top.append({'url': 'https://www.instagram.com/reel/%s/' % it['code'],
                            'plays': it['plays'], 'likes': '?', 'caption': ''})
        return {'creator': handle, 'reels': top}
    except Exception as e:
        return {'creator': handle, 'error': str(e)[:120], 'reels': []}
    finally:
        await pg.close()


async def collect():
    from playwright.async_api import async_playwright
    out = []
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(BASE, 'memory', '.sessions', 'instagram_profile'),
            headless=False, args=['--no-sandbox'])
        for h in PROFILES:
            out.append(await fetch_profile(ctx, h))
        await ctx.close()
    return out


def analyze(data):
    key = getenv('NVIDIA_API_KEY')
    lines = []
    for cr in data:
        for r in cr.get('reels', [])[:2]:
            lines.append('%s | %d plays, %s likes: %s %s' % (
                cr['creator'], r['plays'], r['likes'], r['caption'][:220], r['url']))
    prompt = ('Instagram reels of dental creators (creator, plays, likes, caption). Pick top 5 '
              'formats worth structure-level imitation for Egyptian dental clinics. Reply numbered '
              'list only, Arabic: 1. [creator: reel] - [format] - [adaptation].\n' + '\n'.join(lines))
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
    ok = sum(1 for c in data if c.get('reels'))
    print('profiles ok: %d/%d' % (ok, len(data)))
    for c in data:
        for r in c.get('reels', [])[:2]:
            print('-', c['creator'], '| plays:', r['plays'], '|', r['caption'][:70].replace('\n', ' '))
    if dry:
        return
    digest = 'مرصد انستجرام للمنافسين\n\n' + analyze(data)
    print('sent:', send(digest))


if __name__ == '__main__':
    main()
