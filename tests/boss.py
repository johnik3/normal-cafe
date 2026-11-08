import os
HERE=os.path.dirname(os.path.abspath(__file__))
GAME='file://'+os.path.join(HERE,'..','index.html')
OUT=os.path.join(HERE,'out');os.makedirs(OUT,exist_ok=True)
import asyncio
from playwright.async_api import async_playwright
MK="""(()=>{const cu=G.customers.find(c=>c.boss&&c.state==='wait');if(!cu)return 'none';const o=cu.items[0];const gl=o.base[0]==='冰';const c=newCup(gl,null,W/2,L.trayY);c.loc={t:'tray'};c.hasShot=true;c.q1=1;c.settled=true;c.stage={'浓缩':'shot','热美式':'americano','热拿铁':'latte','冰美式':'iceA','冰拿铁':'iceL'}[o.base];c.cubes=gl?5:0;c.mq=1;c.artQ=1;c.cmQ=1;c.art={shape:'heart',size:0.8,q:1};c.artT=0.7;c.milkT=63;serve(cu,c);return o.base;})()"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get('CHROME') or None,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        errs=[];pg.on('pageerror',lambda e: errs.append(str(e)));pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(GAME); await pg.wait_for_timeout(300)
        await pg.evaluate("localStorage.clear();SAVE=freshSave();SAVE.introSeen=1;SAVE.weekMoney=23456;save();devJump('d50');startPlay();")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=os.path.join(OUT,'b1.png'))
        await pg.wait_for_timeout(2600); await pg.screenshot(path=os.path.join(OUT,'b2.png'))
        shots=0
        for i in range(80):
            r=await pg.evaluate(MK)
            ph=await pg.evaluate("G.boss&&G.boss.ph")
            if r!='none' and ph==2 and shots==0:
                await pg.wait_for_timeout(100);await pg.screenshot(path=os.path.join(OUT,'b3.png'));shots=1
            await pg.wait_for_timeout(400)
            if await pg.evaluate("G.boss&&G.boss.ko"): break
        await pg.wait_for_timeout(500); await pg.screenshot(path=os.path.join(OUT,'b4.png'))
        for i in range(30):
            await pg.wait_for_timeout(500)
            if await pg.evaluate("G.scene")!='play': break
        print('scene',await pg.evaluate("G.scene"))
        await pg.evaluate("__go('summary')"); await pg.evaluate("__go('review')"); await pg.wait_for_timeout(2600); await pg.screenshot(path=os.path.join(OUT,'b5.png'))
        print(errs[:5])
        await b.close()
asyncio.run(main())
