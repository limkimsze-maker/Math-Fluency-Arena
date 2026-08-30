from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'Created by Lim Kim Sze' in s:
    raise SystemExit('Credit already present')

css = '.siteCredit{width:100%;text-align:center;padding:12px 8px 18px;font-size:13px;font-weight:800;color:#66758d}\n'
if '</style>' not in s:
    raise SystemExit('style marker not found')
s = s.replace('</style>', css + '</style>', 1)

footer = '<footer class="siteCredit">Created by Lim Kim Sze</footer>\n'
if '<script>' not in s:
    raise SystemExit('script marker not found')
s = s.replace('<script>', footer + '<script>', 1)

p.write_text(s, encoding='utf-8')
