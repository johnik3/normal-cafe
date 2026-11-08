import os
HERE=os.path.dirname(os.path.abspath(__file__))
GAME='file://'+os.path.join(HERE,'..','index.html')
OUT=os.path.join(HERE,'out');os.makedirs(OUT,exist_ok=True)
import asyncio,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get('CHROME') or None,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True)
        errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(GAME)
        await pg.wait_for_timeout(500)
        scenes=set()
        # walk 55 days using devSkip, buying stuff along the way by script
        for step in range(400):
            sc=await pg.evaluate('__G.scene')
            scenes.add(sc)
            d=await pg.evaluate('__S().day')
            if d>55: break
            if sc=='shop':
                await pg.evaluate("""(()=>{const S=__S();S.weekMoney+=2000;for(const t of ['dev','lure','cup']){}})()""")
                # buy everything affordable via scene down on boxes
                for t in ['dev','lure','cup']:
                    await pg.evaluate(f"(()=>{{const sh=window.__SC.shop;sh.tab='{t}';}})()")
                    await pg.wait_for_timeout(120)
                    boxes=await pg.evaluate("window.__SC.shop.boxes.map(b=>[b.x+b.w-40,b.y+b.h/2])")
                    for bx,by in boxes:
                        await pg.evaluate(f"window.__SC.shop.down({bx},{by})")
                await pg.wait_for_timeout(50)
            await pg.evaluate("document.getElementById('devBtn').click()")
            await pg.evaluate("document.querySelector('[data-a=skip]').click()")
            await pg.wait_for_timeout(60)
        print('scenes',sorted(scenes))
        print('day',await pg.evaluate('__S().day'),'lures',await pg.evaluate('__S().lures'),'staff',await pg.evaluate('__S().staff'))
        print('errors',errs[:10])
        await b.close()
asyncio.run(main())
