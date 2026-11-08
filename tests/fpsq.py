import os
HERE=os.path.dirname(os.path.abspath(__file__))
GAME='file://'+os.path.join(HERE,'..','index.html')
OUT=os.path.join(HERE,'out');os.makedirs(OUT,exist_ok=True)
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get('CHROME') or None,args=['--no-sandbox'])
        for q in ['high','low','auto']:
            pg=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
            await pg.goto(GAME); await pg.evaluate(f"localStorage.setItem('cafe_q',JSON.stringify('{q}'));localStorage.removeItem('cafe_qlv');location.reload()");await pg.wait_for_timeout(600)
            await pg.evaluate("devJump('d29')");await pg.wait_for_timeout(300)
            await pg.evaluate("startPlay();G.clock=430");await pg.wait_for_timeout(7000)
            n=await pg.evaluate("new Promise(r=>{let n=0,t0=performance.now();function f(){n++;if(performance.now()-t0<2000)requestAnimationFrame(f);else r(n/2)}requestAnimationFrame(f)})")
            print(q,'fps',n,'lv',await pg.evaluate("qlv()"))
            await pg.close()
        await b.close()
asyncio.run(main())
