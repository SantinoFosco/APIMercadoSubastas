from pydantic import BaseModel
from typing import Optional

#------------------ Auth y Registro ------------------------#

class RegistroIniciarResponse(BaseModel):
    mensaje: str
    usuario_id: int

class RegistroIniciarRequest(BaseModel):
    nombre: str
    documento: str
    mail: str
    direccion: str
    id_pais: int

#------------------ Medios de pago -------------------------#

#------------------ Home y Catalogo ------------------------#

#------------------ Sala de Subastas -----------------------#

#------------------ Compras --------------------------------#

#------------------ Personas -------------------------------#

#------------------ Ventas ---------------------------------#

#------------------ Informacion Necesaria ------------------#

# Esquema base con los campos comunes
class PaisBase(BaseModel):
    nombre: str
    nombreCorto: Optional[str] = None
    capital: str
    nacionalidad: str
    idiomas: str

# Esquema para crear (lo que el usuario envía)
class PaisCreate(PaisBase):
    pass

# Esquema para leer (lo que la API devuelve, incluye el ID)
class Pais(PaisBase):
    numero: int

    class Config:
        from_attributes = True # Permite leer modelos de SQLAlchemy