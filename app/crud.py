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

#------------------ Medios de pago -------------------------#

#------------------ Home y Catalogo ------------------------#

#------------------ Sala de Subastas -----------------------#

#------------------ Compras --------------------------------#

#------------------ Personas -------------------------------#



#------------------ Ventas ---------------------------------#

#------------------ Informacion Necesaria ------------------#

# Obtener todos los países
def get_paises(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Pais).offset(skip).limit(limit).all()

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
    if db_pais:
        db.delete(db_pais)
        db.commit()
    return db_pais