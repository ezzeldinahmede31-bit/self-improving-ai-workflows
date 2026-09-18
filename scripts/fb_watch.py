"""Facebook lane of competitor watch: headed Chromium with the owner's saved
session reads public Page timelines, Nemotron picks imitable formats.

Usage:
  fb_watch.py --dry-run
  fb_watch.py
Needs: memory/.sessions/instagram_profile (one-time visible FB login),
display (real :0 or xvfb-run). Secrets from .env.
"""
import asyncio
import json
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = ['asnandentalcenter', 'dentalcareegy', 'zakidentalclinics']

CLEAN = re.compile(r'[_*\[\]()~`>#+=|{}.!-]')


def getenv(name):
    for line in open(os.path.join(BASE, '.env'), encoding='utf-8'):
        if line.startswith(name + '='):
            return line.strip().split('=', 1)[1]
    raise RuntimeError('missing env ' + name)


async def fetch_page(ctx, page_name):
    pg = await ctx.new_page()
    try:
        await pg.goto('https://www.facebook.com/%s' % page_name,
                      wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_timeout(15000)
        for _ in range(5):
            await pg.mouse.wheel(0, 2500)
            await pg.wait_for_timeout(2500)
        body = await pg.inner_text('body')
        blocks = body.split('اكتب تعليقًا')
        posts = []
        months = 'يناير|فبراير|مارس|أبريل|مايو|يونيو|يوليو|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر'
        for b in blocks[:12]:
            b = re.sub(r'\s+', ' ', b).strip()
            dm = re.search(r'(\d{1,2} (?:%s) \d{4}|أمس|منذ \d+ \S+)' % months, b)
            if not dm:
                continue
            text = b[dm.end():].strip()[:320]
            if len(text) < 40:
                continue
            posts.append({'date': dm.group(1), 'text': text})
            if len(posts) >= 5:
                break
        return {'page': page_name, 'posts': posts}
    except Exception as e:
        return {'page': page_name, 'error': str(e)[:120], 'posts': []}
    finally:
        await pg.close()


async def collect():
    from playwright.async_api import async_playwright
    out = []
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(BASE, 'memory', '.sessions', 'instagram_profile'),
            headless=False, args=['--no-sandbox'])
        for slug in PAGES:
            out.append(await fetch_page(ctx, slug))
        await ctx.close()
    return out


def analyze(data):
    key = getenv('NVIDIA_API_KEY')
    lines = []
    for pg in data:
        for ps in pg.get('posts', [])[:3]:
            lines.append('%s (%s): %s' % (pg['page'], ps['date'], ps['text'][:250]))
    prompt = ('Facebook posts of Egyptian dental clinics (page, date, text). Pick top 5 formats '
              'worth structure-level imitation for selling clinic booking systems. Reply numbered '
              'list only, Arabic: 1. [page: post] - [format] - [adaptation].\n' + '\n'.join(lines))
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
    ok = sum(1 for c in data if c.get('posts'))
    print('pages ok: %d/%d' % (ok, len(data)))
    for c in data:
        for ps in c.get('posts', [])[:2]:
            print('-', c['page'], '|', ps['date'], '|', ps['text'][:70])
    if dry:
        return
    digest = 'مرصد فيسبوك للعيادات\n\n' + analyze(data)
    print('sent:', send(digest))


if __name__ == '__main__':
    main()
