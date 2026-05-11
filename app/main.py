from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

# Crea las tablas en Supabase (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependencia para obtener la DB en cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#------------------ Auth y Registro ------------------------#

@app.post("/auth/registro/iniciar", response_model=schemas.RegistroIniciarResponse)
def iniciar_registro(request: schemas.RegistroIniciarRequest, db: Session = Depends(get_db)):
    return crud.iniciar_registro(db=db, request=request)

@app.post("/auth/registro/verificar/{mail}", response_model=schemas.RegistroVerificarResponse)
def verificar_registro(mail: str, verificador: int, db: Session = Depends(get_db)):
    return crud.verificar_registro(db=db, mail=mail, verificador=verificador)


@app.get("/auth/registro/estado", response_model=schemas.RegistroEstadoResponse)
def estado_registro(mail: str, db: Session = Depends(get_db)):
    return crud.estado_registro(db=db, mail=mail)
#------------------ Medios de pago -------------------------#

#------------------ Home y Catalogo ------------------------#

#------------------ Sala de Subastas -----------------------#

#------------------ Compras --------------------------------#

#------------------ Personas -------------------------------#

#------------------ Ventas ---------------------------------#

#------------------ Informacion Necesaria ------------------#

@app.post("/paises/", response_model=schemas.Pais)
def create_pais(pais: schemas.PaisCreate, db: Session = Depends(get_db)):
    return crud.create_pais(db=db, pais=pais)

@app.get("/paises/", response_model=list[schemas.Pais])
def read_paises(db: Session = Depends(get_db)):
    paises = crud.get_paises(db)
    return paises

@app.get("/paises/{numero}", response_model=schemas.Pais)
def read_pais(numero: int, db: Session = Depends(get_db)):
    return crud.get_pais(db, numero=numero)

@app.delete("/paises/{numero}")
def delete_pais(numero: int, db: Session = Depends(get_db)):
    return crud.delete_pais(db, numero=numero)