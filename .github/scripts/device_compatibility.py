from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")

MARKER = "MULTI_BOT_3V3_V1"
if MARKER in s:
    raise SystemExit("3v3 bot demo is already installed")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f"{label} marker not found")
    s = s.replace(old, new, 1)

def regex_once(pattern, replacement, label):
    global s
    s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"{label} marker not found or ambiguous: {n}")
    s = s2

replace_once(
    'demoMode=false,demoBot=null,botSolveAt=0,botLastTag=0,',
    'demoMode=false,demoBot=null,demoBots=[],botSolveAt=0,botLastTag=0,',
    'demo bot state'
)

multi_bot_block = r'''function clearDemoActors(){world.querySelectorAll(".player").forEach(el=>el.remove())}
// MULTI_BOT_3V3_V1
function botPlaceStar(bot){
  if(!bot)return;
  const minTravel=165,maxTravel=420;
  let sx=mapW()*.5,sy=mapH()*.5,found=false;
  for(let i=0;i<220;i++){
    const radius=minTravel+Math.random()*(maxTravel-minTravel),angle=Math.random()*Math.PI*2;
    const px=bot.x+Math.cos(angle)*radius,py=bot.y+Math.sin(angle)*radius;
    if(starSpotSafe(px,py)){sx=px;sy=py;found=true;break}
  }
  if(!found){
    outer:for(let radius=150;radius<=500;radius+=45){
      for(let angle=0;angle<Math.PI*2;angle+=Math.PI/12){
        const px=bot.x+Math.cos(angle)*radius,py=bot.y+Math.sin(angle)*radius;
        if(starSpotSafe(px,py)){sx=px;sy=py;found=true;break outer}
      }
    }
  }
  if(!found){sx=mapW()*.5;sy=mapH()*.5}
  bot.starX=sx;bot.starY=sy;bot._solveAt=0;bot._targetKey="";bot._path=[];bot._pathIndex=0
}
function makeDemoBot(id,name,teamName,yRatio){
  const bx=mapW()*(teamName==="blue"?.11:.89),by=mapH()*yRatio;
  return{id,name,team:teamName,isBot:true,x:bx,y:by,starX:0,starY:0,carried:0,immuneUntil:0,boostUntil:0,facing:teamName==="blue"?"right":"left",lastSeen:Date.now(),_solveAt:0,_lastTag:0,_path:[],_pathIndex:0,_pathAt:0,_targetKey:"",_stuckAt:performance.now(),_lastX:bx,_lastY:by}
}
function initDemoBots(){
  demoBots=[
    makeDemoBot("demo-blue-1","Blue Bot 1","blue",.34),
    makeDemoBot("demo-blue-2","Blue Bot 2","blue",.66),
    makeDemoBot("demo-red-1","Red Bot 1","red",.25),
    makeDemoBot("demo-red-2","Red Bot 2","red",.50),
    makeDemoBot("demo-red-3","Red Bot 3","red",.75)
  ];
  demoBot=demoBots.find(b=>b.team==="red")||null;
  demoBots.forEach(bot=>{players.set(bot.id,bot);botPlaceStar(bot);drawRemote(bot)})
}
function startBotDemo(){
  if(socket){try{socket.close()}catch(e){}socket=null}
  clearInterval(hostTicker);hostTicker=null;stop();players.clear();clearDemoActors();seenEvents.clear();tagCooldown.clear();
  demoMode=true;demoBot=null;demoBots=[];isHost=false;isObserver=false;observerAuthorized=false;room="BOT";name="You";team="blue";teamAssigned=true;observerTarget="overview";
  roomCode.textContent="BOT";status.textContent="OFFLINE 3v3 BOT DEMO";teamBadge.innerHTML='<span class="teamBadge blue">🔵 BLUE TEAM</span>';
  if(resultNote)resultNote.textContent="Browser-only 3v3 bot demo: You + 2 Blue Bots vs 3 Red Bots.";if(demoResultActions)demoResultActions.style.display="none";
  setMap("compact");setMathMode("add20");show($("game"));
  const s=Date.now()+2200,e=s+ROUND;beginRound(s,e,"add20","compact");initDemoBots();
  waitTitle.textContent="3v3 Bot Challenge";waitText.textContent="You + 2 Blue Bots vs 3 Red Bots. Solve, grab stars from Red Bots, and bank more stars to win."
}
function leaveBotDemo(){
  stop();roundActive=false;finished=true;demoMode=false;demoBot=null;demoBots=[];teamAssigned=false;team=null;players.clear();clearDemoActors();star.style.display="none";results.classList.remove("open");waiting.classList.remove("open");show($("lobby"));msg.textContent=""
}
function botPointBlocked(px,py){
  const pad=30,p=mapProfiles[mapKey]||mapProfiles.compact;
  if(px<28||px>mapW()-28||py<34||py>mapH()-30)return true;
  return p.walls.some(a=>{const rx=mapW()*a[0]/100,ry=mapH()*a[1]/100,rw=mapW()*a[2]/100,rh=mapH()*a[3]/100;return px+pad>rx&&px-pad<rx+rw&&py+pad>ry&&py-pad<ry+rh})
}
function botLineClear(ax,ay,bx,by){
  const dist=Math.hypot(bx-ax,by-ay),steps=Math.max(1,Math.ceil(dist/22));
  for(let i=1;i<=steps;i++){const t=i/steps;if(botPointBlocked(ax+(bx-ax)*t,ay+(by-ay)*t))return false}
  return true
}
function botPlanPath(bot,tx,ty){
  if(!bot)return[];
  if(botLineClear(bot.x,bot.y,tx,ty))return[{x:tx,y:ty}];
  const cell=55,cols=Math.ceil(mapW()/cell),rows=Math.ceil(mapH()/cell),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const point=(gx,gy)=>({gx,gy,x:clamp(gx*cell+cell/2,28,mapW()-28),y:clamp(gy*cell+cell/2,34,mapH()-30)});
  function nearest(px,py){
    const gx0=clamp(Math.floor(px/cell),0,cols-1),gy0=clamp(Math.floor(py/cell),0,rows-1);
    for(let r=0;r<=7;r++)for(let gy=Math.max(0,gy0-r);gy<=Math.min(rows-1,gy0+r);gy++)for(let gx=Math.max(0,gx0-r);gx<=Math.min(cols-1,gx0+r);gx++){
      if(r&&Math.abs(gx-gx0)!==r&&Math.abs(gy-gy0)!==r)continue;const q=point(gx,gy);if(!botPointBlocked(q.x,q.y))return q
    }
    return null
  }
  const start=nearest(bot.x,bot.y),goal=nearest(tx,ty);if(!start||!goal)return[{x:tx,y:ty}];
  const key=(gx,gy)=>gy*cols+gx,sk=key(start.gx,start.gy),gk=key(goal.gx,goal.gy),open=new Set([sk]),came=new Map(),g=new Map([[sk,0]]),f=new Map([[sk,Math.hypot(goal.gx-start.gx,goal.gy-start.gy)]]);
  const dirs=[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];
  let guard=0;
  while(open.size&&guard++<cols*rows*4){
    let cur=null,best=Infinity;for(const k of open){const score=f.get(k)??Infinity;if(score<best){best=score;cur=k}}
    if(cur===gk)break;open.delete(cur);const cgx=cur%cols,cgy=Math.floor(cur/cols);
    for(const[dgx,dgy]of dirs){const ngx=cgx+dgx,ngy=cgy+dgy;if(ngx<0||ngy<0||ngx>=cols||ngy>=rows)continue;const np=point(ngx,ngy);if(botPointBlocked(np.x,np.y))continue;if(dgx&&dgy){const a=point(cgx+dgx,cgy),b=point(cgx,cgy+dgy);if(botPointBlocked(a.x,a.y)||botPointBlocked(b.x,b.y))continue}const nk=key(ngx,ngy),tent=(g.get(cur)??Infinity)+(dgx&&dgy?1.414:1);if(tent<(g.get(nk)??Infinity)){came.set(nk,cur);g.set(nk,tent);f.set(nk,tent+Math.hypot(goal.gx-ngx,goal.gy-ngy));open.add(nk)}}
  }
  if(gk!==sk&&!came.has(gk))return[{x:tx,y:ty}];
  const rev=[];let cur=gk;while(cur!==sk){const gx=cur%cols,gy=Math.floor(cur/cols),q=point(gx,gy);rev.push({x:q.x,y:q.y});cur=came.get(cur);if(cur==null)break}rev.reverse();rev.push({x:tx,y:ty});
  return rev
}
function botMoveToward(bot,tx,ty,dt){
  if(!bot)return;
  const now=performance.now(),targetKey=Math.round(tx/70)+":"+Math.round(ty/70),movedSince=Math.hypot(bot.x-bot._lastX,bot.y-bot._lastY);
  let force=false;if(!bot._stuckAt)bot._stuckAt=now;if(now-bot._stuckAt>700){force=movedSince<9;bot._lastX=bot.x;bot._lastY=bot.y;bot._stuckAt=now}
  if(force||targetKey!==bot._targetKey||now-bot._pathAt>800||bot._pathIndex>=bot._path.length){bot._path=botPlanPath(bot,tx,ty);bot._pathIndex=0;bot._pathAt=now;bot._targetKey=targetKey}
  while(bot._pathIndex<bot._path.length&&Math.hypot(bot._path[bot._pathIndex].x-bot.x,bot._path[bot._pathIndex].y-bot.y)<24)bot._pathIndex++;
  const wp=bot._path[bot._pathIndex]||{x:tx,y:ty},dx=wp.x-bot.x,dy=wp.y-bot.y,len=Math.hypot(dx,dy);if(len<2)return;
  const speed=BOT_SPEED*(bot.team==="red"?.96:1),step=Math.min(speed*dt,len),nx=Math.max(28,Math.min(mapW()-28,bot.x+dx/len*step)),ny=Math.max(34,Math.min(mapH()-30,bot.y+dy/len*step));
  if(!botPointBlocked(nx,ny)){bot.facing=dx<0?"left":"right";bot.x=nx;bot.y=ny}else{bot._pathAt=0;bot._targetKey=""}
}
function nearestDemoEnemy(bot){
  const now=Date.now(),candidates=[];
  if(bot.team!=="blue"&&!qOpen&&carried>0&&now>=immuneUntil)candidates.push({kind:"human",x,y,name:"You",distance:Math.hypot(x-bot.x,y-bot.y)});
  for(const other of demoBots){
    if(other.id===bot.id||other.team===bot.team||other.carried<=0||now<other.immuneUntil)continue;
    candidates.push({kind:"bot",bot:other,x:other.x,y:other.y,name:other.name,distance:Math.hypot(other.x-bot.x,other.y-bot.y)})
  }
  candidates.sort((a,b)=>a.distance-b.distance);
  return candidates.length&&candidates[0].distance<270?candidates[0]:null
}
function botSteal(bot,target,now){
  if(!target||bot.carried>=LIMIT)return false;
  if(target.kind==="human"){
    if(carried<=0||now<immuneUntil)return false;
    carried--;immuneUntil=now+IMMUNE;bot.carried=Math.min(LIMIT,bot.carried+1);flash("🤖 "+bot.name+" grabbed 1 of your stars!");carryUI();placeStar();return true
  }
  const victim=target.bot;
  if(!victim||victim.carried<=0||now<victim.immuneUntil)return false;
  victim.carried--;victim.immuneUntil=now+IMMUNE;bot.carried=Math.min(LIMIT,bot.carried+1);drawRemote(victim);return true
}
function botStepOne(bot,dt){
  if(!demoMode||!bot||!roundActive||finished)return;
  const now=Date.now();bot.lastSeen=now;if(now<roundStart){drawRemote(bot);return}
  if(qOpen&&questionMode==="steal"&&stealTargetId===bot.id){drawRemote(bot);return}
  if(bot.carried>=LIMIT){
    botMoveToward(bot,bot.team==="blue"?mapW()*.06:mapW()*.94,mapH()*.5,dt)
  }else{
    const target=nearestDemoEnemy(bot);
    if(target){
      const tx=target.kind==="human"?x:target.bot.x,ty=target.kind==="human"?y:target.bot.y;
      botMoveToward(bot,tx,ty,dt);
      const fx=target.kind==="human"?x:target.bot.x,fy=target.kind==="human"?y:target.bot.y,d=Math.hypot(fx-bot.x,fy-bot.y);
      if(d<72&&now-bot._lastTag>2300){bot._lastTag=now;if(Math.random()<.68)botSteal(bot,target,now)}
    }else{
      botMoveToward(bot,bot.starX,bot.starY,dt);
      if(Math.hypot(bot.x-bot.starX,bot.y-bot.starY)<54){
        if(!bot._solveAt)bot._solveAt=now+650+Math.random()*650;
        if(now>=bot._solveAt){
          const solveChance=bot.team==="blue"?.82:.76;
          if(Math.random()<solveChance)bot.carried=Math.min(LIMIT,bot.carried+1);
          botPlaceStar(bot)
        }
      }else bot._solveAt=0
    }
  }
  const inBase=bot.team==="blue"?bot.x<mapW()*BASE:bot.x>mapW()*(1-BASE);
  if(bot.carried>0&&inBase){
    const pts=bot.carried;bot.carried=0;if(bot.team==="blue")blue+=pts;else red+=pts;score();flash("🏦 "+bot.name+" banked "+pts+" star"+(pts===1?"":"s")+"!");botPlaceStar(bot)
  }
  drawRemote(bot)
}
function botDemoStep(dt){for(const bot of demoBots)botStepOne(bot,dt)}'''

regex_once(
    r'function clearDemoActors\(\)\{.*?\n\}\n\nfunction connectSocket',
    multi_bot_block + '\n\nfunction connectSocket',
    'bot demo block'
)

old_steal = 'if(mode==="steal"){if(demoMode&&targetId===BOT_ID&&demoBot&&demoBot.carried>0&&Date.now()>=demoBot.immuneUntil){demoBot.carried--;demoBot.immuneUntil=Date.now()+IMMUNE;carried=Math.min(LIMIT,carried+1);stats.stolen++;feedback.textContent="Correct! ⚡ You grabbed 1 ⭐ from Bot!";carryUI();drawRemote(demoBot)}else{feedback.textContent="Correct! ⚡ Grab unlocked!";if(targetId)send({type:"tagAttempt",taggerId:playerId,targetId,taggerName:name,challengePassed:true,ts:Date.now()})}}'
new_steal = 'if(mode==="steal"){const demoTarget=demoMode?players.get(targetId):null;if(demoTarget&&demoTarget.isBot&&demoTarget.team!==team&&demoTarget.carried>0&&Date.now()>=demoTarget.immuneUntil){demoTarget.carried--;demoTarget.immuneUntil=Date.now()+IMMUNE;carried=Math.min(LIMIT,carried+1);stats.stolen++;feedback.textContent="Correct! ⚡ You grabbed 1 ⭐ from "+safe(demoTarget.name)+"!";carryUI();drawRemote(demoTarget)}else{feedback.textContent="Correct! ⚡ Grab unlocked!";if(targetId)send({type:"tagAttempt",taggerId:playerId,targetId,taggerName:name,challengePassed:true,ts:Date.now()})}}'
replace_once(old_steal, new_steal, 'player steals from bots')

replace_once(
    'const reach=demoMode&&id===BOT_ID?84:TAG;',
    'const reach=demoMode&&p.isBot?84:TAG;',
    'bot steal reach'
)

replace_once(
    'if(demoMode)botStep(dt);',
    'if(demoMode)botDemoStep(dt);',
    'multi bot loop'
)

s = s.replace('🤖 Try the Game vs Bot', '🤖 Try 3v3 vs Bots', 1)

p.write_text(s, encoding="utf-8")
print("Installed MULTI_BOT_3V3_V1")
