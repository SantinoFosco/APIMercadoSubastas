from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

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

class RegistroVerificarResponse(BaseModel):
    mensaje: str

class RegistroEstadoResponse(BaseModel):
    verificado: bool
    categoria: str
    mensaje: str

#------------------ Medios de pago -------------------------#

class MedioPagoResponse(BaseModel):
    identificador: int
    cliente: int
    tipo: str
    estado: str
    moneda: str
    es_internacional: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class CuentaBancariaCreate(BaseModel):
    cliente: int
    moneda: str = "ARS"
    es_internacional: str = "no"
    descripcion: Optional[str] = None
    titular: str
    banco: str
    cbu: str
    alias: Optional[str] = None
    pais_banco: int

class CuentaBancariaResponse(MedioPagoResponse):
    titular: str
    banco: str
    cbu: str
    alias: Optional[str] = None
    pais_banco: int

class TarjetaCreate(BaseModel):
    cliente: int
    moneda: str = "ARS"
    es_internacional: str = "no"
    descripcion: Optional[str] = None
    titular: str
    ultimos_4_digitos: str
    vencimiento: date
    marca: str
    tipo_tarjeta: str

class TarjetaResponse(MedioPagoResponse):
    titular: str
    ultimos_4_digitos: str
    vencimiento: date
    marca: str
    tipo_tarjeta: str

class ChequeCertificadoCreate(BaseModel):
    cliente: int
    moneda: str = "ARS"
    es_internacional: str = "no"
    descripcion: Optional[str] = None
    banco: str
    numero_cheque: str
    monto: Decimal
    monto_disponible: Decimal
    observaciones: Optional[str] = None

class ChequeCertificadoResponse(MedioPagoResponse):
    banco: str
    numero_cheque: str
    monto: Decimal
    monto_disponible: Decimal
    observaciones: Optional[str] = None

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
        from_attributes = True