from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'SHARED_STAR_PRACTICE_V1' in s:
    raise SystemExit('Shared star practice patch already applied')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit('Could not find: ' + label)
    s = s.replace(old, new, 1)

# Mark and style the shared central practice stars.
replace_once(
    '.star{position:absolute;transform:translate(-50%,-50%);font-size:52px;z-index:8;animation:bob .8s ease-in-out infinite alternate;filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 12px #ffd84a) drop-shadow(0 3px 0 rgba(100,70,0,.25))}@keyframes bob{to{transform:translate(-50%,-58%) scale(1.06)}}',
    '/* SHARED_STAR_PRACTICE_V1 — same central star field for everyone; stars are reusable practice stations */\n.star{position:absolute;transform:translate(-50%,-50%);font-size:52px;z-index:8;animation:bob .8s ease-in-out infinite alternate;filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 12px #ffd84a) drop-shadow(0 3px 0 rgba(100,70,0,.25))}.sharedStar{pointer-events:none}@keyframes bob{to{transform:translate(-50%,-58%) scale(1.06)}}',
    'star CSS',
)

# Remove old shared stars whenever a map is rebuilt.
replace_once(
    'world.querySelectorAll(".path,.base,.wall,.bush,.jpDecor,.themeDecor").forEach(el=>el.remove());',
    'world.querySelectorAll(".path,.base,.wall,.bush,.jpDecor,.themeDecor,.sharedStar").forEach(el=>el.remove());',
    'map cleanup selector',
)

# Shared-star client state.
replace_once(
    'hostHadPlayers=false,safeToClose=false;',
    'hostHadPlayers=false,safeToClose=false,sharedStars=[],sharedStarCooldownUntil=0;',
    'state tail',
)

# Add host-generated shared star field helpers immediately before legacy personal-star placement.
replace_once(
    'function placeStar(){\n  if(!teamAssigned)return;',
    '''function sharedStarCountForPlayers(n){return n<=8?6:n<=16?8:n<=24?10:12}\nfunction sanitiseSharedStars(list){return(Array.isArray(list)?list:[]).slice(0,16).map((a,i)=>({id:String(a&&a.id||("s"+i)).slice(0,12),x:Math.round(Number(a&&a.x)||0),y:Math.round(Number(a&&a.y)||0)})).filter(a=>a.x>0&&a.y>0&&a.x<mapW()&&a.y<mapH())}\nfunction makeSharedStars(count){\n  const out=[],w=mapW(),h=mapH(),minSep=count>=12?105:count>=10?115:125;\n  function tryFill(sep,tries){for(let i=0;i<tries&&out.length<count;i++){const px=w*(.27+Math.random()*.46),py=h*(.18+Math.random()*.64);if(!starSpotSafe(px,py))continue;if(out.some(q=>Math.hypot(q.x-px,q.y-py)<sep))continue;out.push({id:"s"+out.length,x:Math.round(px),y:Math.round(py)})}}\n  tryFill(minSep,1800);if(out.length<count)tryFill(minSep*.68,1800);\n  return out\n}\nfunction renderSharedStars(){\n  if(!world)return;world.querySelectorAll(".sharedStar").forEach(el=>el.remove());\n  if(demoMode||!sharedStars.length)return;\n  sharedStars.forEach(s=>{const el=document.createElement("div");el.className="star sharedStar";el.dataset.sharedStar=s.id;el.textContent="⭐";el.style.left=s.x+"px";el.style.top=s.y+"px";world.appendChild(el)})\n}\nfunction placeStar(){\n  if(!teamAssigned)return;\n  if(!demoMode){star.style.display="none";renderSharedStars();return}''',
    'placeStar start',
)

# Shared stations have a larger trigger radius and are not consumed by one player.
replace_once(
    'function checkStar(){if(!roundActive||Date.now()<roundStart||qOpen||carried>=LIMIT)return;if(Math.hypot(x-starX,y-starY)<52)openQuestion()}',
    'function checkStar(){if(!roundActive||Date.now()<roundStart||qOpen||carried>=LIMIT)return;if(demoMode){if(Math.hypot(x-starX,y-starY)<58)openQuestion();return}const now=Date.now();if(now<sharedStarCooldownUntil)return;for(const s of sharedStars){if(Math.hypot(x-s.x,y-s.y)<72){sharedStarCooldownUntil=now+850;openQuestion();break}}}',
    'checkStar',
)

# Host creates one shared star layout for the entire room, scaled to class size.
replace_once(
    'function startByHost(){if(!isHost||startRoundBtn.disabled)return;setMathMode(mathModeSelect.value);const n=[...players.values()].filter(p=>Date.now()-(p.lastSeen||0)<15000).length;setMap(chooseMapForCount(n));const s=Date.now()+START_DELAY,e=s+ROUND;resetRound();roundStart=s;roundEnd=e;send({type:"startRound",startAt:s,endAt:e,mathMode,mapKey});beginRound(s,e,mathMode,mapKey)}',
    'function startByHost(){if(!isHost||startRoundBtn.disabled)return;setMathMode(mathModeSelect.value);const n=[...players.values()].filter(p=>Date.now()-(p.lastSeen||0)<15000).length;setMap(chooseMapForCount(n));const s=Date.now()+START_DELAY,e=s+ROUND;resetRound();sharedStars=makeSharedStars(sharedStarCountForPlayers(n));roundStart=s;roundEnd=e;send({type:"startRound",startAt:s,endAt:e,mathMode,mapKey,sharedStars});beginRound(s,e,mathMode,mapKey,sharedStars)}',
    'startByHost',
)

replace_once(
    'function beginRound(s,e,mode=mathMode,map=mapKey){setMathMode(mode);setMap(map);s=Number(s)||Date.now()+1000;e=Number(e)||s+ROUND;roundStart=s;roundEnd=e;roundActive=true;finished=false;resetRound(false);if(isHost){show($("hostGame"));hostPhase.textContent="Get ready…";hostTimer.textContent="3:00";playAgain.style.display="none";renderObserverMap();refreshObserverSelect();requestAnimationFrame(updateObserver)}else{spawnPlayer();placeStar();drawSelf();sendState();results.classList.remove("open");waiting.classList.add("open");waitTitle.textContent="Get ready!";waitText.textContent="";startCount.style.display="block";updateBoostUI()}}',
    'function beginRound(s,e,mode=mathMode,map=mapKey,stars=null){setMathMode(mode);setMap(map);s=Number(s)||Date.now()+1000;e=Number(e)||s+ROUND;roundStart=s;roundEnd=e;roundActive=true;finished=false;if(!demoMode&&Array.isArray(stars))sharedStars=sanitiseSharedStars(stars);if(demoMode)sharedStars=[];resetRound(false);renderSharedStars();if(isHost){show($("hostGame"));hostPhase.textContent="Get ready…";hostTimer.textContent="3:00";playAgain.style.display="none";renderObserverMap();refreshObserverSelect();requestAnimationFrame(updateObserver)}else{spawnPlayer();placeStar();drawSelf();sendState();results.classList.remove("open");waiting.classList.add("open");waitTitle.textContent="Get ready!";waitText.textContent="";startCount.style.display="block";updateBoostUI()}}',
    'beginRound',
)

replace_once(
    'function resetRound(clearTimes=true){blue=0;red=0;carried=0;streak=0;bestStreak=0;immuneUntil=0;boostStarStreak=0;boostReady=false;boostUntil=0;Object.keys(stats).forEach(k=>stats[k]=0);finished=false;if(clearTimes){roundStart=0;roundEnd=0;roundActive=false}score();carryUI();updateBoostUI();results.classList.remove("open")}',
    'function resetRound(clearTimes=true){blue=0;red=0;carried=0;streak=0;bestStreak=0;immuneUntil=0;boostStarStreak=0;boostReady=false;boostUntil=0;sharedStarCooldownUntil=0;Object.keys(stats).forEach(k=>stats[k]=0);finished=false;if(clearTimes){roundStart=0;roundEnd=0;roundActive=false;sharedStars=[];renderSharedStars()}score();carryUI();updateBoostUI();results.classList.remove("open")}',
    'resetRound',
)

# Every player receives exactly the same host-generated coordinates, including reconnecting players.
replace_once(
    'if(d.type==="startRound"){if(isObserver){beginObserverRound(d.startAt,d.endAt,d.mathMode,d.mapKey)}else beginRound(d.startAt,d.endAt,d.mathMode,d.mapKey);return}',
    'if(d.type==="startRound"){if(isObserver){beginObserverRound(d.startAt,d.endAt,d.mathMode,d.mapKey)}else beginRound(d.startAt,d.endAt,d.mathMode,d.mapKey,d.sharedStars);return}',
    'startRound handler',
)

replace_once(
    'function sendHostSync(){if(!isHost)return;send({type:"hostSync",blue,red,roundStart,roundEnd,mathMode,mapKey,active:roundActive&&!finished,finished,ts:Date.now()})}',
    'function sendHostSync(){if(!isHost)return;send({type:"hostSync",blue,red,roundStart,roundEnd,mathMode,mapKey,sharedStars,active:roundActive&&!finished,finished,ts:Date.now()})}',
    'sendHostSync',
)

replace_once(
    'function applyHostSync(d){if(isHost)return;if(isObserver){if(observerAuthorized)applyObserverSync(d);return}if(d.mathMode)setMathMode(d.mathMode);if(d.mapKey)setMap(d.mapKey);blue=Math.max(blue,Number(d.blue)||0);red=Math.max(red,Number(d.red)||0);score();const e=Number(d.roundEnd)||0,s=Number(d.roundStart)||0;if(d.active&&e>Date.now()&&!roundActive)beginRound(s,e,d.mathMode||mathMode,d.mapKey||mapKey)}',
    'function applyHostSync(d){if(isHost)return;if(isObserver){if(observerAuthorized)applyObserverSync(d);return}if(d.mathMode)setMathMode(d.mathMode);if(d.mapKey)setMap(d.mapKey);if(Array.isArray(d.sharedStars)){sharedStars=sanitiseSharedStars(d.sharedStars);renderSharedStars()}blue=Math.max(blue,Number(d.blue)||0);red=Math.max(red,Number(d.red)||0);score();const e=Number(d.roundEnd)||0,s=Number(d.roundStart)||0;if(d.active&&e>Date.now()&&!roundActive)beginRound(s,e,d.mathMode||mathMode,d.mapKey||mapKey,sharedStars)}',
    'applyHostSync',
)

# Host observer always sees the same shared star field.
replace_once(
    "observerWorld.querySelectorAll('.obsStar').forEach(el=>el.remove());const vw=",
    "observerWorld.querySelectorAll('.obsStar').forEach(el=>el.remove());sharedStars.forEach(s=>{const st=document.createElement(\"div\");st.className=\"obsStar\";st.textContent=\"⭐\";st.style.left=s.x+\"px\";st.style.top=s.y+\"px\";observerWorld.appendChild(st)});const vw=",
    'observer shared stars',
)

old_personal_observer = ';if(target.starX>0&&target.starY>0&&target.carried<LIMIT){const st=document.createElement("div");st.className="obsStar";st.textContent="⭐";st.style.left=target.starX+"px";st.style.top=target.starY+"px";observerWorld.appendChild(st)}'
if old_personal_observer not in s:
    raise SystemExit('Could not find selected-player personal observer star')
s = s.replace(old_personal_observer, '', 1)

# Shared stars stay visible; carrying three only stops new question triggers until the player banks.
replace_once(
    'function carryUI(){carryValue.textContent=carried;streakValue.textContent=streak;drawSelf();updateBoostUI();updateBankGuide();if(!teamAssigned)return;const bankDir=team==="blue"?"← BLUE BASE":"RED BASE →";if(carried>=LIMIT){star.style.display="none";hint.textContent="⭐⭐⭐ FULL! 🏦 BANK NOW — "+bankDir}else if(roundActive&&Date.now()>=roundStart){star.style.display="block";hint.textContent=carried?"🏦 BANK "+carried+" ⭐ — "+bankDir:"Your ⭐ is nearby. Chase it and solve!"}}',
    'function carryUI(){carryValue.textContent=carried;streakValue.textContent=streak;drawSelf();updateBoostUI();updateBankGuide();if(!teamAssigned)return;const bankDir=team==="blue"?"← BLUE BASE":"RED BASE →";if(!demoMode){star.style.display="none";renderSharedStars();if(carried>=LIMIT){hint.textContent="⭐⭐⭐ FULL! 🏦 BANK NOW — "+bankDir}else if(roundActive&&Date.now()>=roundStart){hint.textContent=carried?"🏦 BANK "+carried+" ⭐ — "+bankDir:"Head to any ⭐ in the centre and solve!"}return}if(carried>=LIMIT){star.style.display="none";hint.textContent="⭐⭐⭐ FULL! 🏦 BANK NOW — "+bankDir}else if(roundActive&&Date.now()>=roundStart){star.style.display="block";hint.textContent=carried?"🏦 BANK "+carried+" ⭐ — "+bankDir:"Your ⭐ is nearby. Chase it and solve!"}}',
    'carryUI',
)

replace_once(
    'hint.textContent="Your next ⭐ is nearby — chase it, solve, then bank!"',
    'hint.textContent=demoMode?"Your next ⭐ is nearby — chase it, solve, then bank!":"Shared ⭐ are spread through the centre — choose any one and solve!"',
    'round-start hint',
)

replace_once(
    'Move to your ⭐, solve, carry up to 3, tag an opponent and solve correctly to grab one, then bank at your base. Solve 3 personal stars correctly in a row to earn a 7-second Speed Boost.',
    'Head to any shared ⭐ in the centre, solve, carry up to 3, tag an opponent and solve correctly to grab one, then bank at your base. Shared stars stay available so everyone gets practice. Solve 3 star questions correctly in a row to earn a 7-second Speed Boost.',
    'player instructions',
)

# Safety checks.
required = [
    'SHARED_STAR_PRACTICE_V1',
    'function sharedStarCountForPlayers',
    'n<=8?6:n<=16?8:n<=24?10:12',
    'function makeSharedStars',
    'function renderSharedStars',
    'sharedStars=makeSharedStars(sharedStarCountForPlayers(n))',
    'sharedStars,active:roundActive',
    'Math.hypot(x-s.x,y-s.y)<72',
    'Shared stars stay available so everyone gets practice.',
]
for item in required:
    if item not in s:
        raise SystemExit('Missing expected shared-star marker: ' + item)

p.write_text(s, encoding='utf-8')
print('Added reusable shared central stars: 6/8/10/12 by class size.')
