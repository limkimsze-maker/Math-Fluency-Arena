from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'SCARCE_SHARED_STARS_V1' in s:
    raise SystemExit('Scarce shared stars patch already applied')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit('Could not find: ' + label)
    s = s.replace(old, new, 1)

replace_once(
    '/* SHARED_STAR_PRACTICE_V1 — same central star field for everyone; stars are reusable practice stations */',
    '/* SCARCE_SHARED_STARS_V1 — shared central stars are scarce; first player to reach one claims it for everyone */',
    'shared star marker',
)

replace_once(
    'hostHadPlayers=false,safeToClose=false,sharedStars=[],sharedStarCooldownUntil=0;',
    'hostHadPlayers=false,safeToClose=false,sharedStars=[],sharedStarCooldownUntil=0,pendingStarClaimId="";',
    'shared star state',
)

replace_once(
    'function sharedStarCountForPlayers(n){return n<=8?6:n<=16?8:n<=24?10:12}',
    'function sharedStarCountForPlayers(n){return n<=8?2:n<=16?3:n<=24?4:5}',
    'scarce star scaling',
)

replace_once(
    'const out=[],w=mapW(),h=mapH(),minSep=count>=12?105:count>=10?115:125;',
    'const out=[],w=mapW(),h=mapH(),minSep=count>=5?155:count>=4?165:175;',
    'shared star separation',
)

replace_once(
    '  tryFill(minSep,1800);if(out.length<count)tryFill(minSep*.68,1800);\n  return out\n}\nfunction renderSharedStars(){',
    '''  tryFill(minSep,1800);if(out.length<count)tryFill(minSep*.72,1800);\n  return out\n}\nfunction makeReplacementSharedStar(existing){\n  const list=Array.isArray(existing)?existing:[],w=mapW(),h=mapH(),id="s"+Date.now().toString(36)+Math.random().toString(36).slice(2,5);\n  function pick(sep,tries){for(let i=0;i<tries;i++){const px=w*(.27+Math.random()*.46),py=h*(.18+Math.random()*.64);if(!starSpotSafe(px,py))continue;if(list.some(q=>Math.hypot(q.x-px,q.y-py)<sep))continue;return{id,x:Math.round(px),y:Math.round(py)}}return null}\n  return pick(155,1200)||pick(105,1200)||{id,x:Math.round(w*.5),y:Math.round(h*.5)}\n}\nfunction renderSharedStars(){''',
    'replacement star helper',
)

replace_once(
    'function checkStar(){if(!roundActive||Date.now()<roundStart||qOpen||carried>=LIMIT)return;if(demoMode){if(Math.hypot(x-starX,y-starY)<58)openQuestion();return}const now=Date.now();if(now<sharedStarCooldownUntil)return;for(const s of sharedStars){if(Math.hypot(x-s.x,y-s.y)<72){sharedStarCooldownUntil=now+850;openQuestion();break}}}',
    '''function checkStar(){if(!roundActive||Date.now()<roundStart||qOpen||carried>=LIMIT)return;if(demoMode){if(Math.hypot(x-starX,y-starY)<58)openQuestion();return}const now=Date.now();if(now<sharedStarCooldownUntil||pendingStarClaimId)return;for(const s of sharedStars){if(Math.hypot(x-s.x,y-s.y)<64){pendingStarClaimId=s.id;sharedStarCooldownUntil=now+1200;send({type:"starClaim",starId:s.id,id:playerId,x,y,ts:now});setTimeout(()=>{if(pendingStarClaimId===s.id)pendingStarClaimId=""},1300);break}}}\nfunction handleStarClaim(d){\n  if(!isHost||!roundActive||Date.now()<roundStart)return;\n  const starId=String(d.starId||""),idx=sharedStars.findIndex(s=>s.id===starId);if(idx<0)return;\n  const p=players.get(d.id);if(!p||Date.now()-(p.lastSeen||0)>6000)return;\n  const claimed=sharedStars[idx];if(Math.hypot((Number(p.x)||0)-claimed.x,(Number(p.y)||0)-claimed.y)>115)return;\n  sharedStars.splice(idx,1);sharedStars.push(makeReplacementSharedStar(sharedStars));renderSharedStars();updateObserver();\n  send({type:"starAwarded",targetId:d.id,starId:claimed.id,sharedStars,ts:Date.now()});sendHostSync()\n}\nfunction applyStarAward(d){\n  if(Array.isArray(d.sharedStars)){sharedStars=sanitiseSharedStars(d.sharedStars);renderSharedStars();if(isHost||isObserver)updateObserver()}\n  if(d.targetId===playerId&&!isHost&&!isObserver){pendingStarClaimId="";if(roundActive&&Date.now()>=roundStart&&!qOpen&&carried<LIMIT)openQuestion()}\n  else if(pendingStarClaimId&&!sharedStars.some(s=>s.id===pendingStarClaimId))pendingStarClaimId=""\n}''',
    'scarce star claim logic',
)

replace_once(
    'if(d.type==="startRound"){if(isObserver){beginObserverRound(d.startAt,d.endAt,d.mathMode,d.mapKey)}else beginRound(d.startAt,d.endAt,d.mathMode,d.mapKey,d.sharedStars);return}\n if(d.type==="hostSync")',
    'if(d.type==="startRound"){if(isObserver){beginObserverRound(d.startAt,d.endAt,d.mathMode,d.mapKey)}else beginRound(d.startAt,d.endAt,d.mathMode,d.mapKey,d.sharedStars);return}\n if(d.type==="starClaim"&&isHost){handleStarClaim(d);return}\n if(d.type==="starAwarded"){applyStarAward(d);return}\n if(d.type==="hostSync")',
    'websocket star handlers',
)

replace_once(
    'sharedStarCooldownUntil=0;Object.keys(stats)',
    'sharedStarCooldownUntil=0;pendingStarClaimId="";Object.keys(stats)',
    'reset pending claim',
)

replace_once(
    'hint.textContent=carried?"🏦 BANK "+carried+" ⭐ — "+bankDir:"Head to any ⭐ in the centre and solve!"',
    'hint.textContent=carried?"🏦 BANK "+carried+" ⭐ — "+bankDir:"Race to a shared ⭐ — first there gets it!"',
    'carry hint',
)

replace_once(
    'hint.textContent=demoMode?"Your next ⭐ is nearby — chase it, solve, then bank!":"Shared ⭐ are spread through the centre — choose any one and solve!"',
    'hint.textContent=demoMode?"Your next ⭐ is nearby — chase it, solve, then bank!":"Shared ⭐ are scarce — race to the centre and snatch one first!"',
    'round start hint',
)

replace_once(
    'Head to any shared ⭐ in the centre, solve, carry up to 3, tag an opponent and solve correctly to grab one, then bank at your base. Shared stars stay available so everyone gets practice. Solve 3 star questions correctly in a row to earn a 7-second Speed Boost.',
    'Race to the scarce shared ⭐ in the centre. The first player to reach one claims it and gets the question. Solve correctly, carry up to 3, tag an opponent and solve correctly to grab one, then bank at your base. A claimed star disappears for everyone and a new one respawns elsewhere in the centre. Solve 3 star questions correctly in a row to earn a 7-second Speed Boost.',
    'instructions',
)

required = [
    'SCARCE_SHARED_STARS_V1',
    'n<=8?2:n<=16?3:n<=24?4:5',
    'function makeReplacementSharedStar',
    'type:"starClaim"',
    'type:"starAwarded"',
    'function handleStarClaim',
    'function applyStarAward',
    'Math.hypot(x-s.x,y-s.y)<64',
    'A claimed star disappears for everyone and a new one respawns elsewhere in the centre.',
]
for item in required:
    if item not in s:
        raise SystemExit('Missing expected scarce-star marker: ' + item)

p.write_text(s, encoding='utf-8')
print('Changed shared stars to scarce first-claim wins: 2/3/4/5 by class size.')
