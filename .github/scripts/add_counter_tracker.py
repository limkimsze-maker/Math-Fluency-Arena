from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

tracker = '<script src="https://cdn.counter.dev/script.js" data-id="825e93b6-ce99-40ef-8bcc-125f13297433" data-utcoffset="8"></script>'

if tracker in s:
    raise SystemExit('Counter.dev tracker already present')

anchor = '<title>Math Star Chase and Bank</title>'
if anchor not in s:
    raise SystemExit('Could not find title anchor')

s = s.replace(anchor, anchor + '\n' + tracker, 1)

if s.count(tracker) != 1:
    raise SystemExit('Tracker insertion count is not exactly 1')

p.write_text(s, encoding='utf-8')
print('Added Counter.dev tracker once in <head>.')
