"""LinkedIn lane of competitor watch: headed Chromium with the owner's saved
session scrapes public company-page posts, ranks by recency+reactions,
Nemotron picks imitable formats, Telegram digest.

Usage:
  linkedin_watch.py --dry-run   # print only
  linkedin_watch.py              # full run + Telegram send
Needs: memory/.sessions/linkedin_profile (one-time visible user login),
display (real :0 or xvfb-run). Secrets from .env.
"""
import asyncio
import json
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMPANIES = ['solutionreach', 'grow-with-adit', 'practice-by-numbers', 'nexhealth-inc',
             'ay-automate', 'gumloop', 'zapier', 'make']

CLEAN = re.compile(r'[_*\[\]()~`>#+=|{}.!-]')


def getenv(name):
    for line in open(os.path.join(BASE, '.env'), encoding='utf-8'):
        if line.startswith(name + '='):
            return line.strip().split('=', 1)[1]
    raise RuntimeError('missing env ' + name)


def parse_posts(body, company):
    chunks = body.split('Feed post')[1:]
    posts = []
    for ch in chunks[:8]:
        lines = [l.strip() for l in ch.split('\n') if l.strip()]
        if not lines:
            continue
        time_m = re.search(r'^(\d+[hdwmo]|just now)', lines[1] if len(lines) > 1 else '')
        when = time_m.group(1) if time_m else '?'
        text_lines = []
        for l in lines[2:]:
            if re.match(r'^\d+\s+(reactions?|reposts?|comments?)', l):
                break
            if l in ('Like', 'Comment', 'Repost', 'Send', 'Follow', company):
                continue
            text_lines.append(l)
        text = ' '.join(text_lines)
        text = re.sub(r'\s*… more\s*$', '', text).strip()[:500]
        rm = re.search(r'(\d+)\s+reactions?', ch)
        reacts = int(rm.group(1)) if rm else 0
        if len(text) > 60:
            posts.append({'when': when, 'text': text, 'reactions': reacts})
    return posts


async def fetch_company(ctx, slug):
    pg = await ctx.new_page()
    try:
        await pg.goto('https://www.linkedin.com/company/%s/posts/' % slug,
                      wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_timeout(18000)
        for _ in range(4):
            await pg.mouse.wheel(0, 2500)
            await pg.wait_for_timeout(2000)
        title = await pg.title()
        if 'not found' in title.lower() or 'page not found' in title.lower():
            return {'company': slug, 'error': 'page-not-found', 'posts': []}
        body = await pg.inner_text('body')
        posts = parse_posts(body, slug)
        return {'company': slug, 'posts': posts}
    except Exception as e:
        return {'company': slug, 'error': str(e)[:120], 'posts': []}
    finally:
        await pg.close()


async def collect():
    from playwright.async_api import async_playwright
    out = []
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(BASE, 'memory', '.sessions', 'linkedin_profile'),
            headless=False, args=['--no-sandbox'])
        for slug in COMPANIES:
            out.append(await fetch_company(ctx, slug))
        await ctx.close()
    return out


def analyze(data):
    key = getenv('NVIDIA_API_KEY')
    lines = []
    for co in data:
        for ps in co.get('posts', [])[:3]:
            lines.append('%s (%s, %d reacts): %s' % (co['company'], ps['when'], ps['reactions'], ps['text'][:280]))
    prompt = ('Competitor LinkedIn posts (company, age, reactions, text). Pick top 5 formats '
              'worth structure-level imitation for Egyptian dental clinics. Reply numbered list '
              'only, Arabic: 1. [company: post] - [format] - [adaptation].\n' + '\n'.join(lines))
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
    print('companies ok: %d/%d' % (ok, len(data)))
    for c in data:
        print('-', c['company'], len(c.get('posts', [])), 'posts', c.get('error', ''))
    if dry:
        return
    digest = 'مرصد لينكدإن للمنافسين\n\n' + analyze(data)
    print('sent:', send(digest))


if __name__ == '__main__':
    main()
