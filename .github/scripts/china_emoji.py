from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_theme = '''  if(theme==="china")return '<div class="themeDecor faint" style="left:50%;top:14%">🏯</div><div class="themeDecor big" style="left:15%;top:22%">🎋</div><div class="themeDecor big" style="left:85%;top:78%">🎋</div><div class="themeDecor" style="left:50%;top:82%">🏮</div><div class="themeDecor" style="left:28%;top:18%">🪨</div><div class="themeDecor" style="left:72%;top:20%">🏮</div>';'''
new_theme = '''  // CHINA_CNY_EMOJI_V1 — lightweight browser-native decorations only
  if(theme==="china")return '<div class="themeDecor big" style="left:14%;top:18%">🧧</div><div class="themeDecor" style="left:31%;top:82%">🍊</div><div class="themeDecor big" style="left:49%;top:13%">🎆</div><div class="themeDecor" style="left:67%;top:82%">🏮</div><div class="themeDecor big" style="left:86%;top:22%">🐉</div><div class="themeDecor" style="left:18%;top:72%">🎋</div><div class="themeDecor" style="left:82%;top:68%">🎇</div><div class="themeDecor" style="left:38%;top:18%">🌸</div><div class="themeDecor" style="left:59%;top:76%">🪙</div><div class="themeDecor" style="left:74%;top:16%">✨</div>';'''

old_mini = 'if(theme==="china")return [[50,16,"🏯"],[18,23,"🎋"],[82,76,"🎋"],[50,82,"🏮"]]'
new_mini = 'if(theme==="china")return [[14,20,"🧧"],[32,78,"🍊"],[50,16,"🎆"],[68,78,"🏮"],[86,22,"🐉"]]'

if 'CHINA_CNY_EMOJI_V1' in s:
    raise SystemExit('China emoji patch already installed')
if old_theme not in s:
    raise SystemExit('China theme marker not found')
if old_mini not in s:
    raise SystemExit('China preview marker not found')

s = s.replace(old_theme, new_theme, 1)
s = s.replace(old_mini, new_mini, 1)
p.write_text(s, encoding='utf-8')
print('Installed lightweight China CNY emoji decorations')
