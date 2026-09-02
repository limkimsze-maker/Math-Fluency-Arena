from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = '''/* BANK_NINJA_GLOW_V1 — brief team-colour glow when a ninja banks */
.player.bankGlow.blue .ninja{animation:bankBlueGlow .72s ease-out 1}
.player.bankGlow.red .ninja{animation:bankRedGlow .72s ease-out 1}
@keyframes bankBlueGlow{0%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 5px #2f7df6)}38%{filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 15px #45c8ff) drop-shadow(0 0 24px #2f7df6)}100%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 3px #2f7df6)}}
@keyframes bankRedGlow{0%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 5px #ff5b63)}38%{filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 15px #ff7680) drop-shadow(0 0 24px #ff3344)}100%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 3px #ff5b63)}}'''
new = '''/* BANK_NINJA_GLOW_V2 — brief golden glow when any ninja banks */
.player.bankGlow .ninja{animation:bankGoldGlow .72s ease-out 1}
@keyframes bankGoldGlow{0%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 5px #ffd84a)}38%{filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 15px #ffd84a) drop-shadow(0 0 24px #ffb300)}100%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 3px #ffd84a)}}'''
if old not in s:
    raise SystemExit('Expected team-colour bank glow block not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
