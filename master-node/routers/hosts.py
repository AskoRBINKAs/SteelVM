from fastapi import Depends, HTTPException, APIRouter
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from models import HostMachine
from schemas import HostCreateModel, HostRegisterModel
from uuid import uuid4
from utils import get_current_user, get_current_host
import aiohttp

router = APIRouter(
    tags=['Hosts']
)

@router.get('/api/hosts')
async def get_hosts(db:AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    hosts = await db.execute(Select(HostMachine))
    return hosts.scalars().all()

@router.post('/api/hosts')
async def create_new_host(host:HostCreateModel, db:AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    new_machine = HostMachine(name=host.name)
    new_machine.access_key = str(uuid4())
    db.add(new_machine)
    await db.commit()
    await db.refresh(new_machine)
    return new_machine

@router.post('/api/hosts/{token}/')
async def register_host(token:str, host_details:HostRegisterModel, db:AsyncSession = Depends(get_db),host = Depends(get_current_host)):
    host = await db.execute(Select(HostMachine).where(HostMachine.access_key==token))
    host:HostMachine = host.scalar_one_or_none()
    if host is None:
        return HTTPException(
            status_code=404,
            detail='Host not found'
        )
    if host.activated:
        return host
    host.cpu_count = host_details.cpu_count
    host.ram_count = host_details.ram_count
    host.host_os = host_details.host_os
    host.ip_address = host_details.ip_address
    host.online = True
    host.activated = True
    host.port = host_details.port
    host.vm_type = host_details.vm_type
    await db.commit()
    return host

# return list of vm's on host
@router.get('/api/hosts/{id}/info')
async def get_host_information(id:int, db:AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    host = await db.execute(Select(HostMachine).where(HostMachine.id == id))
    host = host.scalar_one_or_none()
    if host is None:
        raise HTTPException(
            status_code=404,
            detail='Host not found'
        )
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{host.ip_address}:{host.port}/vms/") as response:
            return await response.json()

# send request to start/stop/restart vm
@router.get('/api/hosts/{id}/vm/{vm_id}/')
async def interact_with_vm(id:int,vm_id:str,action:str = 'none', db:AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    print(id,vm_id)
    host = await db.execute(Select(HostMachine).where(HostMachine.id == id))
    host = host.scalar_one_or_none()
    if host is None:
        raise HTTPException(
            status_code=404,
            detail='Host not found'
        )
    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://{host.ip_address}:{host.port}/vms/{vm_id}/?action={action}") as response:
            return await response.json()

@router.delete('/api/hosts/{id}/delete')
async def delete_vm(id:int, db:AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    host = await db.execute(Select(HostMachine).where(HostMachine.id == id))
    host = host.scalar_one_or_none()
    if host is None:
        raise HTTPException(
            status_code=404,
            detail='Host not found'
        )
    await db.delete(host)
    await db.commit()
    await db.flush()
    return {'status':'ok'}