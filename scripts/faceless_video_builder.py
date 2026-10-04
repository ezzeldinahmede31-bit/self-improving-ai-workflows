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
SEED = 11

DEMO_SCENES = [
    {'image': 'ultra photorealistic close-up of vintage telephone ringing on empty elegant dental reception desk, shallow depth of field, warm evening light Cairo clinic, 9:16 vertical composition, professional photography, sharp focus, no people, no text, no watermark',
     'voice': 'بص... تليفون العيادة بيرن، ومحدش بيرد. عارف ده معناه ايه؟ كل مكالمة بتضيع... عيان بيروح يحجز عند الدكتور اللي جنبك.'},
    {'image': 'ultra photorealistic empty luxury dental chair in dark modern Cairo clinic at night, single spotlight from above, dramatic shadows, cinematic mood, 9:16 vertical composition, professional photography, no people, no text, no watermark',
     'voice': 'عارف في كام دكتور سنان في مصر؟ ستين الف. متخيل؟ والكرسي الفاضي بتاعك... بياكل فلوسك كل يوم، وانت بتتفرج.'},
    {'image': 'ultra photorealistic POV over shoulder, hand holding smartphone showing green chat bubbles booking a dental appointment, bright modern clinic blurred background, daylight, 9:16 vertical composition, sharp focus on phone, no readable text, no watermark',
     'voice': 'طب والحل؟ بص بقى... النظام بتاعنا بيرد على الواتساب في ثانية واحدة. يحجز، ويأكد، ويبعت التذكير. وانت نايم بالليل ومرتاح.'},
    {'image': 'ultra photorealistic happy Egyptian family leaving bright modern dental clinic, mother and child smiling at reception, morning sunlight, 9:16 vertical composition, professional lifestyle photography, no text, no watermark',
     'voice': 'وعلى فكرة... عيادات شبه عيادتك بالظبط، زودت الحجوزات من اول شهر. من غير ما تشغل سكرتيرة زيادة، ومن غير وجع دماغ.'},
    {'image': 'ultra photorealistic smartphone on marble counter showing chat app with big green button, dental clinic blurred background, bright inviting light, 9:16 vertical composition, product photography style, no readable text, no watermark',
     'voice': 'مستني ايه؟ ابعت كلمة ديمو على الواتساب دلوقتي... وشوف بعنيك النظام وهو شغال على عيادتك. يلا!'},
]


def getenv(name, default=''):
    for line in open(os.path.join(BASE, '.env'), encoding='utf-8'):
        if line.startswith(name + '='):
            return line.strip().split('=', 1)[1]
    return default


def gen_image_pollinations(prompt, out):
    # Oct 2026: pollinations free tier = width<=512, height<=768 (bigger -> 402).
    # Generate 512x768 free, ffmpeg upscales/crops to 720x1280 downstream.
    for model in ('turbo', 'flux'):
        url = ('https://image.pollinations.ai/prompt/%s?width=512&height=768&nologo=true&model=%s&seed=%d'
               % (urllib.parse.quote(prompt[:400]), model, SEED))
        req = urllib.request.Request(url, headers={'User-Agent': 'clinic-builder/1.0'})
        try:
            data = urllib.request.urlopen(req, timeout=180).read()
        except Exception:
            continue  # paid-gate (402) or transient -> try next model
        if data[:4] == b'<htm' or len(data) <= 10000:
            continue
        open(out, 'wb').write(data)
        return
    raise RuntimeError('pollinations turbo+flux both failed (free tier may be down)')


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



# Emotion direction per scene position: subtle, never exaggerated (user rule:
# real feelings, no overacting). Tags follow ElevenLabs v3 audio-tag style.
EMOTION_ARC = ['[softly, with genuine concern, like a friend warning you about losing money]',
               '[seriously, with urgency, speaking fast and direct]',
               '[warmly, with relief, like good news after worry]',
               '[confidently, like proof that cannot be argued with]',
               '[warmly, inviting, like a personal invitation]']


def elevenlabs_voice(text, mp3, voice_id, api_key, emotion=''):
    import urllib.request
    spoken = (emotion + ' ' + text).strip() if emotion else text
    body = json.dumps({'text': spoken, 'model_id': 'eleven_v3',
                       'voice_settings': {'stability': 0.55, 'similarity_boost': 0.75}}).encode()
    req = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128' % voice_id,
        data=body, headers={'xi-api-key': api_key, 'Content-Type': 'application/json',
                            'Accept': 'audio/mpeg'})
    audio = urllib.request.urlopen(req, timeout=180).read()
    assert len(audio) > 5000, 'elevenlabs returned too little audio'
    open(mp3, 'wb').write(audio)


def scene_srt_from_text(text, dur, srt):
    # Full-scene captions (no word timings from ElevenLabs): split in halves.
    words = text.split()
    mid = max(1, len(words) // 2)
    parts = [' '.join(words[:mid]), ' '.join(words[mid:])]
    def ts(s):
        h, m, sec = int(s // 3600), int((s % 3600) // 60), s % 60
        return '%02d:%02d:%06.3f' % (h, m, sec)
    with open(srt, 'w', encoding='utf-8') as f:
        for i, part in enumerate(parts):
            a, b = dur * i / 2, dur * (i + 1) / 2
            f.write('%d\n%s --> %s\n%s\n\n' % (i + 1, ts(a).replace('.', ','), ts(b).replace('.', ','), part))



GEMINI_VOICE = 'Kore'
GEMINI_DIRECTION = ('اتكلم باللهجة المصرية العامية، بصوت دكتور خبير واثق من كل كلمة بيقولها، '
                    'وفي صوته بهجة خفيفة وابتسامة صغيرة زي حد مبسوط بشغله ومتفائل، '
                    'هادي ومتمكن زي اللي جرب الحاجة دي مية مرة قبل كده، '
                    'بيحكي لصاحبه كلام طبيعي فيه وقفات وتنفس وأسئلة بلاغية، '
                    'بدون أي مبالغة خالص: ')


def gemini_voice(text, mp3, voice=None, direction=None):
    import base64
    key = getenv('GEMINI_API_KEY')
    if not key:
        raise RuntimeError('gemini engine needs GEMINI_API_KEY in .env')
    spoken = (direction or GEMINI_DIRECTION) + text
    body = json.dumps({'contents': [{'parts': [{'text': spoken}]}],
                       'generationConfig': {'responseModalities': ['AUDIO'],
                                             'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice or GEMINI_VOICE}}}}}).encode()
    req = urllib.request.Request(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=' + key,
        data=body, headers={'Content-Type': 'application/json'})
    b64 = json.load(urllib.request.urlopen(req, timeout=180))['candidates'][0]['content']['parts'][0]['inlineData']['data']
    pcm = os.path.join(os.path.dirname(mp3), 'g.pcm')
    open(pcm, 'wb').write(base64.b64decode(b64))
    subprocess.run([FFMPEG, '-y', '-v', 'error', '-f', 's16le', '-ar', '24000', '-ac', '1',
                    '-i', pcm, '-c:a', 'libmp3lame', '-b:a', '64k', mp3],
                   check=True, timeout=120, capture_output=True)


def gen_voice(text, mp3, srt, voice='ar-EG-SalmaNeural'):
    subprocess.run([EDGE, '--voice', voice, '--text', text,
                    '--write-media', mp3, '--write-subtitles', srt],
                   check=True, timeout=120)


def duration_of(path):
    r = subprocess.run([FFMPEG, '-i', path], capture_output=True, text=True)
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr)
    h, mnt, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return max(1.0, h * 3600 + mnt * 60 + s)



def kinetic_title_card(text, out, fontsize=64):
    """Big multi-line Arabic title PNG (transparent) for kinetic overlay."""
    import arabic_reshaper
    from bidi.algorithm import get_display
    from PIL import Image, ImageDraw, ImageFont
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        if len(cur) + len(w_) + 1 <= 16:
            cur = (cur + ' ' + w_).strip()
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    lines = lines[:4]
    f = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoKufiArabic-Regular.ttf', fontsize)
    img = Image.new('RGBA', (W, 500), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = 20
    for ln in lines:
        t = get_display(arabic_reshaper.reshape(ln))
        d.text((W // 2, y), t, font=f, fill=(255, 255, 255, 255),
               anchor='ma', stroke_width=2, stroke_fill=(0, 0, 0, 220))
        y += fontsize + 18
    img.save(out)


def kinetic_bg(out, seed_color=(18, 22, 38)):
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (W, H), seed_color)
    d = ImageDraw.Draw(img)
    for i in range(0, H, 4):
        shade = max(0, 26 - i // 90)
        d.line([(0, i), (W, i)], fill=(seed_color[0] + shade, seed_color[1] + shade, seed_color[2] + shade + 6))
    img.save(out)


def scene_clip_kinetic(bg, title_png, mp3, srt, out):
    dur = duration_of(mp3) + 0.4
    frames = int(dur * FPS)
    fc = ("crop=iw:ih-120:0:0,scale=1440:2560,zoompan=z='min(zoom+0.0008,1.15)':d=%d:"
          "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=%d" % (frames, FPS))
    vf = ('%s,subtitles=%s:fontsdir=/usr/share/fonts:force_style=\'FontName="Noto Kufi Arabic",'
          'FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,BorderStyle=1,MarginV=120\'' % (fc, srt.replace(':', '\\:').replace("'", '')))
    # title overlay (static) + progress bar
    vf += (",movie=%s,format=rgba[o];[v][o]overlay=(W-w)/2:300,"
           "drawbox=x=60:y=1190:w='(720-120)*t/%s':h=8:c=yellow:t=fill" % (title_png, dur))
    subprocess.run([FFMPEG, '-y', '-loop', '1', '-i', bg, '-i', mp3,
                    '-filter_complex', vf.replace('[v]', '[0:v]'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-shortest', out],
                   check=True, timeout=300, capture_output=True)


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
    ap.add_argument('--engine', default='edge', choices=['edge', 'elevenlabs', 'gemini'])
    ap.add_argument('--style', default='cinema', choices=['cinema', 'kinetic'])
    ap.add_argument('--eleven-voice', default='JBFqnCBsd6RMkjVDRZzb')
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
        scene_kind = sc.get('kind', a.style)
        if scene_kind == 'kinetic':
            print('scene %d/%d kinetic...' % (i + 1, len(scenes)), flush=True)
            kinetic_bg(img)
            kinetic_title_card(sc.get('title') or sc['voice'][:60],
                               os.path.join(work, 't%d.png' % i))
        elif sc.get('image_file'):
            print('scene %d/%d real footage...' % (i + 1, len(scenes)), flush=True)
            import shutil as _sh
            _sh.copy(sc['image_file'], img)
        else:
            print('scene %d/%d img...' % (i + 1, len(scenes)), flush=True)
            gen_img(sc['image'], img)
        if not a.no_voice:
            print('scene %d/%d voice...' % (i + 1, len(scenes)), flush=True)
            if a.engine == 'gemini':
                print('scene %d/%d voice (gemini)...' % (i + 1, len(scenes)), flush=True)
                gemini_voice(sc['voice'], mp3)
                scene_srt_from_text(sc['voice'], duration_of(mp3), srt)
            elif a.engine == 'elevenlabs':
                emo = EMOTION_ARC[min(i, len(EMOTION_ARC) - 1)]
                elevenlabs_voice(sc['voice'], mp3, a.eleven_voice, getenv('ELEVENLABS_API_KEY'), emo)
                scene_srt_from_text(sc['voice'], duration_of(mp3), srt)
            else:
                gen_voice(sc['voice'], mp3, srt)
        else:
            subprocess.run([FFMPEG, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                            '-t', '3', mp3], check=True, capture_output=True)
            open(srt, 'w').write('1\n00:00:00,000 --> 00:00:03,000\n%s\n' % sc['voice'])
        clip = os.path.join(work, 'c%d.mp4' % i)
        print('scene %d/%d render...' % (i + 1, len(scenes)), flush=True)
        if scene_kind == 'kinetic':
            scene_clip_kinetic(img, os.path.join(work, 't%d.png' % i), mp3, srt, clip)
        else:
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
