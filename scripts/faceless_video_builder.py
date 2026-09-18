"""Faceless video builder: scenes JSON -> 1 AI image per scene (free providers)
+ Arabic voiceover (edge-tts, free) + Ken Burns motion + burned captions ->
vertical MP4. All free, no keys required (pollinations + edge-tts).

Usage:
  faceless_video_builder.py --demo                 # 5-scene system sales demo
  faceless_video_builder.py --scenes scenes.json   # custom [{image, voice}]
  faceless_video_builder.py --demo --no-voice      # silent preview (faster)
Output: output/faceless_<ts>.mp4 (+ .srt sidecar)

Image providers: pollinations (default, free/keyless). Nano Banana/Gemini
needs a BILLING-enabled key (free API tier = limit 0 for image models, per
Google staff) -> provider 'gemini' activates only if GEMINI_API_KEY exists.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(BASE, 'venv', 'bin')
FFMPEG = subprocess.run(
    [os.path.join(VENV, 'python'), '-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],
    capture_output=True, text=True).stdout.strip()
EDGE = os.path.join(VENV, 'edge-tts')
FONT = '/usr/share/fonts/truetype/noto/NotoKufiArabic-Regular.ttf'
W, H, FPS = 720, 1280, 30

DEMO_SCENES = [
    {'image': 'dental clinic phone ringing at empty reception desk, Cairo, cinematic, vertical',
     'voice': 'تليفون العيادة بيرن ومحدش بيرد. كل مكالمة ضايعة مريض راح للمنافس.'},
    {'image': 'angry dentist calculator money loss empty dental chair, dramatic light, vertical',
     'voice': 'في سوق فيه ستين الف دكتور اسنان، الكرسي الفاضي بياكل مكسبك كل يوم.'},
    {'image': 'smartphone whatsapp chat booking dental appointment automatically, glowing, vertical',
     'voice': 'نظامنا بيرد واتساب فورا، يحجز ويذكر ويرقم الدور. وانت نايم.'},
    {'image': 'happy egyptian dentist modern clinic patients smiling, bright, vertical',
     'voice': 'عيادات زي عيادتك زودت حجوزاتها من اول شهر. بدون سكرتيرة زيادة.'},
    {'image': 'phone whatsapp message demo button press, call to action style, vertical',
     'voice': 'ابعت كلمة ديمو على واتساب وشوف النظام شغال على عيادتك بنفسك.'},
]


def getenv(name, default=''):
    for line in open(os.path.join(BASE, '.env'), encoding='utf-8'):
        if line.startswith(name + '='):
            return line.strip().split('=', 1)[1]
    return default


def gen_image_pollinations(prompt, out):
    url = ('https://image.pollinations.ai/prompt/%s?width=720&height=1280&nologo=true&model=flux'
           % urllib.parse.quote(prompt[:400]))
    req = urllib.request.Request(url, headers={'User-Agent': 'clinic-builder/1.0'})
    data = urllib.request.urlopen(req, timeout=180).read()
    assert data[:4] != b'<htm' and len(data) > 10000, 'pollinations failed'
    open(out, 'wb').write(data)


def gen_image_gemini(prompt, out):
    key = getenv('GEMINI_API_KEY')
    if not key:
        raise RuntimeError('gemini provider needs billing-enabled GEMINI_API_KEY in .env')
    body = json.dumps({'contents': [{'parts': [{'text': prompt[:1000]}]}]}).encode()
    req = urllib.request.Request(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=' + key,
        data=body, headers={'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=180))
    for part in r['candidates'][0]['content']['parts']:
        if 'inlineData' in part:
            import base64
            open(out, 'wb').write(base64.b64decode(part['inlineData']['data']))
            return
    raise RuntimeError('gemini returned no image (quota? billing?)')


def gen_voice(text, mp3, srt, voice='ar-EG-SalmaNeural'):
    subprocess.run([EDGE, '--voice', voice, '--text', text,
                    '--write-media', mp3, '--write-subtitles', srt],
                   check=True, timeout=120)


def duration_of(path):
    r = subprocess.run([FFMPEG, '-i', path], capture_output=True, text=True)
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr)
    h, mnt, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return max(1.0, h * 3600 + mnt * 60 + s)


def scene_clip(img, mp3, srt, out, idx):
    dur = duration_of(mp3) + 0.4
    frames = int(dur * FPS)
    vf = ('crop=iw:ih-120:0:0,scale=1440:2560,zoompan=z=\'min(zoom+0.0015,1.3)\':d=%d:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=720x1280:fps=%d,'
          'subtitles=%s:fontsdir=/usr/share/fonts:force_style=\'FontName="Noto Kufi Arabic",FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,BorderStyle=1,MarginV=120\'' % (frames, FPS, srt.replace(':', '\\:').replace("'", '')))
    subprocess.run([FFMPEG, '-y', '-loop', '1', '-i', img, '-i', mp3,
                    '-vf', vf, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-shortest', out],
                   check=True, timeout=300, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--demo', action='store_true')
    ap.add_argument('--scenes', default='')
    ap.add_argument('--provider', default='pollinations', choices=['pollinations', 'gemini'])
    ap.add_argument('--no-voice', action='store_true')
    ap.add_argument('--outdir', default=os.path.join(BASE, 'output'))
    a = ap.parse_args()
    scenes = list(DEMO_SCENES) if (a.demo or not a.scenes) else json.load(open(a.scenes, encoding='utf-8'))
    ts = time.strftime('%Y%m%d-%H%M%S')
    work = os.path.join('/tmp', 'fv_' + ts)
    os.makedirs(work, exist_ok=True)
    os.makedirs(a.outdir, exist_ok=True)
    gen_img = gen_image_gemini if a.provider == 'gemini' else gen_image_pollinations
    clips = []
    for i, sc in enumerate(scenes):
        img = os.path.join(work, 's%d.jpg' % i)
        mp3 = os.path.join(work, 's%d.mp3' % i)
        srt = os.path.join(work, 's%d.srt' % i)
        print('scene %d/%d img...' % (i + 1, len(scenes)), flush=True)
        gen_img(sc['image'], img)
        if not a.no_voice:
            print('scene %d/%d voice...' % (i + 1, len(scenes)), flush=True)
            gen_voice(sc['voice'], mp3, srt)
        else:
            subprocess.run([FFMPEG, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                            '-t', '3', mp3], check=True, capture_output=True)
            open(srt, 'w').write('1\n00:00:00,000 --> 00:00:03,000\n%s\n' % sc['voice'])
        clip = os.path.join(work, 'c%d.mp4' % i)
        print('scene %d/%d render...' % (i + 1, len(scenes)), flush=True)
        scene_clip(img, mp3, srt, clip, i)
        clips.append(clip)
    lst = os.path.join(work, 'list.txt')
    open(lst, 'w').write(''.join("file '%s'\n" % c for c in clips))
    final = os.path.join(a.outdir, 'faceless_%s.mp4' % ts)
    subprocess.run([FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-c', 'copy', final], check=True, timeout=120, capture_output=True)
    print('DONE:', final, os.path.getsize(final), 'bytes')


if __name__ == '__main__':
    main()
