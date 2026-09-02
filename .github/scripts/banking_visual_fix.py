from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'BANKING_VISUAL_FIX_V2' in s:
    raise SystemExit('BANKING_VISUAL_FIX_V2 already installed')

old = '''/* BANKING_CLARITY_V1 — lightweight visual guidance for banking */
.base.bankReady{border-style:solid;animation:bankPulse .58s ease-in-out infinite alternate;box-shadow:0 0 0 5px rgba(255,216,74,.55),0 0 20px rgba(255,216,74,.8)}
.base.bankReady::after{content:"🏦 BANK HERE";position:absolute;top:50%;writing-mode:horizontal-tb;white-space:nowrap;transform:translateY(-50%);background:#fff7b2;color:#172033;border:3px solid #172033;border-radius:10px;padding:5px 8px;font-size:14px;font-weight:900;box-shadow:0 3px 0 rgba(23,32,51,.18)}
.base.blue.bankReady::after{left:calc(100% + 8px)}.base.red.bankReady::after{right:calc(100% + 8px)}
.base.bankBurst{box-shadow:0 0 0 10px rgba(255,255,255,.9),0 0 32px 18px rgba(255,216,74,.95);filter:brightness(1.35)}
@keyframes bankPulse{to{box-shadow:0 0 0 9px rgba(255,216,74,.72),0 0 32px 10px rgba(255,216,74,.95);filter:brightness(1.2)}}
@media(prefers-reduced-motion:reduce){.base.bankReady{animation:none!important}}'''

new = '''/* BANKING_VISUAL_FIX_V2 — unmistakable lightweight banking pulse + success burst */
.base.bankReady{border:6px solid #fff!important;outline:5px solid #ffd84a;outline-offset:2px;background:rgba(255,216,74,.58)!important;animation:bankPulseStrong .42s ease-in-out infinite alternate;box-shadow:0 0 0 7px rgba(255,216,74,.7),0 0 30px 12px rgba(255,216,74,.9);filter:brightness(1.08)}
.base.bankReady::after{content:"🏦 BANK HERE";position:absolute;top:50%;writing-mode:horizontal-tb;white-space:nowrap;transform:translateY(-50%);background:#fff36d;color:#172033;border:4px solid #172033;border-radius:11px;padding:6px 9px;font-size:15px;font-weight:900;box-shadow:0 4px 0 rgba(23,32,51,.24),0 0 14px rgba(255,255,255,.9)}
.base.blue.bankReady::after{left:calc(100% + 10px)}.base.red.bankReady::after{right:calc(100% + 10px)}
@keyframes bankPulseStrong{from{background:rgba(255,216,74,.46)!important;box-shadow:0 0 0 5px rgba(255,216,74,.52),0 0 18px 7px rgba(255,216,74,.65);filter:brightness(1.02)}to{background:rgba(255,244,120,.95)!important;box-shadow:0 0 0 15px rgba(255,216,74,.82),0 0 48px 24px rgba(255,216,74,.98);filter:brightness(1.5)}}
.base.bankBurst{z-index:9!important;border:7px solid #fff!important;outline:8px solid #ffd84a;outline-offset:3px;background:#fff36d!important;animation:bankBurstStrong 1.05s ease-out 1!important;box-shadow:0 0 0 20px rgba(255,255,255,.92),0 0 70px 38px rgba(255,216,74,1)!important;filter:brightness(1.7)!important}
.base.bankBurst::after{content:"✅ BANKED!";position:absolute;top:50%;writing-mode:horizontal-tb;white-space:nowrap;transform:translateY(-50%) scale(1.05);background:#fff;color:#172033;border:4px solid #172033;border-radius:12px;padding:7px 10px;font-size:17px;font-weight:900;box-shadow:0 0 22px 8px rgba(255,216,74,.95)}
.base.blue.bankBurst::after{left:calc(100% + 10px)}.base.red.bankBurst::after{right:calc(100% + 10px)}
@keyframes bankBurstStrong{0%{filter:brightness(2)!important;box-shadow:0 0 0 3px rgba(255,255,255,1),0 0 18px 8px rgba(255,216,74,1)!important}35%{filter:brightness(1.8)!important;box-shadow:0 0 0 25px rgba(255,255,255,.92),0 0 85px 48px rgba(255,216,74,1)!important}100%{filter:brightness(1.2)!important;box-shadow:0 0 0 8px rgba(255,255,255,.25),0 0 28px 12px rgba(255,216,74,.35)!important}}
@media(prefers-reduced-motion:reduce){.base.bankReady{animation:none!important;background:rgba(255,244,120,.95)!important;box-shadow:0 0 0 12px rgba(255,216,74,.82),0 0 40px 18px rgba(255,216,74,.9)!important}.base.bankBurst{animation:none!important}}'''

if old not in s:
    raise SystemExit('Expected banking CSS block not found')
s = s.replace(old, new, 1)

old_timeout = 'setTimeout(()=>bankBase.classList.remove("bankBurst"),700)'
new_timeout = 'setTimeout(()=>bankBase.classList.remove("bankBurst"),1100)'
if old_timeout not in s:
    raise SystemExit('Bank burst timeout anchor not found')
s = s.replace(old_timeout, new_timeout, 1)

p.write_text(s, encoding='utf-8')
print('Installed BANKING_VISUAL_FIX_V2')
