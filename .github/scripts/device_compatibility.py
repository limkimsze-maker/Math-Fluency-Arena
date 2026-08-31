from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'GAMEPLAY_TUNING_V2' in s:
    raise SystemExit('Gameplay tuning is already installed')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'{label} marker not found')
    s = s.replace(old, new, 1)

def regex_once(pattern, replacement, label):
    global s
    s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'{label} marker not found or ambiguous: {n}')
    s = s2

# Bot navigation state for lightweight A* routing and stuck recovery.
old_state = 'let room="",name="",team=null,socket=null,isHost=false,isObserver=false,observerAuthorized=false,observerPin="",pendingObserverPin="",teamAssigned=false,x=100,y=100,starX=300,starY=220,carried=0,immuneUntil=0,blue=0,red=0,streak=0,bestStreak=0,boostStarStreak=0,boostReady=false,boostUntil=0,qOpen=false,qLock=false,questionMode="star",stealTargetId=null,stealTargetName="",mathMode="add20",mapKey="compact",roundStart=0,roundEnd=0,roundActive=false,finished=false,lastFrame=performance.now(),lastSend=0,lastHeartbeat=0,lastBank=0,moved=false,toastTimer,hostTicker=null,facing="right",observerTarget="overview",demoMode=false,demoBot=null,botSolveAt=0,botLastTag=0,hostHadPlayers=false,safeToClose=false;'
new_state = 'let room="",name="",team=null,socket=null,isHost=false,isObserver=false,observerAuthorized=false,observerPin="",pendingObserverPin="",teamAssigned=false,x=100,y=100,starX=300,starY=220,carried=0,immuneUntil=0,blue=0,red=0,streak=0,bestStreak=0,boostStarStreak=0,boostReady=false,boostUntil=0,qOpen=false,qLock=false,questionMode="star",stealTargetId=null,stealTargetName="",mathMode="add20",mapKey="compact",roundStart=0,roundEnd=0,roundActive=false,finished=false,lastFrame=performance.now(),lastSend=0,lastHeartbeat=0,lastBank=0,moved=false,toastTimer,hostTicker=null,facing="right",observerTarget="overview",demoMode=false,demoBot=null,botSolveAt=0,botLastTag=0,botPath=[],botPathIndex=0,botPathAt=0,botTargetKey="",botStuckAt=0,botLastX=0,botLastY=0,hostHadPlayers=false,safeToClose=false;'
replace_once(old_state, new_state, 'state')

# Keep the bot's own stars nearby too, so the demo has a higher Math-question density.
new_bot_star = '''// GAMEPLAY_TUNING_V2
function botPlaceStar(){
  if(!demoBot)return;
  const minTravel=165,maxTravel=420;
  let sx=mapW()*.5,sy=mapH()*.5,found=false;
  for(let i=0;i<220;i++){
    const radius=minTravel+Math.random()*(maxTravel-minTravel),angle=Math.random()*Math.PI*2;
    const px=demoBot.x+Math.cos(angle)*radius,py=demoBot.y+Math.sin(angle)*radius;
    if(starSpotSafe(px,py)){sx=px;sy=py;found=true;break}
  }
  if(!found){
    outer:for(let radius=150;radius<=500;radius+=45){
      for(let angle=0;angle<Math.PI*2;angle+=Math.PI/12){
        const px=demoBot.x+Math.cos(angle)*radius,py=demoBot.y+Math.sin(angle)*radius;
        if(starSpotSafe(px,py)){sx=px;sy=py;found=true;break outer}
      }
    }
  }
  if(!found){sx=mapW()*.5;sy=mapH()*.5}
  demoBot.starX=sx;demoBot.starY=sy;botSolveAt=0;botTargetKey="";botPath=[];botPathIndex=0
}
function initDemoBot'''
regex_once(r'function botPlaceStar\(\)\{\n.*?\n\}\nfunction initDemoBot', new_bot_star, 'bot star')

# Reset routing state whenever the bot demo starts.
old_init = 'players.set(BOT_ID,demoBot);botLastTag=0;botPlaceStar();drawRemote(demoBot)'
new_init = 'players.set(BOT_ID,demoBot);botLastTag=0;botPath=[];botPathIndex=0;botPathAt=0;botTargetKey="";botStuckAt=performance.now();botLastX=demoBot.x;botLastY=demoBot.y;botPlaceStar();drawRemote(demoBot)'
replace_once(old_init, new_init, 'bot init')

# Replace angle-wiggling with lightweight A* pathfinding around map walls.
new_bot_move = '''function botPointBlocked(px,py){
  const pad=30,p=mapProfiles[mapKey]||mapProfiles.compact;
  if(px<28||px>mapW()-28||py<34||py>mapH()-30)return true;
  return p.walls.some(a=>{const rx=mapW()*a[0]/100,ry=mapH()*a[1]/100,rw=mapW()*a[2]/100,rh=mapH()*a[3]/100;return px+pad>rx&&px-pad<rx+rw&&py+pad>ry&&py-pad<ry+rh})
}
function botLineClear(ax,ay,bx,by){
  const dist=Math.hypot(bx-ax,by-ay),steps=Math.max(1,Math.ceil(dist/22));
  for(let i=1;i<=steps;i++){const t=i/steps;if(botPointBlocked(ax+(bx-ax)*t,ay+(by-ay)*t))return false}
  return true
}
function botPlanPath(tx,ty){
  if(!demoBot)return[];
  if(botLineClear(demoBot.x,demoBot.y,tx,ty))return[{x:tx,y:ty}];
  const cell=55,cols=Math.ceil(mapW()/cell),rows=Math.ceil(mapH()/cell),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const point=(gx,gy)=>({gx,gy,x:clamp(gx*cell+cell/2,28,mapW()-28),y:clamp(gy*cell+cell/2,34,mapH()-30)});
  function nearest(px,py){
    const gx0=clamp(Math.floor(px/cell),0,cols-1),gy0=clamp(Math.floor(py/cell),0,rows-1);
    for(let r=0;r<=7;r++)for(let gy=Math.max(0,gy0-r);gy<=Math.min(rows-1,gy0+r);gy++)for(let gx=Math.max(0,gx0-r);gx<=Math.min(cols-1,gx0+r);gx++){
      if(r&&Math.abs(gx-gx0)!==r&&Math.abs(gy-gy0)!==r)continue;const q=point(gx,gy);if(!botPointBlocked(q.x,q.y))return q
    }
    return null
  }
  const start=nearest(demoBot.x,demoBot.y),goal=nearest(tx,ty);if(!start||!goal)return[{x:tx,y:ty}];
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
function botMoveToward(tx,ty,dt){
  if(!demoBot)return;
  const now=performance.now(),targetKey=Math.round(tx/70)+":"+Math.round(ty/70),movedSince=Math.hypot(demoBot.x-botLastX,demoBot.y-botLastY);
  let force=false;if(!botStuckAt)botStuckAt=now;if(now-botStuckAt>700){force=movedSince<9;botLastX=demoBot.x;botLastY=demoBot.y;botStuckAt=now}
  if(force||targetKey!==botTargetKey||now-botPathAt>650||botPathIndex>=botPath.length){botPath=botPlanPath(tx,ty);botPathIndex=0;botPathAt=now;botTargetKey=targetKey}
  while(botPathIndex<botPath.length&&Math.hypot(botPath[botPathIndex].x-demoBot.x,botPath[botPathIndex].y-demoBot.y)<24)botPathIndex++;
  const wp=botPath[botPathIndex]||{x:tx,y:ty},dx=wp.x-demoBot.x,dy=wp.y-demoBot.y,len=Math.hypot(dx,dy);if(len<2)return;
  const step=Math.min(BOT_SPEED*dt,len),nx=Math.max(28,Math.min(mapW()-28,demoBot.x+dx/len*step)),ny=Math.max(34,Math.min(mapH()-30,demoBot.y+dy/len*step));
  if(!botPointBlocked(nx,ny)){demoBot.facing=dx<0?"left":"right";demoBot.x=nx;demoBot.y=ny}else{botPathAt=0;botTargetKey=""}
}
function botStep'''
regex_once(r'function botMoveToward\(tx,ty,dt\)\{\n.*?\n\}\nfunction botStep', new_bot_move, 'bot movement')

# Smarter bot decisions and a slightly fairer contact distance when it tries to grab the player.
new_bot_step = '''function botStep(dt){
  if(!demoMode||!demoBot||!roundActive||finished)return;
  const now=Date.now();demoBot.lastSeen=now;if(now<roundStart){drawRemote(demoBot);return}
  if(qOpen&&questionMode==="steal"){drawRemote(demoBot);return}
  let dPlayer=Math.hypot(x-demoBot.x,y-demoBot.y),canChase=carried>0&&demoBot.carried<LIMIT&&now>=immuneUntil&&dPlayer<320;
  if(canChase){
    botMoveToward(x,y,dt);dPlayer=Math.hypot(x-demoBot.x,y-demoBot.y);
    if(!qOpen&&dPlayer<72&&now-botLastTag>2200){
      botLastTag=now;
      if(Math.random()<.72&&carried>0&&now>=immuneUntil){carried--;demoBot.carried=Math.min(LIMIT,demoBot.carried+1);immuneUntil=now+IMMUNE;flash("🤖 Bot solved and grabbed 1 star!");carryUI();placeStar()}
    }
  }else if(demoBot.carried>=LIMIT){
    botMoveToward(mapW()*.94,mapH()*.5,dt);
  }else{
    botMoveToward(demoBot.starX,demoBot.starY,dt);
    if(Math.hypot(demoBot.x-demoBot.starX,demoBot.y-demoBot.starY)<54){if(!botSolveAt)botSolveAt=now+550+Math.random()*500;if(now>=botSolveAt){if(Math.random()<.82)demoBot.carried=Math.min(LIMIT,demoBot.carried+1);botPlaceStar()}}else botSolveAt=0
  }
  if(demoBot.carried>0&&demoBot.x>mapW()*(1-BASE)){const pts=demoBot.carried;demoBot.carried=0;red+=pts;score();flash("🤖 Bot banked "+pts+" star"+(pts===1?"":"s")+"!");botPlaceStar()}
  drawRemote(demoBot)
}

function connectSocket'''
regex_once(r'function botStep\(dt\)\{\n.*?\n\}\n\nfunction connectSocket', new_bot_step, 'bot step')

# Spawn each pupil's next star inside a nearby ring rather than anywhere across a large map.
new_place_star = '''function placeStar(){
  if(!teamAssigned)return;
  const minTravel=175,maxTravel=460;
  let sx=mapW()*.5,sy=mapH()*.5,found=false;
  for(let i=0;i<260;i++){
    const radius=minTravel+Math.random()*(maxTravel-minTravel),angle=Math.random()*Math.PI*2;
    const px=x+Math.cos(angle)*radius,py=y+Math.sin(angle)*radius;
    if(starSpotSafe(px,py)){sx=px;sy=py;found=true;break}
  }
  if(!found){
    outer:for(let radius=150;radius<=540;radius+=45){
      for(let angle=0;angle<Math.PI*2;angle+=Math.PI/12){
        const px=x+Math.cos(angle)*radius,py=y+Math.sin(angle)*radius;
        if(starSpotSafe(px,py)){sx=px;sy=py;found=true;break outer}
      }
    }
  }
  if(!found){sx=mapW()*.5;sy=mapH()*.5}
  starX=sx;starY=sy;star.style.left=starX+"px";star.style.top=starY+"px";star.style.display=carried<LIMIT?"block":"none"
}
function checkStar'''
regex_once(r'function placeStar\(\)\{\n.*?\n\}\nfunction checkStar', new_place_star, 'player star')

# Bot grabbing: larger demo-only contact radius, respect immunity, and permit contact while stationary.
old_check_tag = 'function checkTag(){if(!roundActive||Date.now()<roundStart||qOpen||carried>=LIMIT)return;const now=Date.now();for(const[id,p]of players){if(p.team===team||p.carried<=0||now-(p.lastSeen||0)>5000||Math.hypot(x-p.x,y-p.y)>TAG)continue;const last=tagCooldown.get(id)||0;if(now-last<1800)continue;tagCooldown.set(id,now);openQuestion("steal",id,p.name);break}}'
new_check_tag = 'function checkTag(){if(!roundActive||Date.now()<roundStart||qOpen||carried>=LIMIT)return;const now=Date.now();for(const[id,p]of players){const reach=demoMode&&id===BOT_ID?84:TAG;if(p.team===team||p.carried<=0||now<(p.immuneUntil||0)||now-(p.lastSeen||0)>5000||Math.hypot(x-p.x,y-p.y)>reach)continue;const last=tagCooldown.get(id)||0;if(now-last<1800)continue;tagCooldown.set(id,now);openQuestion("steal",id,p.name);break}}'
replace_once(old_check_tag, new_check_tag, 'tag check')

old_loop_piece = 'checkStar();checkBank();checkTag()}}if(now-lastHeartbeat>5000)'
new_loop_piece = 'checkStar();checkBank()}}if(roundActive&&Date.now()>=roundStart&&!qOpen){checkTag()}if(now-lastHeartbeat>5000)'
replace_once(old_loop_piece, new_loop_piece, 'stationary tag loop')

p.write_text(s, encoding='utf-8')
