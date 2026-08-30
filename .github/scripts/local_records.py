from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

css='.recordsWrap{overflow:auto;margin:10px 0}.recordsTable{width:100%;border-collapse:collapse;font-size:12px;text-align:center}.recordsTable th,.recordsTable td{border:1px solid #d8dfe8;padding:6px 5px;white-space:nowrap}.recordsTable th{background:#f1f6fb;font-weight:900}.recordsTable td.playerName{text-align:left;font-weight:900}.recordsNote{margin:8px 0;padding:8px;border:2px dashed #b9c5d5;border-radius:10px;background:#f8fbff}.recordsSummary{cursor:pointer;padding:8px 0;font-size:17px}.recordScore{font-weight:900;margin:5px 0 10px}.rankGold{font-weight:900;background:#fff7c7}'
marker='@media(max-width:700px)'
if css not in s:
    if marker not in s: raise SystemExit('media marker not found')
    s=s.replace(marker,css+'\n'+marker,1)

old_host='<button id="startRound" class="btn primary" disabled>Start 3-Minute Round</button><div id="hostMsg" class="msg">The button activates when at least one pupil is ready.</div></div></section>'
new_host='<button id="startRound" class="btn primary" disabled>Start 3-Minute Round</button><div id="hostMsg" class="msg">The button activates when at least one pupil is ready.</div><details><summary class="recordsSummary"><b>📊 Local Player Records</b></summary><div class="recordsNote small">Saved only on this browser/device. No pupil record is uploaded to a separate records database.</div><div id="localRecords"><div class="small">No saved rounds yet.</div></div><button id="clearRecords" class="btn" type="button">Clear Local Records</button></details></div></section>'
if old_host not in s: raise SystemExit('host lobby marker not found')
s=s.replace(old_host,new_host,1)

old_game='<h2 id="hostPhase">Round in progress</h2><div id="hostGameRoster" class="roster"></div><button id="playAgain" class="btn primary" style="display:none">Play Another Round</button>'
new_game='<h2 id="hostPhase">Round in progress</h2><div id="hostGameRoster" class="roster"></div><h2>Player Ranking</h2><div id="hostRoundRanking"><div class="small">Results will appear here when pupils finish the round.</div></div><button id="playAgain" class="btn primary" style="display:none">Play Another Round</button>'
if old_game not in s: raise SystemExit('host game marker not found')
s=s.replace(old_game,new_game,1)

old_dom='hostTimer=$("hostTimer"),hostBlueScore=$("hostBlueScore"),hostRedScore=$("hostRedScore"),hostPhase=$("hostPhase"),hostGameRoster=$("hostGameRoster"),playAgain=$("playAgain"),mathModeSelect=$("mathModeSelect"),hostModeLabel=$("hostModeLabel"),hostMapPreview=$("hostMapPreview"),hostMapLabel=$("hostMapLabel"),'
new_dom='hostTimer=$("hostTimer"),hostBlueScore=$("hostBlueScore"),hostRedScore=$("hostRedScore"),hostPhase=$("hostPhase"),hostGameRoster=$("hostGameRoster"),hostRoundRanking=$("hostRoundRanking"),localRecords=$("localRecords"),clearRecordsBtn=$("clearRecords"),playAgain=$("playAgain"),mathModeSelect=$("mathModeSelect"),hostModeLabel=$("hostModeLabel"),hostMapPreview=$("hostMapPreview"),hostMapLabel=$("hostMapLabel"),'
if old_dom not in s: raise SystemExit('DOM marker not found')
s=s.replace(old_dom,new_dom,1)

old_stats='const playerId=(crypto.randomUUID?crypto.randomUUID():String(Date.now())+Math.random()).slice(0,8),players=new Map(),move={up:false,down:false,left:false,right:false},tagCooldown=new Map(),seenEvents=new Set(),stats={attempts:0,correct:0,collected:0,stolen:0,banked:0};'
if old_stats not in s: raise SystemExit('stats marker not found')
s=s.replace(old_stats,old_stats+'\nconst RECORD_KEY="mathStarChaseLocalRecordsV1",MAX_SAVED_ROUNDS=30;',1)

bank_line=' if(d.type==="bank"){applyBank(d);return}\n'
if bank_line not in s: raise SystemExit('handle bank marker not found')
s=s.replace(bank_line,bank_line+' if(d.type==="roundResult"&&isHost){receiveRoundResult(d);return}\n',1)

old_open='function openHost(code){isHost=true;room=String(code);hostRoomCode.textContent=room;hostGameCode.textContent=room;show($("hostLobby"));connectSocket();startHostTicker()}'
new_open='function openHost(code){isHost=true;room=String(code);hostRoomCode.textContent=room;hostGameCode.textContent=room;show($("hostLobby"));renderLocalRecords();connectSocket();startHostTicker()}'
if old_open not in s: raise SystemExit('openHost marker not found')
s=s.replace(old_open,new_open,1)

score_marker='function score(){blueScore.textContent=blue;redScore.textContent=red;hostBlueScore.textContent=blue;hostRedScore.textContent=red}\n'
if score_marker not in s: raise SystemExit('score marker not found')
records_js=r'''function loadLocalRecords(){try{const v=JSON.parse(localStorage.getItem(RECORD_KEY)||"[]");return Array.isArray(v)?v:[]}catch(e){return[]}}
function saveLocalRecords(v){try{localStorage.setItem(RECORD_KEY,JSON.stringify(v.slice(-MAX_SAVED_ROUNDS)))}catch(e){console.warn("Local records could not be saved",e)}}
function cleanResult(d){const a=Math.max(0,Number(d.attempts)||0),c=Math.max(0,Number(d.correct)||0);return{id:String(d.id||""),name:safe(d.name)||"Player",team:d.team==="red"?"red":"blue",attempts:a,correct:c,accuracy:a?Math.round(c/a*100):0,collected:Math.max(0,Number(d.collected)||0),stolen:Math.max(0,Number(d.stolen)||0),banked:Math.max(0,Number(d.banked)||0),bestStreak:Math.max(0,Number(d.bestStreak)||0)}}
function rankRows(list){return[...(list||[])].sort((a,b)=>b.banked-a.banked||b.correct-a.correct||b.accuracy-a.accuracy||b.stolen-a.stolen||a.name.localeCompare(b.name))}
function getRoundRecord(records,key,seed={}){let r=records.find(x=>String(x.id)===String(key));if(!r){r={id:String(key),savedAt:new Date().toISOString(),room:String(seed.room||room||""),mathMode:seed.mathMode||mathMode,mapKey:seed.mapKey||mapKey,blue:Number(seed.blue)||0,red:Number(seed.red)||0,players:[]};records.push(r)}return r}
function archiveHostRound(){if(!isHost||!roundStart)return;const records=loadLocalRecords(),r=getRoundRecord(records,roundStart,{room,mathMode,mapKey,blue,red});r.savedAt=new Date().toISOString();r.room=room;r.mathMode=mathMode;r.mapKey=mapKey;r.blue=blue;r.red=red;saveLocalRecords(records);renderRoundRanking(r);renderLocalRecords()}
function receiveRoundResult(d){if(!isHost||!d.roundStart)return;const records=loadLocalRecords(),r=getRoundRecord(records,d.roundStart,{room:d.room||room,mathMode:d.mathMode||mathMode,mapKey:d.mapKey||mapKey,blue,red});r.savedAt=new Date().toISOString();r.blue=blue;r.red=red;r.mathMode=d.mathMode||r.mathMode;r.mapKey=d.mapKey||r.mapKey;const row=cleanResult(d),i=r.players.findIndex(x=>x.id===row.id);if(i>=0)r.players[i]=row;else r.players.push(row);saveLocalRecords(records);renderRoundRanking(r);renderLocalRecords()}
function resultTable(rows,allTime=false){if(!rows.length)return'<div class="small">No pupil results received yet.</div>';const body=rows.map((p,i)=>'<tr class="'+(i===0?'rankGold':'')+'"><td>'+(i+1)+'</td><td class="playerName">'+safe(p.name)+'</td>'+(allTime?'<td>'+p.rounds+'</td>':'<td>'+(p.team==="red"?'🔴':'🔵')+'</td>')+'<td>'+p.banked+'</td><td>'+p.correct+'</td><td>'+p.accuracy+'%</td><td>'+p.stolen+'</td>'+(allTime?'':'<td>'+p.collected+'</td><td>'+p.bestStreak+'</td>')+'</tr>').join("");return'<div class="recordsWrap"><table class="recordsTable"><thead><tr><th>#</th><th>Player</th><th>'+(allTime?'Rounds':'Team')+'</th><th>Banked</th><th>Correct</th><th>Accuracy</th><th>Grabbed</th>'+(allTime?'':'<th>Collected</th><th>Best streak</th>')+'</tr></thead><tbody>'+body+'</tbody></table></div>'}
function renderRoundRanking(r=null){if(!hostRoundRanking)return;if(!r&&roundStart){r=loadLocalRecords().find(x=>String(x.id)===String(roundStart))}if(!r){hostRoundRanking.innerHTML='<div class="small">Results will appear here when pupils finish the round.</div>';return}hostRoundRanking.innerHTML='<div class="recordScore">Blue '+r.blue+' — '+r.red+' Red</div>'+resultTable(rankRows(r.players||[]),false)}
function aggregateRecords(records){const m=new Map();for(const r of records)for(const p of(r.players||[])){const k=(p.name||"Player").toLowerCase();let a=m.get(k);if(!a){a={name:p.name||"Player",rounds:0,attempts:0,correct:0,collected:0,stolen:0,banked:0,bestStreak:0};m.set(k,a)}a.rounds++;a.attempts+=Number(p.attempts)||0;a.correct+=Number(p.correct)||0;a.collected+=Number(p.collected)||0;a.stolen+=Number(p.stolen)||0;a.banked+=Number(p.banked)||0;a.bestStreak=Math.max(a.bestStreak,Number(p.bestStreak)||0)}return[...m.values()].map(a=>({...a,accuracy:a.attempts?Math.round(a.correct/a.attempts*100):0})).sort((a,b)=>b.banked-a.banked||b.correct-a.correct||b.accuracy-a.accuracy||a.name.localeCompare(b.name))}
function renderLocalRecords(){if(!localRecords)return;const records=loadLocalRecords();if(!records.length){localRecords.innerHTML='<div class="small">No saved rounds yet.</div>';return}const latest=records[records.length-1],when=new Date(latest.savedAt||Number(latest.id)||Date.now()).toLocaleString(),all=aggregateRecords(records);localRecords.innerHTML='<h3>All-time ranking</h3>'+resultTable(all,true)+'<div class="recordsNote small">Saved rounds: '+records.length+' · Latest: '+when+' · '+(modeNames[latest.mathMode]||latest.mathMode||'Math')+' · Blue '+latest.blue+' — '+latest.red+' Red</div>'}
'''
s=s.replace(score_marker,score_marker+records_js,1)

finish_re=r'function finish\(\)\{.*?results\.classList\.add\("open"\)\}'
m=re.search(finish_re,s,re.S)
if not m: raise SystemExit('finish function not found')
new_finish='function finish(){if(finished)return;finished=true;roundActive=false;boostReady=false;boostUntil=0;updateBoostUI();stop();if(isHost){hostTimer.textContent="0:00";hostPhase.textContent=blue===red?"Draw!":blue>red?"🔵 Blue Wins!":"🔴 Red Wins!";playAgain.style.display="block";archiveHostRound();sendHostSync();return}question.classList.remove("open");qOpen=false;timer.textContent="0:00";winner.textContent=blue===red?"🤝 It\'s a Draw!":blue>red?"🔵 Blue Wins!":"🔴 Red Wins!";finalScore.textContent="Blue "+blue+" — "+red+" Red";sCorrect.textContent=stats.correct;sAccuracy.textContent=stats.attempts?Math.round(stats.correct/stats.attempts*100)+"%":"0%";sStreak.textContent=bestStreak;sCollected.textContent=stats.collected;sStolen.textContent=stats.stolen;sBanked.textContent=stats.banked;send({type:"roundResult",roundStart,id:playerId,name,team,room,mathMode,mapKey,attempts:stats.attempts,correct:stats.correct,collected:stats.collected,stolen:stats.stolen,banked:stats.banked,bestStreak,ts:Date.now()});results.classList.add("open")}'
s=s[:m.start()]+new_finish+s[m.end():]

event_marker='playAgain.addEventListener("click",()=>{show($("hostLobby"));renderHostRoster();hostMsg.textContent="Ready for another round. Press Start when your class is ready."});'
if event_marker not in s: raise SystemExit('event marker not found')
s=s.replace(event_marker,event_marker+'\nif(clearRecordsBtn)clearRecordsBtn.addEventListener("click",()=>{if(confirm("Clear all locally saved player records on this device?")){localStorage.removeItem(RECORD_KEY);renderLocalRecords();if(hostRoundRanking)hostRoundRanking.innerHTML=\'<div class="small">Local records cleared.</div>\'}});',1)

p.write_text(s,encoding='utf-8')
