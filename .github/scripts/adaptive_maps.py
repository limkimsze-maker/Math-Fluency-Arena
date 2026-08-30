from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

new_maps = r'''const mapProfiles={
 compact:{name:"Compact",w:1300,h:820,paths:[[12,24,76,8],[12,68,76,8]],walls:[[23,11,4,27],[23,56,4,31],[73,11,4,31],[73,60,4,27],[37,29,22,4],[42,66,21,4],[48,40,4,16]],bushes:[[33,46],[65,48],[50,20]]},
 standard:{name:"Standard",w:1700,h:1050,paths:[[11,20,78,8],[11,72,78,8]],walls:[[18,10,4,26],[18,54,4,34],[31,24,4,31],[31,70,4,18],[45,10,4,25],[45,50,4,38],[59,24,4,31],[59,70,4,18],[73,10,4,26],[73,54,4,34],[22,42,21,4],[57,42,21,4]],bushes:[[25,64],[38,18],[50,62],[64,18],[77,64]]},
 large:{name:"Large",w:2100,h:1300,paths:[[10,18,80,8],[10,74,80,8],[17,46,66,8]],walls:[[16,9,4,26],[16,52,4,37],[27,22,4,30],[27,69,4,20],[38,9,4,26],[38,50,4,39],[49,22,4,26],[49,65,4,24],[60,9,4,26],[60,50,4,39],[71,22,4,30],[71,69,4,20],[82,9,4,26],[82,52,4,37],[20,41,16,4],[64,41,16,4],[42,58,16,4]],bushes:[[23,61],[34,17],[45,76],[55,17],[66,76],[77,61],[50,36]]},
 mega:{name:"Mega",w:2500,h:1550,paths:[[9,17,82,8],[9,76,82,8],[15,46,70,8]],walls:[[14,8,4,28],[14,53,4,38],[24,21,4,31],[24,70,4,21],[34,8,4,28],[34,51,4,40],[44,21,4,27],[44,65,4,26],[54,8,4,28],[54,51,4,40],[64,21,4,27],[64,65,4,26],[74,8,4,28],[74,51,4,40],[84,21,4,31],[84,70,4,21],[18,41,14,4],[38,58,17,4],[68,41,14,4],[58,74,14,4]],bushes:[[20,61],[30,15],[40,78],[50,34],[60,15],[70,78],[80,61],[50,72],[30,50],[70,50]]}
};
function chooseMapForCount'''

s2, n = re.subn(r'const mapProfiles=\{.*?\n\};\nfunction chooseMapForCount', new_maps, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not replace mapProfiles block')
s = s2

old_star = 'function placeStar(){if(!teamAssigned)return;const m=90,w=Math.max(20,mapW()-m*2),h=Math.max(20,mapH()-m*2);let sx=m,sy=m,found=false;for(let i=0;i<120;i++){const px=m+Math.random()*w,py=m+Math.random()*h;if(starSpotSafe(px,py)){sx=px;sy=py;found=true;break}}if(!found){const spots=[[.5,.5],[.5,.2],[.5,.8],[.35,.5],[.65,.5],[.25,.35],[.75,.65]];const safe=spots.find(([fx,fy])=>starSpotSafe(mapW()*fx,mapH()*fy));if(safe){sx=mapW()*safe[0];sy=mapH()*safe[1]}}starX=sx;starY=sy;star.style.left=starX+"px";star.style.top=starY+"px";star.style.display=carried<LIMIT?"block":"none"}'
new_star = 'function placeStar(){if(!teamAssigned)return;const m=90,view=Math.max(150,Math.min(320,Math.min(arena.clientWidth,arena.clientHeight)*.48));let sx=x,sy=y,found=false;for(let i=0;i<100;i++){const a=Math.random()*Math.PI*2,d=105+Math.random()*Math.max(45,view-105),px=Math.max(m,Math.min(mapW()-m,x+Math.cos(a)*d)),py=Math.max(m,Math.min(mapH()-m,y+Math.sin(a)*d));if(Math.hypot(px-x,py-y)>85&&starSpotSafe(px,py)){sx=px;sy=py;found=true;break}}if(!found){const w=Math.max(20,mapW()-m*2),h=Math.max(20,mapH()-m*2);for(let i=0;i<160;i++){const px=m+Math.random()*w,py=m+Math.random()*h;if(starSpotSafe(px,py)){sx=px;sy=py;found=true;break}}}if(!found){sx=mapW()*.5;sy=mapH()*.5}starX=sx;starY=sy;star.style.left=starX+"px";star.style.top=starY+"px";star.style.display=carried<LIMIT?"block":"none"}'
if old_star not in s:
    raise SystemExit('Could not find current placeStar function')
s = s.replace(old_star, new_star, 1)

old_css = '.star{position:absolute;transform:translate(-50%,-50%);font-size:45px;z-index:8;animation:bob 1s ease-in-out infinite alternate;filter:drop-shadow(0 3px 0 rgba(100,70,0,.25))}'
new_css = '.star{position:absolute;transform:translate(-50%,-50%);font-size:52px;z-index:8;animation:bob .8s ease-in-out infinite alternate;filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 12px #ffd84a) drop-shadow(0 3px 0 rgba(100,70,0,.25))}'
if old_css not in s:
    raise SystemExit('Could not find star CSS')
s = s.replace(old_css, new_css, 1)

s = s.replace('hint.textContent="Find your ⭐, solve, then bank it at your base!"', 'hint.textContent="Your next ⭐ is nearby — chase it, solve, then bank!"', 1)
s = s.replace('hint.textContent=carried?"Carry "+carried+" safely to your base — or collect more.":"Find your ⭐ and solve the Math question."', 'hint.textContent=carried?"Carry "+carried+" safely to your base — or chase another nearby ⭐.":"Your ⭐ is nearby. Chase it and solve!"', 1)

p.write_text(s, encoding='utf-8')
