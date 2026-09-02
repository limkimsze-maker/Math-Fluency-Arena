from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'BANKING_VISUAL_FIX_V3' in s:
    raise SystemExit('BANKING_VISUAL_FIX_V3 already installed')

start = s.find('/* BANKING_VISUAL_FIX_V2')
if start < 0:
    raise SystemExit('BANKING_VISUAL_FIX_V2 block not found')
end = s.find('.wall{', start)
if end < 0:
    raise SystemExit('Could not find end of banking CSS block')

new = '''/* BANKING_VISUAL_FIX_V3 — corrected visible pulse + animated success burst */
.base.bankReady{border:6px solid #fff;outline:5px solid #ffd84a;outline-offset:2px;background:rgba(255,216,74,.58);animation:bankPulseStrong .42s ease-in-out infinite alternate;box-shadow:0 0 0 7px rgba(255,216,74,.7),0 0 30px 12px rgba(255,216,74,.9);filter:brightness(1.08)}
.base.bankReady::after{content:"🏦 BANK HERE";position:absolute;top:50%;writing-mode:horizontal-tb;white-space:nowrap;transform:translateY(-50%);background:#fff36d;color:#172033;border:4px solid #172033;border-radius:11px;padding:6px 9px;font-size:15px;font-weight:900;box-shadow:0 4px 0 rgba(23,32,51,.24),0 0 14px rgba(255,255,255,.9)}
.base.blue.bankReady::after{left:calc(100% + 10px)}.base.red.bankReady::after{right:calc(100% + 10px)}
@keyframes bankPulseStrong{from{background:rgba(255,216,74,.42);box-shadow:0 0 0 4px rgba(255,216,74,.45),0 0 16px 6px rgba(255,216,74,.55);filter:brightness(1)}to{background:rgba(255,244,120,.98);box-shadow:0 0 0 16px rgba(255,216,74,.88),0 0 52px 26px rgba(255,216,74,1);filter:brightness(1.55)}}
.base.bankBurst{z-index:9;border:7px solid #fff;outline:8px solid #ffd84a;outline-offset:3px;background:#fff36d;animation:bankBurstStrong 1.05s ease-out 1;box-shadow:0 0 0 20px rgba(255,255,255,.92),0 0 70px 38px rgba(255,216,74,1);filter:brightness(1.7)}
.base.bankBurst::after{content:"✅ BANKED!";position:absolute;top:50%;writing-mode:horizontal-tb;white-space:nowrap;transform:translateY(-50%) scale(1.05);background:#fff;color:#172033;border:4px solid #172033;border-radius:12px;padding:7px 10px;font-size:17px;font-weight:900;box-shadow:0 0 22px 8px rgba(255,216,74,.95)}
.base.blue.bankBurst::after{left:calc(100% + 10px)}.base.red.bankBurst::after{right:calc(100% + 10px)}
@keyframes bankBurstStrong{0%{background:#fff;filter:brightness(2);box-shadow:0 0 0 3px rgba(255,255,255,1),0 0 18px 8px rgba(255,216,74,1)}35%{background:#fff36d;filter:brightness(1.8);box-shadow:0 0 0 28px rgba(255,255,255,.94),0 0 92px 52px rgba(255,216,74,1)}100%{background:#fff7b2;filter:brightness(1.15);box-shadow:0 0 0 8px rgba(255,255,255,.2),0 0 30px 12px rgba(255,216,74,.28)}}
@media(prefers-reduced-motion:reduce){.base.bankReady{animation:none!important;background:rgba(255,244,120,.98);box-shadow:0 0 0 14px rgba(255,216,74,.86),0 0 44px 20px rgba(255,216,74,.95)}.base.bankBurst{animation:none!important;background:#fff36d;box-shadow:0 0 0 24px rgba(255,255,255,.94),0 0 86px 46px rgba(255,216,74,1)}}
'''

s = s[:start] + new + s[end:]
p.write_text(s, encoding='utf-8')
print('Installed BANKING_VISUAL_FIX_V3')
