from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'BOT_DEMO_V1' in s:
    print('Bot demo already installed')
    raise SystemExit(0)

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(label + ' marker not found')
    s = s.replace(old, new, 1)

# Small responsive styles and a marker for CI.
rep('.siteCredit{width:100%;text-align:center;padding:12px 8px 18px;font-size:13px;font-weight:800;color:#66758d}\n',
    '.siteCredit{width:100%;text-align:center;padding:12px 8px 18px;font-size:13px;font-weight:800;color:#66758d}\n/* BOT_DEMO_V1 */\n#demoResultActions{display:none;margin-top:10px}\n#demoResultActions .btn{margin:5px 0}\n',
    'credit CSS')

# Put the browser-only trial first on the landing screen.
rep('<p class="small">Teachers create a room. Pupils join with the 4-digit code.</p><button id="create" class="btn primary">Create Live Class Room</button>',
    '<p class="small">Teachers create a room. Pupils join with the 4-digit code.</p><button id="tryBot" class="btn primary">🤖 Try the Game vs Bot</button><div class="small">Browser-only demo · no room code needed</div><button id="create" class="btn">Create Live Class Room</button>',
    'lobby demo button')

# Add demo-only result actions so a trial user is never trapped at the end screen.
rep('<div class="small">Waiting for the teacher to start another round.</div></div></div></div>',
    '<div id="resultNote" class="small">Waiting for the teacher to start another round.</div><div id="demoResultActions"><button id="demoAgain" class="btn primary" type="button">🤖 Play Bot Again</button><button id="demoHome" class="btn" type="button">Back to Home</button></div></div></div></div>',
    'results actions')

# DOM references.
rep('createBtn=$("create"),joinBtn=$("join"),creatorBtn=$("creator"),roomInput=$("roomInput"),msg=$("msg"),creatorPassword=$("creatorPassword"),',
    'tryBotBtn=$("tryBot"),createBtn=$("create"),joinBtn=$("join"),creatorBtn=$("creator"),roomInput=$("roomInput"),msg=$("msg"),creatorPassword=$("creatorPassword"),',
    'try bot DOM')
rep('sCorrect=$("sCorrect"),sAccuracy=$("sAccuracy"),sStreak=$("sStreak"),sCollected=$("sCollected"),sStolen=$("sStolen"),sBanked=$("sBanked");',
    'sCorrect=$("sCorrect"),sAccuracy=$("sAccuracy"),sStreak=$("sStreak"),sCollected=$("sCollected"),sStolen=$("sStolen"),sBanked=$("sBanked"),resultNote=$("resultNote"),demoResultActions=$("demoResultActions"),demoAgain=$("demoAgain"),demoHome=$("demoHome");',
    'demo result DOM')

rep('const RECORD_KEY="mathStarChaseLocalRecordsV1",MAX_SAVED_ROUNDS=30;',
    'const RECORD_KEY="mathStarChaseLocalRecordsV1",MAX_SAVED_ROUNDS=30,BOT_ID="demo-bot",BOT_SPEED=170;',
    'bot constants')
rep('hostTicker=null,facing="right",observerTarget="overview";',
    'hostTicker=null,facing="right",observerTarget="overview",demoMode=false,demoBot=null,botSolveAt=0,botLastTag=0;',
    'bot state')

# Browser-only bot mode. These function declarations may call helpers declared later in the file.
bot_code = r'''
function clearDemoActors(){world.querySelectorAll(".player").forEach(el=>el.remove())}
function botPlaceStar(){
  if(!demoBot)return;
  const side=Math.max(210,mapW()*.18),top=90,minTravel=Math.min(400,Math.max(170,Math.min(mapW(),mapH())*.2));
  let sx=mapW()*.5,sy=mapH()*.5,found=false;
  for(let i=0;i<180;i++){
    const px=side+Math.random()*Math.max(20,mapW()-side*2),py=top+Math.random()*Math.max(20,mapH()-top*2);
    if(Math.hypot(px-demoBot.x,py-demoBot.y)>=minTravel&&starSpotSafe(px,py)){sx=px;sy=py;found=true;break}
  }
  if(!found){sx=mapW()*.5;sy=mapH()*.5}
  demoBot.starX=sx;demoBot.starY=sy;botSolveAt=0
}
function initDemoBot(){
  demoBot={id:BOT_ID,name:"Bot",team:"red",x:mapW()*.90,y:mapH()*.5,starX:0,starY:0,carried:0,immuneUntil:0,boostUntil:0,facing:"left",lastSeen:Date.now()};
  players.set(BOT_ID,demoBot);botLastTag=0;botPlaceStar();drawRemote(demoBot)
}
function startBotDemo(){
  if(socket){try{socket.close()}catch(e){}socket=null}
  clearInterval(hostTicker);hostTicker=null;stop();players.clear();clearDemoActors();seenEvents.clear();tagCooldown.clear();
  demoMode=true;isHost=false;room="BOT";name="You";team="blue";teamAssigned=true;observerTarget="overview";
  roomCode.textContent="BOT";status.textContent="OFFLINE BOT DEMO";teamBadge.innerHTML='<span class="teamBadge blue">🔵 BLUE TEAM</span>';
  if(resultNote)resultNote.textContent="Browser-only bot demo.";if(demoResultActions)demoResultActions.style.display="none";
  setMap("compact");setMathMode("add20");show($("game"));
  const s=Date.now()+2200,e=s+ROUND;beginRound(s,e,"add20","compact");initDemoBot();
  waitTitle.textContent="Bot Challenge";waitText.textContent="You are Blue. Beat the Red Bot by solving, grabbing and banking more stars."
}
function leaveBotDemo(){
  stop();roundActive=false;finished=true;demoMode=false;demoBot=null;teamAssigned=false;team=null;players.clear();clearDemoActors();star.style.display="none";results.classList.remove("open");waiting.classList.remove("open");show($("lobby"));msg.textContent=""
}
function botMoveToward(tx,ty,dt){
  if(!demoBot)return;
  const dx=tx-demoBot.x,dy=ty-demoBot.y,len=Math.hypot(dx,dy);if(len<2)return;
  const base=Math.atan2(dy,dx),step=BOT_SPEED*dt,tries=[0,.55,-.55,1.1,-1.1,Math.PI];
  for(const a of tries){
    const ang=base+a,nx=Math.max(28,Math.min(mapW()-28,demoBot.x+Math.cos(ang)*step)),ny=Math.max(34,Math.min(mapH()-30,demoBot.y+Math.sin(ang)*step));
    if(!blocked(nx,ny)){demoBot.facing=Math.cos(ang)<0?"left":"right";demoBot.x=nx;demoBot.y=ny;return}
  }
}
function botStep(dt){
  if(!demoMode||!demoBot||!roundActive||finished)return;
  const now=Date.now();demoBot.lastSeen=now;if(now<roundStart){drawRemote(demoBot);return}
  if(qOpen&&questionMode==="steal"){drawRemote(demoBot);return}
  const dPlayer=Math.hypot(x-demoBot.x,y-demoBot.y),canChase=carried>0&&demoBot.carried<LIMIT&&now>=immuneUntil&&dPlayer<250;
  if(canChase){
    botMoveToward(x,y,dt);
    if(!qOpen&&dPlayer<TAG+5&&now-botLastTag>2200){
      botLastTag=now;
      if(Math.random()<.72&&carried>0&&now>=immuneUntil){
        carried--;demoBot.carried=Math.min(LIMIT,demoBot.carried+1);immuneUntil=now+IMMUNE;flash("🤖 Bot solved and grabbed 1 star!");carryUI();placeStar()
      }
    }
  }else if(demoBot.carried>=LIMIT){
    botMoveToward(mapW()*.94,mapH()*.5,dt);
  }else{
    botMoveToward(demoBot.starX,demoBot.starY,dt);
    if(Math.hypot(demoBot.x-demoBot.starX,demoBot.y-demoBot.starY)<54){
      if(!botSolveAt)botSolveAt=now+550+Math.random()*500;
      if(now>=botSolveAt){if(Math.random()<.82)demoBot.carried=Math.min(LIMIT,demoBot.carried+1);botPlaceStar()}
    }else botSolveAt=0
  }
  if(demoBot.carried>0&&demoBot.x>mapW()*(1-BASE)){
    const pts=demoBot.carried;demoBot.carried=0;red+=pts;score();flash("🤖 Bot banked "+pts+" star"+(pts===1?"":"s")+"!");botPlaceStar()
  }
  drawRemote(demoBot)
}
'''
rep('function connectSocket(){if(socket&&socket.readyState<=1)return;', bot_code + '\nfunction connectSocket(){if(socket&&socket.readyState<=1)return;', 'bot function insertion')

# A correct steal question against the bot transfers the star locally instead of using WebSockets.
old_steal = 'if(mode==="steal"){feedback.textContent="Correct! ⚡ Grab unlocked!";if(targetId)send({type:"tagAttempt",taggerId:playerId,targetId,taggerName:name,challengePassed:true,ts:Date.now()})}'
new_steal = 'if(mode==="steal"){if(demoMode&&targetId===BOT_ID&&demoBot&&demoBot.carried>0&&Date.now()>=demoBot.immuneUntil){demoBot.carried--;demoBot.immuneUntil=Date.now()+IMMUNE;carried=Math.min(LIMIT,carried+1);stats.stolen++;feedback.textContent="Correct! ⚡ You grabbed 1 ⭐ from Bot!";carryUI();drawRemote(demoBot)}else{feedback.textContent="Correct! ⚡ Grab unlocked!";if(targetId)send({type:"tagAttempt",taggerId:playerId,targetId,taggerName:name,challengePassed:true,ts:Date.now()})}}'
rep(old_steal, new_steal, 'local bot steal')

# Keep the bot running during the round; unlike the player it can continue while a normal star question is open.
rep('function loop(now){const dt=Math.min(.05,(now-lastFrame)/1000);lastFrame=now;updateRoundClock();updateBoostUI();if(!isHost)prune();',
    'function loop(now){const dt=Math.min(.05,(now-lastFrame)/1000);lastFrame=now;updateRoundClock();updateBoostUI();if(demoMode)botStep(dt);if(!isHost)prune();',
    'bot loop')

# Demo results never attempt a backend result submission and offer rematch/home buttons.
old_finish_tail = 'sStolen.textContent=stats.stolen;sBanked.textContent=stats.banked;send({type:"roundResult",roundStart,id:playerId,name,team,room,mathMode,mapKey,attempts:stats.attempts,correct:stats.correct,collected:stats.collected,stolen:stats.stolen,banked:stats.banked,bestStreak,ts:Date.now()});results.classList.add("open")}'
new_finish_tail = 'sStolen.textContent=stats.stolen;sBanked.textContent=stats.banked;if(demoMode){if(resultNote)resultNote.textContent="Browser-only demo complete. No live room or server quota was used.";if(demoResultActions)demoResultActions.style.display="block"}else{if(resultNote)resultNote.textContent="Waiting for the teacher to start another round.";if(demoResultActions)demoResultActions.style.display="none";send({type:"roundResult",roundStart,id:playerId,name,team,room,mathMode,mapKey,attempts:stats.attempts,correct:stats.correct,collected:stats.collected,stolen:stats.stolen,banked:stats.banked,bestStreak,ts:Date.now()})}results.classList.add("open")}'
rep(old_finish_tail, new_finish_tail, 'demo finish')

# Button bindings.
rep('createBtn.addEventListener("click",createRoom);joinBtn.addEventListener("click",joinRoom);',
    'tryBotBtn.addEventListener("click",startBotDemo);createBtn.addEventListener("click",createRoom);joinBtn.addEventListener("click",joinRoom);',
    'try bot binding')
rep('if(observerSelect)observerSelect.addEventListener("change",()=>{observerTarget=observerSelect.value||"overview";updateObserver()});\n',
    'if(observerSelect)observerSelect.addEventListener("change",()=>{observerTarget=observerSelect.value||"overview";updateObserver()});\nif(demoAgain)demoAgain.addEventListener("click",startBotDemo);if(demoHome)demoHome.addEventListener("click",leaveBotDemo);\n',
    'demo result bindings')

p.write_text(s, encoding='utf-8')
print('Installed browser-only bot demo')
