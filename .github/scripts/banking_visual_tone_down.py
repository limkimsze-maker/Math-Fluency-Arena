from pathlib import Path
import re

path=Path('index.html')
s=path.read_text(encoding='utf-8')

pattern=r'/\* BANKING_VISUAL_FIX_V3 — corrected visible pulse \+ animated success burst \*/.*?(?=\.wall\{)'
replacement='''/* BANKING_VISUAL_V4 — gentle, clear banking cue without harsh brightness */
.base.bankReady{border:5px solid #fff;outline:3px solid rgba(255,216,74,.9);outline-offset:1px;animation:bankPulseGentle .65s ease-in-out infinite alternate;box-shadow:0 0 0 3px rgba(255,216,74,.28),0 0 12px 5px rgba(255,216,74,.28);filter:brightness(1.02)}
.base.bankReady::after{content:"🏦 BANK HERE";position:absolute;top:50%;writing-mode:horizontal-tb;white-space:nowrap;transform:translateY(-50%);background:#fff7c7;color:#172033;border:2px solid #172033;border-radius:10px;padding:4px 7px;font-size:14px;font-weight:900;box-shadow:0 2px 0 rgba(23,32,51,.18)}
.base.blue.bankReady::after{left:calc(100% + 8px)}.base.red.bankReady::after{right:calc(100% + 8px)}
@keyframes bankPulseGentle{from{box-shadow:0 0 0 2px rgba(255,216,74,.22),0 0 8px 3px rgba(255,216,74,.22);filter:brightness(1)}to{box-shadow:0 0 0 6px rgba(255,216,74,.38),0 0 18px 7px rgba(255,216,74,.38);filter:brightness(1.08)}}
.base.bankBurst{z-index:9;border:5px solid #fff;outline:4px solid rgba(255,216,74,.92);outline-offset:2px;animation:bankBurstGentle .55s ease-out 1;box-shadow:0 0 0 8px rgba(255,216,74,.42),0 0 28px 12px rgba(255,216,74,.48);filter:brightness(1.12)}
.base.bankBurst::after{content:"✅ BANKED!";position:absolute;top:50%;writing-mode:horizontal-tb;white-space:nowrap;transform:translateY(-50%);background:#fff;color:#172033;border:3px solid #172033;border-radius:10px;padding:5px 8px;font-size:14px;font-weight:900;box-shadow:0 2px 8px rgba(23,32,51,.18)}
.base.blue.bankBurst::after{left:calc(100% + 8px)}.base.red.bankBurst::after{right:calc(100% + 8px)}
@keyframes bankBurstGentle{0%{box-shadow:0 0 0 2px rgba(255,216,74,.25),0 0 8px 3px rgba(255,216,74,.3);filter:brightness(1.03)}45%{box-shadow:0 0 0 10px rgba(255,216,74,.48),0 0 32px 14px rgba(255,216,74,.52);filter:brightness(1.14)}100%{box-shadow:0 0 0 4px rgba(255,216,74,.16),0 0 12px 5px rgba(255,216,74,.18);filter:brightness(1.02)}}
@media(prefers-reduced-motion:reduce){.base.bankReady{animation:none!important;box-shadow:0 0 0 4px rgba(255,216,74,.3),0 0 12px 5px rgba(255,216,74,.28)}.base.bankBurst{animation:none!important;box-shadow:0 0 0 7px rgba(255,216,74,.36),0 0 22px 9px rgba(255,216,74,.4)}}
'''

s2,n=re.subn(pattern,replacement,s,flags=re.S)
if n!=1:
    raise SystemExit(f'Expected one V3 banking CSS block, found {n}')
s2=s2.replace('bankBase.classList.remove("bankBurst"),1100','bankBase.classList.remove("bankBurst"),650')
if s2==s:
    raise SystemExit('No changes made')
path.write_text(s2,encoding='utf-8')
print('Installed BANKING_VISUAL_V4')
