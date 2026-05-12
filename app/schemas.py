from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

#------------------ Auth y Registro ------------------------#

class RegistroIniciarResponse(BaseModel):
    mensaje: str
    personaId: int

class RegistroIniciarRequest(BaseModel):
    nombre: str
    apellido: str
    documento: str
    mail: str
    direccion: str
    pais: int

#------------------ Medios de pago -------------------------#

class MedioPagoItem(BaseModel):
    id: int
    tipo: str
    estado: str
    descripcion: Optional[str] = None
    moneda: str
    esInternacional: bool
    montoCheque: Optional[Decimal] = None
    montoDisponibleCheque: Optional[Decimal] = None

class MedioPagoListResponse(BaseModel):
    tieneMedioPagoVerificado: bool
    medios: list[MedioPagoItem]

class DescripcionUpdate(BaseModel):
    descripcion: str

class CuentaBancariaCreate(BaseModel):
    cliente: int
    moneda: str = "ARS"
    descripcion: Optional[str] = None
    titular: str
    banco: str
    cbu: str
    alias: Optional[str] = None
    paisBanco: int

class CuentaBancariaResponse(MedioPagoItem):
    titular: str
    banco: str
    cbu: str
    alias: Optional[str] = None
    paisBanco: int

class TarjetaCreate(BaseModel):
    cliente: int
    moneda: str = "ARS"
    descripcion: Optional[str] = None
    titular: str
    ultimos4Digitos: str
    vencimiento: date
    marca: str
    tipoTarjeta: str
    esInternacional: bool = False

class TarjetaResponse(MedioPagoItem):
    titular: str
    ultimos4Digitos: str
    vencimiento: date
    marca: str
    tipoTarjeta: str

class ChequeCertificadoCreate(BaseModel):
    cliente: int
    moneda: str = "ARS"
    descripcion: Optional[str] = None
    banco: str
    numeroCheque: str
    monto: Decimal
    observaciones: Optional[str] = None

class ChequeCertificadoResponse(MedioPagoItem):
    banco: str
    numeroCheque: str
    observaciones: Optional[str] = None

#------------------ Home y Catalogo ------------------------#

#------------------ Sala de Subastas -----------------------#

#------------------ Compras --------------------------------#

#------------------ Personas -------------------------------#

class SectorCreate(BaseModel):
    nombreSector: str
    codigoSector: Optional[str] = None

class SectorResponse(BaseModel):
    identificador: int
    nombreSector: str
    codigoSector: Optional[str] = None

    class Config:
        from_attributes = True

class EmpleadoCreate(BaseModel):
    cargo: Optional[str] = None
    sector: Optional[int] = None

class EmpleadoResponse(BaseModel):
    identificador: int
    cargo: Optional[str] = None
    sector: Optional[int] = None

    class Config:
        from_attributes = True

class ClienteCreate(BaseModel):
    identificador: int
    numeroPais: Optional[int] = None
    verificador: int

class ClienteResponse(BaseModel):
    identificador: int
    numeroPais: Optional[int] = None
    admitido: str
    categoria: str
    verificador: int

    class Config:
        from_attributes = True

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