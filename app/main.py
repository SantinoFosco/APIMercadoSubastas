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

@app.get("/medios-pago/cliente/{cliente_id}", response_model=list[schemas.MedioPagoResponse])
def get_medios_pago_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return crud.get_medios_pago_cliente(db=db, cliente_id=cliente_id)

@app.delete("/medios-pago/{medio_pago_id}")
def delete_medio_pago(medio_pago_id: int, db: Session = Depends(get_db)):
    db_medio = crud.delete_medio_pago(db=db, medio_pago_id=medio_pago_id)
    if db_medio is None:
        raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
    return {"message": f"Medio de pago {medio_pago_id} eliminado con éxito"}

@app.post("/medios-pago/cuenta-bancaria/", response_model=schemas.CuentaBancariaResponse)
def create_cuenta_bancaria(request: schemas.CuentaBancariaCreate, db: Session = Depends(get_db)):
    return crud.create_cuenta_bancaria(db=db, request=request)

@app.get("/medios-pago/cuenta-bancaria/{medio_pago_id}", response_model=schemas.CuentaBancariaResponse)
def get_cuenta_bancaria(medio_pago_id: int, db: Session = Depends(get_db)):
    result = crud.get_cuenta_bancaria(db=db, medio_pago_id=medio_pago_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
    return result

@app.post("/medios-pago/tarjeta/", response_model=schemas.TarjetaResponse)
def create_tarjeta(request: schemas.TarjetaCreate, db: Session = Depends(get_db)):
    return crud.create_tarjeta(db=db, request=request)

@app.get("/medios-pago/tarjeta/{medio_pago_id}", response_model=schemas.TarjetaResponse)
def get_tarjeta(medio_pago_id: int, db: Session = Depends(get_db)):
    result = crud.get_tarjeta(db=db, medio_pago_id=medio_pago_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    return result

@app.post("/medios-pago/cheque/", response_model=schemas.ChequeCertificadoResponse)
def create_cheque_certificado(request: schemas.ChequeCertificadoCreate, db: Session = Depends(get_db)):
    return crud.create_cheque_certificado(db=db, request=request)

@app.get("/medios-pago/cheque/{medio_pago_id}", response_model=schemas.ChequeCertificadoResponse)
def get_cheque_certificado(medio_pago_id: int, db: Session = Depends(get_db)):
    result = crud.get_cheque_certificado(db=db, medio_pago_id=medio_pago_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cheque certificado no encontrado")
    return result

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