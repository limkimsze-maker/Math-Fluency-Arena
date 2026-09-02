from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

if 'GRABBER_IMMUNITY_V1' in s:
    raise SystemExit('Grabber immunity patch is already installed')

replacements = [
    (
        'function botSteal(bot,target,now){\n  if(!target||bot.carried>=LIMIT)return false;',
        '// GRABBER_IMMUNITY_V1 — after any successful grab, the grabber gets 2 seconds of immunity\nfunction botSteal(bot,target,now){\n  if(!target||bot.carried>=LIMIT)return false;'
    ),
    (
        'carried--;immuneUntil=now+IMMUNE;bot.carried=Math.min(LIMIT,bot.carried+1);flash("🤖 "+bot.name+" grabbed 1 of your stars!");',
        'carried--;bot.carried=Math.min(LIMIT,bot.carried+1);bot.immuneUntil=now+IMMUNE;flash("🤖 "+bot.name+" grabbed 1 of your stars!");'
    ),
    (
        'victim.carried--;victim.immuneUntil=now+IMMUNE;bot.carried=Math.min(LIMIT,bot.carried+1);drawRemote(victim);return true',
        'victim.carried--;bot.carried=Math.min(LIMIT,bot.carried+1);bot.immuneUntil=now+IMMUNE;drawRemote(victim);return true'
    ),
    (
        'demoTarget.carried--;demoTarget.immuneUntil=Date.now()+IMMUNE;carried=Math.min(LIMIT,carried+1);stats.stolen++;',
        'demoTarget.carried--;carried=Math.min(LIMIT,carried+1);immuneUntil=Date.now()+IMMUNE;stats.stolen++;'
    ),
    (
        'carried--;immuneUntil=now+IMMUNE;flash("💫 "+safe(d.taggerName||"Opponent")+" solved correctly and grabbed 1 star!");',
        'carried--;flash("💫 "+safe(d.taggerName||"Opponent")+" solved correctly and grabbed 1 star!");'
    ),
    (
        'function tagSuccess(d){if(!roundActive||Date.now()<roundStart||carried>=LIMIT)return;carried++;stats.stolen++;',
        'function tagSuccess(d){if(!roundActive||Date.now()<roundStart||carried>=LIMIT)return;carried++;immuneUntil=Date.now()+IMMUNE;stats.stolen++;'
    ),
]

for old, new in replacements:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'Expected exactly one match, found {count}: {old[:90]}')
    s = s.replace(old, new, 1)

path.write_text(s, encoding='utf-8')
print('Installed universal 2-second grabber immunity')
