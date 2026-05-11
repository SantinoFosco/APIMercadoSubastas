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