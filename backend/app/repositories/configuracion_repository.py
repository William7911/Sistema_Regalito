from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from app.db.models import ParametroSistema

class ConfiguracionRepositoryImpl:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def obtener_todos(self) -> Dict[str, str]:
        result = await self.db.execute(select(ParametroSistema))
        parametros = result.scalars().all()
        return {p.clave: p.valor for p in parametros}

    async def actualizar_valor(self, clave: str, valor: str) -> None:
        result = await self.db.execute(
            select(ParametroSistema).where(ParametroSistema.clave == clave)
        )
        parametro = result.scalar_one_or_none()
        
        if parametro:
            parametro.valor = valor
        else:
            nuevo_parametro = ParametroSistema(clave=clave, valor=valor)
            self.db.add(nuevo_parametro)
