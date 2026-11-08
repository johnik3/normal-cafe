import os
HERE=os.path.dirname(os.path.abspath(__file__))
GAME='file://'+os.path.join(HERE,'..','index.html')
OUT=os.path.join(HERE,'out');os.makedirs(OUT,exist_ok=True)
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get('CHROME') or None,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        errs=[];pg.on('pageerror',lambda e: errs.append(str(e)));pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(GAME); await pg.wait_for_timeout(300)
        await pg.evaluate("document.getElementById('devBtn').click()"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=os.path.join(OUT,'devpanel.png'))
        js=await pg.evaluate("[...document.querySelectorAll('[data-j]')].map(b=>b.dataset.j)")
        for j in js:
            await pg.evaluate(f"devJump('{j}')"); await pg.wait_for_timeout(500)
            if await pg.evaluate("G.scene")=='open':
                await pg.evaluate("if(!OP.story||OP.story.ph==='done'){startPlay();}"); await pg.wait_for_timeout(1500)
            print(j, await pg.evaluate("[G.scene,SAVE.day,Object.keys(SAVE.staff).filter(k=>SAVE.staff[k]).join(','),SAVE.lures.join(','),SAVE.story,SAVE.weekMoney]"))
        print('errors',errs[:6]); await b.close()
asyncio.run(main())
