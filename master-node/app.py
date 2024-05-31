from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_tables, get_all_hosts, new_session
from routers import hosts, users
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
from sqlalchemy import Select
from models import HostMachine
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def host_checker():
    print('[CHECKER] : Started host checking')
    db = new_session()
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5)) as session:
        hosts = await db.execute(Select(HostMachine))
        hosts = hosts.scalars().all()
        for host in hosts:
            if host.activated == False:
                continue
            print('[CHECKER] : Checking',host.ip_address,host.port)
            try:
                async with session.get(f'http://{host.ip_address}:{host.port}/healthcheck/') as response:
                    if response.status == 200 and await response.json() == {'status':'ok'}:
                        host.online = True
                    else:
                        host.online = False
            except:
                host.online = False
    await db.commit()
    await db.close()
    print('[CHECKER] : All hosts checked')


@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_tables()
    print("[+] Database created")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(id='job1',func=host_checker,trigger='interval',seconds=60)
    scheduler.start()
    yield
    print('[+] Database connection closed')
    scheduler.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(hosts.router)
app.include_router(users.router)



@app.get('/api/healthcheck')
async def health_check():
    return {
        "status":'ok'
    }





    