from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

marker='BANK_INSIDE_BASE_V1'
if marker in s:
    raise SystemExit('BANK_INSIDE_BASE_V1 already installed')

old_bot='''  const inBase=bot.team==="blue"?bot.x<mapW()*BASE:bot.x>mapW()*(1-BASE);\n  if(bot.carried>0&&inBase){\n    const pts=bot.carried;bot.carried=0;if(bot.team==="blue")blue+=pts;else red+=pts;score();flash("🏦 "+bot.name+" banked "+pts+" star"+(pts===1?"":"s")+"!");botPlaceStar(bot)\n  }'''
new_bot='''  const inBase=fullyInsideOwnBase(bot.x,bot.y,bot.team);\n  if(bot.carried>0&&inBase){\n    const pts=bot.carried;bot.carried=0;if(bot.team==="blue")blue+=pts;else red+=pts;score();flash("🏦 "+bot.name+" banked "+pts+" star"+(pts===1?"":"s")+"!");botPlaceStar(bot)\n  }'''
if old_bot not in s:
    raise SystemExit('Bot banking anchor not found')
s=s.replace(old_bot,new_bot,1)

old_target='''  if(bot.carried>=LIMIT){\n    botMoveToward(bot,bot.team==="blue"?mapW()*.06:mapW()*.94,mapH()*.5,dt)'''
new_target='''  if(bot.carried>=LIMIT){\n    const home=baseCentre(bot.team);botMoveToward(bot,home.x,home.y,dt)'''
if old_target not in s:
    raise SystemExit('Bot base target anchor not found')
s=s.replace(old_target,new_target,1)

old_check='''function checkBank(){if(!roundActive||Date.now()<roundStart||!team||carried<=0)return;const w=mapW(),inBase=team==="blue"?x<w*BASE:x>w*(1-BASE);if(!inBase||Date.now()-lastBank<700)return;lastBank=Date.now();const pts=carried,bankBase=world.querySelector(".base."+team);if(bankBase){bankBase.classList.add("bankBurst");setTimeout(()=>bankBase.classList.remove("bankBurst"),650)}carried=0;stats.banked+=pts;const eventId=eid();seenEvents.add(eventId);if(team==="blue")blue+=pts;else red+=pts;score();send({type:"bank",eventId,team,points:pts});flash("✅ BANKED "+pts+" ⭐! +"+pts+" POINT"+(pts===1?"":"S"));carryUI();placeStar();sendState()}'''
new_check='''// BANK_INSIDE_BASE_V1 — banking only when the ninja body is inside its own visible base\nfunction baseBounds(teamName){\n  const w=mapW(),h=mapH();\n  return teamName==="blue"?{left:w*.01,right:w*.08,top:h*.12,bottom:h*.88}:{left:w*.92,right:w*.99,top:h*.12,bottom:h*.88}\n}\nfunction baseCentre(teamName){const b=baseBounds(teamName);return{x:(b.left+b.right)/2,y:(b.top+b.bottom)/2}}\nfunction fullyInsideOwnBase(px,py,teamName){\n  if(teamName!=="blue"&&teamName!=="red")return false;\n  const b=baseBounds(teamName),halfW=27,halfH=28;\n  return px-halfW>=b.left&&px+halfW<=b.right&&py-halfH>=b.top&&py+halfH<=b.bottom\n}\nfunction checkBank(){if(!roundActive||Date.now()<roundStart||!team||carried<=0)return;const inBase=fullyInsideOwnBase(x,y,team);if(!inBase||Date.now()-lastBank<700)return;lastBank=Date.now();const pts=carried,bankBase=world.querySelector(".base."+team);if(bankBase){bankBase.classList.add("bankBurst");setTimeout(()=>bankBase.classList.remove("bankBurst"),650)}carried=0;stats.banked+=pts;const eventId=eid();seenEvents.add(eventId);if(team==="blue")blue+=pts;else red+=pts;score();send({type:"bank",eventId,team,points:pts});flash("✅ BANKED "+pts+" ⭐! +"+pts+" POINT"+(pts===1?"":"S"));carryUI();placeStar();sendState()}'''
if old_check not in s:
    raise SystemExit('Player banking anchor not found')
s=s.replace(old_check,new_check,1)

p.write_text(s,encoding='utf-8')
print('Installed BANK_INSIDE_BASE_V1')
