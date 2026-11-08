import os
HERE=os.path.dirname(os.path.abspath(__file__))
GAME='file://'+os.path.join(HERE,'..','index.html')
OUT=os.path.join(HERE,'out');os.makedirs(OUT,exist_ok=True)
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get('CHROME') or None,args=['--no-sandbox'])
        for (w,h) in [(375,667),(360,640)]:
            pg=await b.new_page(viewport={'width':w,'height':h},device_scale_factor=2)
            await pg.goto(GAME); await pg.wait_for_timeout(300)
            await pg.evaluate("devJump('d43')");await pg.wait_for_timeout(200)
            await pg.evaluate("(()=>{startPlay();G.clock=450;G.spawnT=0.1;})()");await pg.wait_for_timeout(4000)
            await pg.screenshot(path=os.path.join(OUT,f'sm_{w}.png'))
            await pg.evaluate("G.endedDay=30;SAVE.day=31;go('shop')");await pg.wait_for_timeout(900)
            await pg.screenshot(path=os.path.join(OUT,f'sm_shop_{w}.png'))
            await pg.close()
        await b.close()
asyncio.run(main())
