from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'IMMUNITY_VISUAL_V1' in s:
    raise SystemExit('IMMUNITY_VISUAL_V1 already installed')

old='.player.immune .ninja{animation:flash .25s linear infinite alternate}.player.boosting .ninja{filter:drop-shadow(0 0 4px #fff) drop-shadow(0 0 10px #ffd84a) drop-shadow(0 0 18px #ff9f1a)}.player.boosting::after{content:"⚡";position:absolute;left:50%;top:-28px;transform:translateX(-50%);font-size:18px;filter:drop-shadow(0 1px 1px #172033)}@keyframes flash{to{opacity:.35}}'
new='/* IMMUNITY_VISUAL_V1 — clear, lightweight 2-second getaway protection */\n.player.immune{border-radius:50%;outline:3px solid #fff;outline-offset:2px;box-shadow:0 0 0 6px rgba(73,216,255,.9),0 0 20px 8px rgba(73,216,255,.62);animation:immuneHalo .34s ease-in-out infinite alternate}.player.immune::before{content:"🛡️ SAFE 2s";position:absolute;left:50%;top:-34px;transform:translateX(-50%);z-index:25;white-space:nowrap;background:#e8fbff;color:#075a78;border:2px solid #075a78;border-radius:999px;padding:2px 6px;font-size:10px;font-weight:900;line-height:1.2}.player.immune .ninja{opacity:1}.player.boosting .ninja{filter:drop-shadow(0 0 4px #fff) drop-shadow(0 0 10px #ffd84a) drop-shadow(0 0 18px #ff9f1a)}.player.boosting::after{content:"⚡";position:absolute;left:50%;top:-28px;transform:translateX(-50%);font-size:18px;filter:drop-shadow(0 1px 1px #172033)}@keyframes immuneHalo{to{box-shadow:0 0 0 8px rgba(73,216,255,.72),0 0 28px 12px rgba(73,216,255,.72)}}'
if old not in s:
    raise SystemExit('old immunity CSS marker not found')
s=s.replace(old,new,1)

old_feedback='feedback.textContent="Correct! ⚡ You grabbed 1 ⭐ from "+safe(demoTarget.name)+"!";'
new_feedback='feedback.textContent="Correct! ⭐ GRABBED from "+safe(demoTarget.name)+"! 🛡️ SAFE 2s — RUN!";'
if old_feedback not in s:
    raise SystemExit('player-v-bot success feedback not found')
s=s.replace(old_feedback,new_feedback,1)

old_flash='flash("⚡ You grabbed 1 star from "+safe(d.targetName||"an opponent")+"!");'
new_flash='flash("⭐ GRABBED! 🛡️ SAFE 2s — RUN!");'
if old_flash not in s:
    raise SystemExit('player-v-player success flash not found')
s=s.replace(old_flash,new_flash,1)

p.write_text(s,encoding='utf-8')
