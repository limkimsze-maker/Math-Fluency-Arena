from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='''function refreshObserverSelect(){if(!observerSelect)return;const keep=observerTarget;const list=[...players.values()].filter(p=>Date.now()-(p.lastSeen||0)<20000).sort((a,b)=>a.name.localeCompare(b.name));observerSelect.innerHTML='<option value="overview">Whole Game</option>'+list.map(p=>'<option value="'+p.id+'">'+(p.team==="red"?'🔴 ':'🔵 ')+safe(p.name)+'</option>').join("");if(keep!=="overview"&&list.some(p=>p.id===keep))observerSelect.value=keep;else{observerTarget="overview";observerSelect.value="overview"}}'''
new='''function refreshObserverSelect(){if(!observerSelect)return;const keep=observerTarget,list=[...players.values()].filter(p=>Date.now()-(p.lastSeen||0)<20000).sort((a,b)=>a.name.localeCompare(b.name)),sig=list.map(p=>p.id+":"+p.name+":"+p.team).join("|");if(observerSelect.dataset.sig!==sig){observerSelect.dataset.sig=sig;observerSelect.innerHTML='<option value="overview">Whole Game</option>'+list.map(p=>'<option value="'+p.id+'">'+(p.team==="red"?'🔴 ':'🔵 ')+safe(p.name)+'</option>').join("")}if(keep!=="overview"&&list.some(p=>p.id===keep))observerSelect.value=keep;else{observerTarget="overview";observerSelect.value="overview"}}'''
if old not in s:
    raise SystemExit('refreshObserverSelect marker not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
