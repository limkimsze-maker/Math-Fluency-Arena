from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

MARKER = 'SINGAPORE_EMOJI_V1'
if MARKER in s:
    raise SystemExit('Singapore emoji decorations are already installed')

old = '''  if(theme==="singapore")return '<div class="themeDecor faint" style="left:50%;top:14%">🏙️</div><div class="themeDecor big" style="left:16%;top:20%">🌴</div><div class="themeDecor" style="left:84%;top:24%">🌴</div><div class="themeDecor big" style="left:50%;top:84%">🌉</div><div class="themeDecor" style="left:28%;top:84%">🌺</div><div class="themeDecor" style="left:72%;top:78%">🌺</div>';'''
new = '''  // SINGAPORE_EMOJI_V1 — lightweight browser-native decorations only
  if(theme==="singapore")return '<div class="themeDecor big" style="left:13%;top:18%">🏙️</div><div class="themeDecor" style="left:28%;top:80%">🌴</div><div class="themeDecor" style="left:41%;top:16%">🌺</div><div class="themeDecor big" style="left:52%;top:82%">🌉</div><div class="themeDecor" style="left:66%;top:16%">🌊</div><div class="themeDecor" style="left:82%;top:74%">⛵</div><div class="themeDecor" style="left:18%;top:66%">🚌</div><div class="themeDecor" style="left:72%;top:78%">🍜</div><div class="themeDecor big" style="left:86%;top:22%">🦀</div>';'''
if s.count(old) != 1:
    raise SystemExit(f'Singapore decoration marker count: {s.count(old)}')
s = s.replace(old, new, 1)

old_mini = 'function miniDecor(theme){if(theme==="singapore")return [[50,16,"🏙️"],[18,22,"🌴"],[82,75,"🌴"],[50,82,"🌉"]];'
new_mini = 'function miniDecor(theme){if(theme==="singapore")return [[13,20,"🏙️"],[29,78,"🌴"],[42,18,"🌺"],[54,80,"🌉"],[68,18,"🌊"],[84,72,"⛵"],[18,65,"🚌"],[73,76,"🍜"],[87,22,"🦀"]];'
if s.count(old_mini) != 1:
    raise SystemExit(f'Singapore mini preview marker count: {s.count(old_mini)}')
s = s.replace(old_mini, new_mini, 1)

p.write_text(s, encoding='utf-8')
print('Updated Singapore maps with lightweight emoji decorations.')
