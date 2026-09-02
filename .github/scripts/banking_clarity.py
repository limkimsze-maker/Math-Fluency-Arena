from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

marker = 'BANKING_CLARITY_V1'
if marker in s:
    raise SystemExit('Banking clarity patch already installed')

css_anchor = '.base.red{right:1%;background:rgba(255,91,99,.5)}'
css_add = css_anchor + '''\n/* BANKING_CLARITY_V1 — lightweight visual guidance for banking */\n.base.bankReady{border-style:solid;animation:bankPulse .58s ease-in-out infinite alternate;box-shadow:0 0 0 5px rgba(255,216,74,.55),0 0 20px rgba(255,216,74,.8)}\n.base.bankReady::after{content:"🏦 BANK HERE";position:absolute;top:50%;writing-mode:horizontal-tb;white-space:nowrap;transform:translateY(-50%);background:#fff7b2;color:#172033;border:3px solid #172033;border-radius:10px;padding:5px 8px;font-size:14px;font-weight:900;box-shadow:0 3px 0 rgba(23,32,51,.18)}\n.base.blue.bankReady::after{left:calc(100% + 8px)}.base.red.bankReady::after{right:calc(100% + 8px)}\n.base.bankBurst{box-shadow:0 0 0 10px rgba(255,255,255,.9),0 0 32px 18px rgba(255,216,74,.95);filter:brightness(1.35)}\n@keyframes bankPulse{to{box-shadow:0 0 0 9px rgba(255,216,74,.72),0 0 32px 10px rgba(255,216,74,.95);filter:brightness(1.2)}}\n@media(prefers-reduced-motion:reduce){.base.bankReady{animation:none!important}}'''
if css_anchor not in s:
    raise SystemExit('CSS base anchor not found')
s = s.replace(css_anchor, css_add, 1)

old_carry = 'function carryUI(){carryValue.textContent=carried;streakValue.textContent=streak;drawSelf();updateBoostUI();if(!teamAssigned)return;if(carried>=LIMIT){star.style.display="none";hint.textContent="You have 3 ⭐. Get back to your "+team.toUpperCase()+" base!"}else if(roundActive&&Date.now()>=roundStart){star.style.display="block";hint.textContent=carried?"Carry "+carried+" safely to your base — or chase another nearby ⭐.":"Your ⭐ is nearby. Chase it and solve!"}}'
new_carry = '''function updateBankGuide(){world.querySelectorAll(".base").forEach(b=>b.classList.remove("bankReady"));if(teamAssigned&&team&&carried>0&&roundActive&&!finished){const own=world.querySelector(".base."+team);if(own)own.classList.add("bankReady")}}\nfunction carryUI(){carryValue.textContent=carried;streakValue.textContent=streak;drawSelf();updateBoostUI();updateBankGuide();if(!teamAssigned)return;const bankDir=team==="blue"?"← BLUE BASE":"RED BASE →";if(carried>=LIMIT){star.style.display="none";hint.textContent="⭐⭐⭐ FULL! 🏦 BANK NOW — "+bankDir}else if(roundActive&&Date.now()>=roundStart){star.style.display="block";hint.textContent=carried?"🏦 BANK "+carried+" ⭐ — "+bankDir:"Your ⭐ is nearby. Chase it and solve!"}}'''
if old_carry not in s:
    raise SystemExit('carryUI anchor not found')
s = s.replace(old_carry, new_carry, 1)

old_bank = 'function checkBank(){if(!roundActive||Date.now()<roundStart||!team||carried<=0)return;const w=mapW(),inBase=team==="blue"?x<w*BASE:x>w*(1-BASE);if(!inBase||Date.now()-lastBank<700)return;lastBank=Date.now();const pts=carried;carried=0;stats.banked+=pts;const eventId=eid();seenEvents.add(eventId);if(team==="blue")blue+=pts;else red+=pts;score();send({type:"bank",eventId,team,points:pts});flash("🏦 Banked "+pts+" star"+(pts===1?"":"s")+"!");carryUI();placeStar();sendState()}'
new_bank = 'function checkBank(){if(!roundActive||Date.now()<roundStart||!team||carried<=0)return;const w=mapW(),inBase=team==="blue"?x<w*BASE:x>w*(1-BASE);if(!inBase||Date.now()-lastBank<700)return;lastBank=Date.now();const pts=carried,bankBase=world.querySelector(".base."+team);if(bankBase){bankBase.classList.add("bankBurst");setTimeout(()=>bankBase.classList.remove("bankBurst"),700)}carried=0;stats.banked+=pts;const eventId=eid();seenEvents.add(eventId);if(team==="blue")blue+=pts;else red+=pts;score();send({type:"bank",eventId,team,points:pts});flash("✅ BANKED "+pts+" ⭐! +"+pts+" POINT"+(pts===1?"":"S"));carryUI();placeStar();sendState()}'
if old_bank not in s:
    raise SystemExit('checkBank anchor not found')
s = s.replace(old_bank, new_bank, 1)

path.write_text(s, encoding='utf-8')
print('Installed lightweight banking clarity guidance')
