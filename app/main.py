from fastapi import FastAPI, Depends, HTTPException, Query
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

@app.get("/")
def hello_world():
    return {"message": "¡Bienvenido a la API del Mercado de Ari!"}

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

@app.get("/mediosPago", response_model=schemas.MedioPagoListResponse)
def get_medios_pago_cliente(cliente_id: int = Query(...), db: Session = Depends(get_db)):
    return crud.get_medios_pago_cliente(db=db, cliente_id=cliente_id)

@app.post("/mediosPago/cuenta-bancaria", response_model=schemas.CuentaBancariaResponse)
def create_cuenta_bancaria(request: schemas.CuentaBancariaCreate, db: Session = Depends(get_db)):
    return crud.create_cuenta_bancaria(db=db, request=request)

@app.get("/mediosPago/cuenta-bancaria/{medio_pago_id}", response_model=schemas.CuentaBancariaResponse)
def get_cuenta_bancaria(medio_pago_id: int, db: Session = Depends(get_db)):
    result = crud.get_cuenta_bancaria(db=db, medio_pago_id=medio_pago_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cuenta bancaria no encontrada")
    return result

@app.post("/mediosPago/tarjeta", response_model=schemas.TarjetaResponse)
def create_tarjeta(request: schemas.TarjetaCreate, db: Session = Depends(get_db)):
    return crud.create_tarjeta(db=db, request=request)

@app.get("/mediosPago/tarjeta/{medio_pago_id}", response_model=schemas.TarjetaResponse)
def get_tarjeta(medio_pago_id: int, db: Session = Depends(get_db)):
    result = crud.get_tarjeta(db=db, medio_pago_id=medio_pago_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    return result

@app.post("/mediosPago/cheque", response_model=schemas.ChequeCertificadoResponse)
def create_cheque_certificado(request: schemas.ChequeCertificadoCreate, db: Session = Depends(get_db)):
    return crud.create_cheque_certificado(db=db, request=request)

@app.get("/mediosPago/cheque/{medio_pago_id}", response_model=schemas.ChequeCertificadoResponse)
def get_cheque_certificado(medio_pago_id: int, db: Session = Depends(get_db)):
    result = crud.get_cheque_certificado(db=db, medio_pago_id=medio_pago_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cheque certificado no encontrado")
    return result

@app.get("/mediosPago/{medio_pago_id}", response_model=schemas.MedioPagoItem)
def get_medio_pago(medio_pago_id: int, db: Session = Depends(get_db)):
    result = crud.get_medio_pago_detalle(db=db, medio_pago_id=medio_pago_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
    return result

@app.put("/mediosPago/{medio_pago_id}", response_model=schemas.MedioPagoItem)
def update_medio_pago(medio_pago_id: int, request: schemas.DescripcionUpdate, db: Session = Depends(get_db)):
    result = crud.update_medio_pago_descripcion(db=db, medio_pago_id=medio_pago_id, descripcion=request.descripcion)
    if result is None:
        raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
    return result

@app.delete("/mediosPago/{medio_pago_id}")
def delete_medio_pago(medio_pago_id: int, db: Session = Depends(get_db)):
    db_medio = crud.delete_medio_pago(db=db, medio_pago_id=medio_pago_id)
    if db_medio is None:
        raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
    return {"message": f"Medio de pago {medio_pago_id} eliminado con éxito"}

#------------------ Home y Catalogo ------------------------#

#------------------ Sala de Subastas -----------------------#

#------------------ Compras --------------------------------#

#------------------ Personas -------------------------------#

@app.get("/sectores/", response_model=list[schemas.SectorResponse])
def get_sectores(db: Session = Depends(get_db)):
    return crud.get_sectores(db=db)

@app.post("/sectores/", response_model=schemas.SectorResponse)
def create_sector(request: schemas.SectorCreate, db: Session = Depends(get_db)):
    return crud.create_sector(db=db, request=request)

@app.get("/sectores/{sector_id}", response_model=schemas.SectorResponse)
def get_sector(sector_id: int, db: Session = Depends(get_db)):
    result = crud.get_sector(db=db, sector_id=sector_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sector no encontrado")
    return result

@app.delete("/sectores/{sector_id}")
def delete_sector(sector_id: int, db: Session = Depends(get_db)):
    result = crud.delete_sector(db=db, sector_id=sector_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sector no encontrado")
    return {"message": f"Sector {sector_id} eliminado con éxito"}

@app.get("/empleados/", response_model=list[schemas.EmpleadoResponse])
def get_empleados(db: Session = Depends(get_db)):
    return crud.get_empleados(db=db)

@app.post("/empleados/", response_model=schemas.EmpleadoResponse)
def create_empleado(request: schemas.EmpleadoCreate, db: Session = Depends(get_db)):
    return crud.create_empleado(db=db, request=request)

@app.get("/empleados/{empleado_id}", response_model=schemas.EmpleadoResponse)
def get_empleado(empleado_id: int, db: Session = Depends(get_db)):
    result = crud.get_empleado(db=db, empleado_id=empleado_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return result

@app.delete("/empleados/{empleado_id}")
def delete_empleado(empleado_id: int, db: Session = Depends(get_db)):
    result = crud.delete_empleado(db=db, empleado_id=empleado_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return {"message": f"Empleado {empleado_id} eliminado con éxito"}

@app.get("/clientes/", response_model=list[schemas.ClienteResponse])
def get_clientes(db: Session = Depends(get_db)):
    return crud.get_clientes(db=db)

@app.post("/clientes/", response_model=schemas.ClienteResponse)
def create_cliente(request: schemas.ClienteCreate, db: Session = Depends(get_db)):
    return crud.create_cliente(db=db, request=request)

@app.get("/clientes/{cliente_id}", response_model=schemas.ClienteResponse)
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    result = crud.get_cliente(db=db, cliente_id=cliente_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return result

@app.delete("/clientes/{cliente_id}")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    result = crud.delete_cliente(db=db, cliente_id=cliente_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"message": f"Cliente {cliente_id} eliminado con éxito"}

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
    pais = crud.get_pais(db, numero=numero)
    if not pais:
        raise HTTPException(status_code=404, detail="País no encontrado")
    return pais

@app.delete("/paises/{numero}")
def delete_pais(numero: int, db: Session = Depends(get_db)):
    pais = crud.delete_pais(db, numero=numero)
    if not pais:
        raise HTTPException(status_code=404, detail="País no encontrado")
    return pais