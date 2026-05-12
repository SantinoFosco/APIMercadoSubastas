from http.client import HTTPException

from sqlalchemy.orm import Session
from . import models, schemas

#------------------ Auth y Registro ------------------------#

def iniciar_registro(db: Session, request: schemas.RegistroIniciarRequest):
    usuario_existente = db.query(models.Persona).filter(models.Persona.documento == request.documento).first()
    if usuario_existente:
        return schemas.RegistroIniciarResponse(
            mensaje="El documento ya está registrado",
            usuario_id=usuario_existente.identificador
        )

    try:
        nueva_persona = models.Persona(
            nombre=request.nombre,
            documento=request.documento,
            direccion=request.direccion,
            estado="inactivo"
        )
        db.add(nueva_persona)
        
        db.flush() 

        nuevo_detalle = models.PersonaDetalle(
            persona=nueva_persona.identificador,
            pais=request.id_pais,
            mail=request.mail,
            contrasenia="PENDIENTE"
        )
        db.add(nuevo_detalle)

        db.commit()
        db.refresh(nueva_persona)

        return schemas.RegistroIniciarResponse(
            mensaje="Registro iniciado exitosamente",
            usuario_id=nueva_persona.identificador
        )

    except Exception as e:
        db.rollback()
        raise e
    
def verificar_registro(db: Session, mail: str):
    persona = db.query(models.PersonaDetalle).filter(models.PersonaDetalle.mail == mail).first()

    if not persona:
        return schemas.RegistroVerificarResponse(mensaje="Correo no registrado")

    else:

        categorias = ["comun", "especial", "plata", "oro", "platino"]

        nuevo_cliente = models.Cliente(
            numeroPais=persona.pais,
            admitido="si",
            categoria=random.choice(categorias)
        )

        db.add(nuevo_cliente)
        db.commit()

        return schemas.RegistroVerificarResponse(mensaje="Registro verificado exitosamente")

def estado_registro(db: Session, mail: str):
    detalle = db.query(models.PersonaDetalle).filter(models.PersonaDetalle.mail == mail).first()
    if not detalle:
        return schemas.RegistroEstadoResponse(
            verificado=False,
            categoria="",
            mensaje="Correo no registrado"
        )
    
    persona = db.query(models.Persona).filter(models.Persona.identificador == detalle.persona).first()
    if not persona:
        return schemas.RegistroEstadoResponse(
            verificado=False,
            categoria="",
            mensaje="Usuario no encontrado"
        )
    
    if persona.estado == "inactivo":
        return schemas.RegistroEstadoResponse(
            verificado=False,
            categoria="",
            mensaje="Registro en proceso de verificación"
        )
    
    return schemas.RegistroEstadoResponse(
        verificado=True,
        categoria=persona.categoria,
        mensaje="Usuario verificado y activo"
    )

#------------------ Medios de pago -------------------------#

def get_medios_pago_cliente(db: Session, cliente_id: int):
    return db.query(models.MedioPago).filter(
        models.MedioPago.cliente == cliente_id
    ).all()

def delete_medio_pago(db: Session, medio_pago_id: int):
    db_medio = db.query(models.MedioPago).filter(
        models.MedioPago.identificador == medio_pago_id
    ).first()
    if db_medio:
        db.delete(db_medio)
        db.commit()
    return db_medio

def create_cuenta_bancaria(db: Session, request: schemas.CuentaBancariaCreate):
    try:
        nuevo_medio = models.MedioPago(
            cliente=request.cliente,
            tipo="cuenta_bancaria",
            estado="pendiente",
            moneda=request.moneda,
            es_internacional=request.es_internacional,
            descripcion=request.descripcion
        )
        db.add(nuevo_medio)
        db.flush()

        nueva_cuenta = models.mpCuentaBancaria(
            medio_pago=nuevo_medio.identificador,
            titular=request.titular,
            banco=request.banco,
            cbu=request.cbu,
            alias=request.alias,
            pais_banco=request.pais_banco
        )
        db.add(nueva_cuenta)
        db.commit()
        db.refresh(nuevo_medio)
        db.refresh(nueva_cuenta)

        return schemas.CuentaBancariaResponse(
            identificador=nuevo_medio.identificador,
            cliente=nuevo_medio.cliente,
            tipo=nuevo_medio.tipo,
            estado=nuevo_medio.estado,
            moneda=nuevo_medio.moneda,
            es_internacional=nuevo_medio.es_internacional,
            descripcion=nuevo_medio.descripcion,
            titular=nueva_cuenta.titular,
            banco=nueva_cuenta.banco,
            cbu=nueva_cuenta.cbu,
            alias=nueva_cuenta.alias,
            pais_banco=nueva_cuenta.pais_banco
        )
    except Exception as e:
        db.rollback()
        raise e

def get_cuenta_bancaria(db: Session, medio_pago_id: int):
    medio = db.query(models.MedioPago).filter(
        models.MedioPago.identificador == medio_pago_id
    ).first()
    cuenta = db.query(models.mpCuentaBancaria).filter(
        models.mpCuentaBancaria.medio_pago == medio_pago_id
    ).first()
    if not medio or not cuenta:
        return None
    return schemas.CuentaBancariaResponse(
        identificador=medio.identificador,
        cliente=medio.cliente,
        tipo=medio.tipo,
        estado=medio.estado,
        moneda=medio.moneda,
        es_internacional=medio.es_internacional,
        descripcion=medio.descripcion,
        titular=cuenta.titular,
        banco=cuenta.banco,
        cbu=cuenta.cbu,
        alias=cuenta.alias,
        pais_banco=cuenta.pais_banco
    )

def create_tarjeta(db: Session, request: schemas.TarjetaCreate):
    try:
        nuevo_medio = models.MedioPago(
            cliente=request.cliente,
            tipo="tarjeta",
            estado="pendiente",
            moneda=request.moneda,
            es_internacional=request.es_internacional,
            descripcion=request.descripcion
        )
        db.add(nuevo_medio)
        db.flush()

        nueva_tarjeta = models.mpTarjeta(
            medio_pago=nuevo_medio.identificador,
            titular=request.titular,
            ultimos_4_digitos=request.ultimos_4_digitos,
            vencimiento=request.vencimiento,
            marca=request.marca,
            tipo_tarjeta=request.tipo_tarjeta
        )
        db.add(nueva_tarjeta)
        db.commit()
        db.refresh(nuevo_medio)
        db.refresh(nueva_tarjeta)

        return schemas.TarjetaResponse(
            identificador=nuevo_medio.identificador,
            cliente=nuevo_medio.cliente,
            tipo=nuevo_medio.tipo,
            estado=nuevo_medio.estado,
            moneda=nuevo_medio.moneda,
            es_internacional=nuevo_medio.es_internacional,
            descripcion=nuevo_medio.descripcion,
            titular=nueva_tarjeta.titular,
            ultimos_4_digitos=nueva_tarjeta.ultimos_4_digitos,
            vencimiento=nueva_tarjeta.vencimiento,
            marca=nueva_tarjeta.marca,
            tipo_tarjeta=nueva_tarjeta.tipo_tarjeta
        )
    except Exception as e:
        db.rollback()
        raise e

def get_tarjeta(db: Session, medio_pago_id: int):
    medio = db.query(models.MedioPago).filter(
        models.MedioPago.identificador == medio_pago_id
    ).first()
    tarjeta = db.query(models.mpTarjeta).filter(
        models.mpTarjeta.medio_pago == medio_pago_id
    ).first()
    if not medio or not tarjeta:
        return None
    return schemas.TarjetaResponse(
        identificador=medio.identificador,
        cliente=medio.cliente,
        tipo=medio.tipo,
        estado=medio.estado,
        moneda=medio.moneda,
        es_internacional=medio.es_internacional,
        descripcion=medio.descripcion,
        titular=tarjeta.titular,
        ultimos_4_digitos=tarjeta.ultimos_4_digitos,
        vencimiento=tarjeta.vencimiento,
        marca=tarjeta.marca,
        tipo_tarjeta=tarjeta.tipo_tarjeta
    )

def create_cheque_certificado(db: Session, request: schemas.ChequeCertificadoCreate):
    try:
        nuevo_medio = models.MedioPago(
            cliente=request.cliente,
            tipo="cheque_certificado",
            estado="pendiente",
            moneda=request.moneda,
            es_internacional=request.es_internacional,
            descripcion=request.descripcion
        )
        db.add(nuevo_medio)
        db.flush()

        nuevo_cheque = models.mpChequeCertificado(
            medio_pago=nuevo_medio.identificador,
            banco=request.banco,
            numero_cheque=request.numero_cheque,
            monto=request.monto,
            monto_disponible=request.monto_disponible,
            observaciones=request.observaciones
        )
        db.add(nuevo_cheque)
        db.commit()
        db.refresh(nuevo_medio)
        db.refresh(nuevo_cheque)

        return schemas.ChequeCertificadoResponse(
            identificador=nuevo_medio.identificador,
            cliente=nuevo_medio.cliente,
            tipo=nuevo_medio.tipo,
            estado=nuevo_medio.estado,
            moneda=nuevo_medio.moneda,
            es_internacional=nuevo_medio.es_internacional,
            descripcion=nuevo_medio.descripcion,
            banco=nuevo_cheque.banco,
            numero_cheque=nuevo_cheque.numero_cheque,
            monto=nuevo_cheque.monto,
            monto_disponible=nuevo_cheque.monto_disponible,
            observaciones=nuevo_cheque.observaciones
        )
    except Exception as e:
        db.rollback()
        raise e

def get_cheque_certificado(db: Session, medio_pago_id: int):
    medio = db.query(models.MedioPago).filter(
        models.MedioPago.identificador == medio_pago_id
    ).first()
    cheque = db.query(models.mpChequeCertificado).filter(
        models.mpChequeCertificado.medio_pago == medio_pago_id
    ).first()
    if not medio or not cheque:
        return None
    return schemas.ChequeCertificadoResponse(
        identificador=medio.identificador,
        cliente=medio.cliente,
        tipo=medio.tipo,
        estado=medio.estado,
        moneda=medio.moneda,
        es_internacional=medio.es_internacional,
        descripcion=medio.descripcion,
        banco=cheque.banco,
        numero_cheque=cheque.numero_cheque,
        monto=cheque.monto,
        monto_disponible=cheque.monto_disponible,
        observaciones=cheque.observaciones
    )

#------------------ Home y Catalogo ------------------------#

#------------------ Sala de Subastas -----------------------#

#------------------ Compras --------------------------------#

#------------------ Personas -------------------------------#



#------------------ Ventas ---------------------------------#

#------------------ Informacion Necesaria ------------------#

# Obtener todos los países
def get_paises(db: Session):
    return db.query(models.Pais).all()

# Obtener un país por su número (ID)
def get_pais(db: Session, numero: int):
    return db.query(models.Pais).filter(models.Pais.numero == numero).first()

# Crear un nuevo país
def create_pais(db: Session, pais: schemas.PaisCreate):
    db_pais = models.Pais(**pais.model_dump())
    db.add(db_pais)
    db.commit()
    db.refresh(db_pais)
    return db_pais

# Eliminar un país
def delete_pais(db: Session, numero: int):
    db_pais = db.query(models.Pais).filter(models.Pais.numero == numero).first()
    
    db.delete(db_pais)
    db.commit()

    return db_pais