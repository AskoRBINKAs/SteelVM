from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from subprocess import Popen, PIPE
import aiohttp
import psutil
import sys
import os


load_dotenv()

TOKEN = os.environ['TOKEN']
MASTER_NODE_URL = os.environ['MASTER_NODE_URL']

@asynccontextmanager
async def lifespan(app:FastAPI):
    sys_info = dict()
    sys_info['host_os'] = sys.platform
    sys_info['cpu_count'] = os.cpu_count()
    sys_info['ram_count'] = psutil.virtual_memory().total
    sys_info['port'] = os.environ['PORT']
    sys_info['vm_type'] = os.environ['TYPE']
    async with aiohttp.ClientSession(headers={"Authorization":f'Bearer {TOKEN}'}) as session:
        if os.environ['ENV']=='DEV':
            sys_info['ip_address'] = '127.0.0.1'
        else:
            async with session.get('http://ident.me') as response:
                sys_info['ip_address'] = await response.text()
        print('[+] Fetched system info:',sys_info)
        async with session.post(MASTER_NODE_URL+f'/api/hosts/{TOKEN}/',json=sys_info) as response:
            if response.status != 200:
                print('[!] Failed to authorize in master node. Check your access token and URL to master node')
                exit(-1)
    print('[+] Authorization successful')
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/healthcheck")
async def health_check():
    return {'status':'ok'}

@app.get('/vms/')
async def get_list_vms(only_running:bool=False):
    if only_running:
        proc = os.popen("vboxmanage list runningvms")
    else:
        proc = os.popen("vboxmanage list vms")
    data = proc.read().split('\n')
    response = []
    for line in data:
        if len(line)==0:
            continue
        name = line.split("\" ")[0].replace('\"','')
        uid = line.split("\" ")[1]
        response.append({'name':name,'uuid':uid})
    return response

@app.post('/vms/{uid}/')
async def act_with_vm(uid:str, action:str):
    match action:
        case "start":
            proc = os.popen(f'vboxmanage startvm "{uid}" --type headless')
        case "stop":
            proc = os.popen(f'vboxmanage controlvm "{uid}" poweroff')
        case "reboot":
            proc = os.popen(f'vboxmanage controlvm "{uid}" poweroff')      
            proc = os.popen(f'vboxmanage startvm "{uid}" --type headless')
        case "pause":
            proc = os.popen(f'vboxmanage controlvm "{uid}" pause')
        case "resume":
            proc = os.popen(f'vboxmanage controlvm "{uid}" resume')
        case _:
            return {'actions':['start','stop','reboot','pause','resume']}
    return {'status':'ok'}

