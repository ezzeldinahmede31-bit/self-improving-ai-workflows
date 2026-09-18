"""Social lane of competitor watch: YouTube channels via yt-dlp (no API key),
rank by views, Nemotron picks imitable formats, Telegram digest.

Usage:
  comp_social_watch.py --dry-run   # print only, no send, no LLM call bill
  comp_social_watch.py              # full run + Telegram send
Secrets from .env (never hardcoded): NVIDIA_API_KEY, TREND_RADAR_BOT_TOKEN, CHAT_ID_TREND_RADAR
"""
import json
import os
import re
import subprocess
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)


def getenv(name):
    for line in open(os.path.join(BASE, '.env'), encoding='utf-8'):
        if line.startswith(name + '='):
            return line.strip().split('=', 1)[1]
    raise RuntimeError('missing env ' + name)


CHANNELS = [
    ('Solutionreach', 'UCpbkjOhLcXaZ8kiG_kICFPQ'),
    ('Adit', 'UCht4NnnAAZXk6Y6CbpHmOJg'),
    ('Practice by Numbers', 'UCHbRmlpsaO3jAlVT1Khh4RA'),
    ('NexHealth', 'UCdrFnASkMQLNcOEE5S1iYvg'),
    ('Gumloop', 'UCQJ5GMM0afVO2AQ_AguMF0w'),
    ('Lindy', 'UCFJ2Y3dktNSTFZ1kiMeTNKA'),
]
# NOTE: @Zapier/@Make handles resolve flakily via yt-dlp (0 videos on retry);
# their blogs stay on the monthly manual list. TikTok/LinkedIn need an Apify
# token (free tier) — see skill; until then they are manual monthly.

CLEAN = re.compile(r'[_*\[\]()~`>#+=|{}.!-]')


def fetch_channel(name, ref, per=6):
    url = ref if ref.startswith('@') else 'https://www.youtube.com/channel/%s/videos' % ref
    cmd = [os.path.join(BASE, 'venv', 'bin', 'yt-dlp'), '--flat-playlist',
           '--print', '%(title)s\t%(view_count)s\t%(upload_date)s\t%(id)s',
           '--playlist-end', str(per), url]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=180).stdout
    except Exception as e:
        return {'channel': name, 'error': str(e)[:120], 'videos': []}
    videos = []
    for line in out.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) < 2 or not parts[0] or 'ERROR' in line:
            continue
        try:
            views = int(parts[1]) if parts[1] not in ('NA', 'None', '') else 0
        except ValueError:
            views = 0
        videos.append({'title': parts[0][:120], 'views': views,
                       'date': parts[2] if len(parts) > 2 else '',
                       'url': 'https://youtu.be/' + parts[3] if len(parts) > 3 and parts[3] else ''})
    videos.sort(key=lambda v: -v['views'])
    return {'channel': name, 'videos': videos[:4]}


def analyze(data):
    key = getenv('NVIDIA_API_KEY')
    lines = []
    for ch in data:
        for v in ch['videos'][:3]:
            lines.append('%s | %s (%d views)' % (ch['channel'], v['title'], v['views']))
    prompt = ('Competitor YouTube winners (title + views). Pick top 5 formats worth '
              'structure-level imitation for Egyptian dental clinics. Reply numbered list only, '
              'Arabic: 1. [المنافس: الفيديو (المشاهدات)] - [الفورمات] - [التقليد لعيادات مصر].\n'
              + '\n'.join(lines))
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
    r = json.load(urllib.request.urlopen(req, timeout=60))
    return r.get('ok', False)


def main():
    dry = '--dry-run' in sys.argv
    data = []
    for name, ref in CHANNELS:
        print('fetching', name, flush=True)
        data.append(fetch_channel(name, ref))
    ok = sum(1 for c in data if c['videos'])
    print('channels ok: %d/%d' % (ok, len(data)))
    if dry:
        print(json.dumps(data, ensure_ascii=False)[:1500])
        return
    content = analyze(data)
    digest = 'مرصد سوشيال المنافسين\n\n' + content
    print('sent:', send(digest))


if __name__ == '__main__':
    main()
