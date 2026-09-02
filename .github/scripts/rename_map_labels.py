from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

replacements = {
    'Sakura Arena': 'Sakura Garden',
    'Singapore City Garden': 'Singapore Garden City',
    'China Garden City': 'Chinese Lantern Garden',
}

for old, new in replacements.items():
    count = s.count(old)
    if count == 0:
        raise SystemExit(f'Expected label not found: {old}')
    s = s.replace(old, new)
    print(f'Renamed {old!r} -> {new!r} ({count} occurrence(s))')

path.write_text(s, encoding='utf-8')
print('Map labels renamed successfully.')
