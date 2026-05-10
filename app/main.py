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
def read_paises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    paises = crud.get_paises(db, skip=skip, limit=limit)
    return paises

@app.get("/paises/{numero}", response_model=schemas.Pais)
def read_pais(numero: int, db: Session = Depends(get_db)):
    db_pais = crud.get_pais(db, numero=numero)
    if db_pais is None:
        raise HTTPException(status_code=404, detail="País no encontrado")
    return db_pais

@app.delete("/paises/{numero}")
def delete_pais(numero: int, db: Session = Depends(get_db)):
    db_pais = crud.delete_pais(db, numero=numero)
    if db_pais is None:
        raise HTTPException(status_code=404, detail="País no encontrado")
    return {"message": f"País {numero} eliminado con éxito"}