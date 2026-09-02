from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='BANK_NINJA_GLOW_V1'
if marker in s:
    raise SystemExit('Bank ninja glow already installed')

css_anchor='@keyframes immuneHalo{to{box-shadow:0 0 0 8px rgba(73,216,255,.72),0 0 28px 12px rgba(73,216,255,.72)}}'
css_add='''@keyframes immuneHalo{to{box-shadow:0 0 0 8px rgba(73,216,255,.72),0 0 28px 12px rgba(73,216,255,.72)}}
/* BANK_NINJA_GLOW_V1 — brief team-colour glow when a ninja banks */
.player.bankGlow.blue .ninja{animation:bankBlueGlow .72s ease-out 1}
.player.bankGlow.red .ninja{animation:bankRedGlow .72s ease-out 1}
@keyframes bankBlueGlow{0%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 5px #2f7df6)}38%{filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 15px #45c8ff) drop-shadow(0 0 24px #2f7df6)}100%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 3px #2f7df6)}}
@keyframes bankRedGlow{0%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 5px #ff5b63)}38%{filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 15px #ff7680) drop-shadow(0 0 24px #ff3344)}100%{filter:drop-shadow(0 0 2px #fff) drop-shadow(0 0 3px #ff5b63)}}'''
if css_anchor not in s:
    raise SystemExit('CSS anchor not found')
s=s.replace(css_anchor,css_add,1)

bank_anchor='function checkBank(){'
helper='''function bankNinjaGlow(id){const el=document.querySelector('[data-player="'+id+'"]');if(!el)return;el.classList.remove("bankGlow");void el.offsetWidth;el.classList.add("bankGlow");setTimeout(()=>el.classList.remove("bankGlow"),760)}
function checkBank(){'''
if bank_anchor not in s:
    raise SystemExit('checkBank anchor not found')
s=s.replace(bank_anchor,helper,1)

old='flash("✅ BANKED "+pts+" ⭐! +"+pts+" POINT"+(pts===1?"":"S"));carryUI();placeStar();sendState()}'
new='flash("✅ BANKED "+pts+" ⭐! +"+pts+" POINT"+(pts===1?"":"S"));carryUI();bankNinjaGlow(playerId);placeStar();sendState()}'
if old not in s:
    raise SystemExit('Human banking anchor not found')
s=s.replace(old,new,1)

old_bot='score();flash("🏦 "+bot.name+" banked "+pts+" star"+(pts===1?"":"s")+"!");botPlaceStar(bot)'
new_bot='score();flash("🏦 "+bot.name+" banked "+pts+" star"+(pts===1?"":"s")+"!");bankNinjaGlow(bot.id);botPlaceStar(bot)'
if old_bot not in s:
    raise SystemExit('Bot banking anchor not found')
s=s.replace(old_bot,new_bot,1)

p.write_text(s,encoding='utf-8')
print('Installed BANK_NINJA_GLOW_V1')
