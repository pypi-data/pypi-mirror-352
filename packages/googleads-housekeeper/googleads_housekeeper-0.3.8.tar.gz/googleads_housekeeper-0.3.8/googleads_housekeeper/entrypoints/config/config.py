from __future__ import annotations

from fastapi import APIRouter, Body

from googleads_housekeeper import views
from googleads_housekeeper.domain import commands
from googleads_housekeeper.entrypoints.bus import bus

router = APIRouter(prefix='/settings')


@router.get('/')
def list_config() -> list[dict]:
  return views.config(bus.uow)


@router.post('/')
def create_config(data: dict = Body(embed=True)):
  return bus.handle(commands.SaveConfig(**data))
