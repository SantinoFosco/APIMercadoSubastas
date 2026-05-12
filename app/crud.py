from http.client import HTTPException

from sqlalchemy.orm import Session
from . import models, schemas

#------------------ Auth y Registro ------------------------#

def iniciar_registro(db: Session, request: schemas.RegistroIniciarRequest):
    usuario_existente = db.query(models.Persona).filter(models.Persona.documento == request.documento).first()
    if usuario_existente:
        return schemas.RegistroIniciarResponse(
            mensaje="El documento ya está registrado",
            personaId=usuario_existente.identificador
        )

    try:
        nueva_persona = models.Persona(
            nombre=f"{request.nombre} {request.apellido}",
            documento=request.documento,
            direccion=request.direccion,
            estado="inactivo"
        )
        db.add(nueva_persona)

        db.flush()

        nuevo_detalle = models.PersonaDetalle(
            persona=nueva_persona.identificador,
            pais=request.pais,
            mail=request.mail,
            contrasenia="PENDIENTE"
        )
        db.add(nuevo_detalle)

        db.commit()
        db.refresh(nueva_persona)

        return schemas.RegistroIniciarResponse(
            mensaje="Registro iniciado exitosamente",
            personaId=nueva_persona.identificador
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

def _build_medio_pago_item(medio: models.MedioPago, db) -> schemas.MedioPagoItem:
    monto = None
    monto_disp = None
    if medio.tipo == "cheque_certificado":
        cheque = db.query(models.mpChequeCertificado).filter(
            models.mpChequeCertificado.medio_pago == medio.identificador
        ).first()
        if cheque:
            monto = cheque.monto
            monto_disp = cheque.monto_disponible
    return schemas.MedioPagoItem(
        id=medio.identificador,
        tipo=medio.tipo,
        estado=medio.estado,
        descripcion=medio.descripcion,
        moneda=medio.moneda,
        esInternacional=medio.es_internacional == "si",
        montoCheque=monto,
        montoDisponibleCheque=monto_disp
    )

def get_medios_pago_cliente(db: Session, cliente_id: int) -> schemas.MedioPagoListResponse:
    medios = db.query(models.MedioPago).filter(
        models.MedioPago.cliente == cliente_id
    ).all()
    items = [_build_medio_pago_item(m, db) for m in medios]
    return schemas.MedioPagoListResponse(
        tieneMedioPagoVerificado=any(i.estado == "verificado" for i in items),
        medios=items
    )

def get_medio_pago_detalle(db: Session, medio_pago_id: int):
    medio = db.query(models.MedioPago).filter(
        models.MedioPago.identificador == medio_pago_id
    ).first()
    if not medio:
        return None
    return _build_medio_pago_item(medio, db)

def update_medio_pago_descripcion(db: Session, medio_pago_id: int, descripcion: str):
    medio = db.query(models.MedioPago).filter(
        models.MedioPago.identificador == medio_pago_id
    ).first()
    if not medio:
        return None
    medio.descripcion = descripcion
    db.commit()
    db.refresh(medio)
    return _build_medio_pago_item(medio, db)

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
            es_internacional="no",
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
            pais_banco=request.paisBanco
        )
        db.add(nueva_cuenta)
        db.commit()
        db.refresh(nuevo_medio)
        db.refresh(nueva_cuenta)

        return schemas.CuentaBancariaResponse(
            id=nuevo_medio.identificador,
            tipo=nuevo_medio.tipo,
            estado=nuevo_medio.estado,
            descripcion=nuevo_medio.descripcion,
            moneda=nuevo_medio.moneda,
            esInternacional=False,
            titular=nueva_cuenta.titular,
            banco=nueva_cuenta.banco,
            cbu=nueva_cuenta.cbu,
            alias=nueva_cuenta.alias,
            paisBanco=nueva_cuenta.pais_banco
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
        id=medio.identificador,
        tipo=medio.tipo,
        estado=medio.estado,
        descripcion=medio.descripcion,
        moneda=medio.moneda,
        esInternacional=medio.es_internacional == "si",
        titular=cuenta.titular,
        banco=cuenta.banco,
        cbu=cuenta.cbu,
        alias=cuenta.alias,
        paisBanco=cuenta.pais_banco
    )

def create_tarjeta(db: Session, request: schemas.TarjetaCreate):
    try:
        nuevo_medio = models.MedioPago(
            cliente=request.cliente,
            tipo="tarjeta",
            estado="pendiente",
            moneda=request.moneda,
            es_internacional="si" if request.esInternacional else "no",
            descripcion=request.descripcion
        )
        db.add(nuevo_medio)
        db.flush()

        nueva_tarjeta = models.mpTarjeta(
            medio_pago=nuevo_medio.identificador,
            titular=request.titular,
            ultimos_4_digitos=request.ultimos4Digitos,
            vencimiento=request.vencimiento,
            marca=request.marca,
            tipo_tarjeta=request.tipoTarjeta
        )
        db.add(nueva_tarjeta)
        db.commit()
        db.refresh(nuevo_medio)
        db.refresh(nueva_tarjeta)

        return schemas.TarjetaResponse(
            id=nuevo_medio.identificador,
            tipo=nuevo_medio.tipo,
            estado=nuevo_medio.estado,
            descripcion=nuevo_medio.descripcion,
            moneda=nuevo_medio.moneda,
            esInternacional=request.esInternacional,
            titular=nueva_tarjeta.titular,
            ultimos4Digitos=nueva_tarjeta.ultimos_4_digitos,
            vencimiento=nueva_tarjeta.vencimiento,
            marca=nueva_tarjeta.marca,
            tipoTarjeta=nueva_tarjeta.tipo_tarjeta
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
        id=medio.identificador,
        tipo=medio.tipo,
        estado=medio.estado,
        descripcion=medio.descripcion,
        moneda=medio.moneda,
        esInternacional=medio.es_internacional == "si",
        titular=tarjeta.titular,
        ultimos4Digitos=tarjeta.ultimos_4_digitos,
        vencimiento=tarjeta.vencimiento,
        marca=tarjeta.marca,
        tipoTarjeta=tarjeta.tipo_tarjeta
    )

def create_cheque_certificado(db: Session, request: schemas.ChequeCertificadoCreate):
    try:
        nuevo_medio = models.MedioPago(
            cliente=request.cliente,
            tipo="cheque_certificado",
            estado="pendiente",
            moneda=request.moneda,
            es_internacional="no",
            descripcion=request.descripcion
        )
        db.add(nuevo_medio)
        db.flush()

        nuevo_cheque = models.mpChequeCertificado(
            medio_pago=nuevo_medio.identificador,
            banco=request.banco,
            numero_cheque=request.numeroCheque,
            monto=request.monto,
            monto_disponible=request.monto,
            observaciones=request.observaciones
        )
        db.add(nuevo_cheque)
        db.commit()
        db.refresh(nuevo_medio)
        db.refresh(nuevo_cheque)

        return schemas.ChequeCertificadoResponse(
            id=nuevo_medio.identificador,
            tipo=nuevo_medio.tipo,
            estado=nuevo_medio.estado,
            descripcion=nuevo_medio.descripcion,
            moneda=nuevo_medio.moneda,
            esInternacional=False,
            montoCheque=nuevo_cheque.monto,
            montoDisponibleCheque=nuevo_cheque.monto_disponible,
            banco=nuevo_cheque.banco,
            numeroCheque=nuevo_cheque.numero_cheque,
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
        id=medio.identificador,
        tipo=medio.tipo,
        estado=medio.estado,
        descripcion=medio.descripcion,
        moneda=medio.moneda,
        esInternacional=medio.es_internacional == "si",
        montoCheque=cheque.monto,
        montoDisponibleCheque=cheque.monto_disponible,
        banco=cheque.banco,
        numeroCheque=cheque.numero_cheque,
        observaciones=cheque.observaciones
    )

#------------------ Home y Catalogo ------------------------#

#------------------ Sala de Subastas -----------------------#

#------------------ Compras --------------------------------#

#------------------ Personas -------------------------------#

def create_sector(db: Session, request: schemas.SectorCreate):
    nuevo = models.Sector(
        nombreSector=request.nombreSector,
        codigoSector=request.codigoSector
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return schemas.SectorResponse(
        identificador=nuevo.indentificador,
        nombreSector=nuevo.nombreSector,
        codigoSector=nuevo.codigoSector
    )

def get_sectores(db: Session):
    sectores = db.query(models.Sector).all()
    return [schemas.SectorResponse(
        identificador=s.indentificador,
        nombreSector=s.nombreSector,
        codigoSector=s.codigoSector
    ) for s in sectores]

def get_sector(db: Session, sector_id: int):
    s = db.query(models.Sector).filter(models.Sector.indentificador == sector_id).first()
    if not s:
        return None
    return schemas.SectorResponse(
        identificador=s.indentificador,
        nombreSector=s.nombreSector,
        codigoSector=s.codigoSector
    )

def delete_sector(db: Session, sector_id: int):
    s = db.query(models.Sector).filter(models.Sector.indentificador == sector_id).first()
    if s:
        db.delete(s)
        db.commit()
    return s

def create_empleado(db: Session, request: schemas.EmpleadoCreate):
    nuevo = models.Empleado(cargo=request.cargo, sector=request.sector)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def get_empleados(db: Session):
    return db.query(models.Empleado).all()

def get_empleado(db: Session, empleado_id: int):
    return db.query(models.Empleado).filter(models.Empleado.identificador == empleado_id).first()

def delete_empleado(db: Session, empleado_id: int):
    e = db.query(models.Empleado).filter(models.Empleado.identificador == empleado_id).first()
    if e:
        db.delete(e)
        db.commit()
    return e

def create_cliente(db: Session, request: schemas.ClienteCreate):
    nuevo = models.Cliente(
        identificador=request.identificador,
        numeroPais=request.numeroPais,
        admitido="no",
        categoria="comun",
        verificador=request.verificador
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def get_clientes(db: Session):
    return db.query(models.Cliente).all()

def get_cliente(db: Session, cliente_id: int):
    return db.query(models.Cliente).filter(models.Cliente.identificador == cliente_id).first()

def delete_cliente(db: Session, cliente_id: int):
    c = db.query(models.Cliente).filter(models.Cliente.identificador == cliente_id).first()
    if c:
        db.delete(c)
        db.commit()
    return c



#------------------ Ventas ---------------------------------#

#------------------ Informacion Necesaria ------------------#

# Obtener todos los países
def get_paises(db: Session):
    return db.query(models.Pais).all()

# Obtener un país por su número (ID)
def get_pais(db: Session, numero: int):
    db_pais = db.query(models.Pais).filter(models.Pais.numero == numero).first()

    if not db_pais:
        raise HTTPException(status_code=404, detail="País no encontrado")
    
    return db_pais

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
    
    if not db_pais:
        raise HTTPException(status_code=404, detail="País no encontrado")

    db.delete(db_pais)
    db.commit()

    return db_pais