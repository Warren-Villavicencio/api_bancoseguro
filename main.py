from fastapi import FastAPI, HTTPException, Depends, status

from pydantic import BaseModel
from typing import Annotated
import tabla
from base_de_datos import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/")
def read_root():
    return {"Bienvenidos a Banco Seguro"}

class IngresoBase(BaseModel):
    
    numerodecuenta:str
    titular:str
    correoelectronico:str
    clavetarjeta:str
    saldo:float

class DepositoBase(BaseModel):
    numerodecuenta: str
    monto: float
    
class CambioClaveBase(BaseModel):
    numerodecuenta: str
    claveanterior: str
    clavenueva: str
    
class RetiroBase(BaseModel):
    numerodecuenta: str
    monto: float   

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/Registrar_Cuenta/", status_code=status.HTTP_201_CREATED)
async def crear_cuenta_bancaria(registro:IngresoBase, db:db_dependency):
    db_registro = tabla.Ingreso(**registro.dict())  
    db.add(db_registro)
    db.commit()
    return "El registro de la cuenta bancaria se realizo exitosamente"

@app.get("/Listar_Cuentas/", status_code=status.HTTP_200_OK)
async def consultar_registros(db:db_dependency):
    registros = db.query(tabla.Ingreso).all()
    return registros

@app.get("/consultarCuentas/", status_code=status.HTTP_200_OK)
async def consultar_registros_por_numero_de_cuenta(numero_de_cuenta_bancaria, db:db_dependency):
    registro = db.query(tabla.Ingreso).filter(tabla.Ingreso.numerodecuenta==numero_de_cuenta_bancaria).first()
    if registro is None:
        HTTPException(status_code=404, detail="cuenta no encontrado")
    return registro

@app.delete("/borrarCuenta/", status_code=status.HTTP_200_OK)
async def borrar_registro(id_registro, db:db_dependency):
    registroborrar = db.query(tabla.Ingreso).filter(tabla.Ingreso.id==id_registro).first()
    if registroborrar is None:
        HTTPException(status_code=404, detail="No se puede borrar no exite el registro")
    db.delete(registroborrar)
    db.commit()
    return "EL registro de elimino exitosamente"

@app.post("/cambiarclave/", status_code=status.HTTP_200_OK)
async def cambiar_clave(datos_cambio: CambioClaveBase, db: db_dependency):
    cuenta = db.query(tabla.Ingreso).filter(tabla.Ingreso.numerodecuenta == datos_cambio.numerodecuenta).first()
    if cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    if cuenta.clavetarjeta != datos_cambio.claveanterior:  
        raise HTTPException(status_code=400, detail="Clave anterior incorrecta")
    cuenta.clavetarjeta = datos_cambio.clavenueva  
    db.commit()
    return {"mensaje": "La clave de la tarjeta de débito ha sido cambiada exitosamente"}

@app.post("/depositar/", status_code=status.HTTP_200_OK)
async def depositar_dinero(deposito: DepositoBase, db: db_dependency):
    cuenta = db.query(tabla.Ingreso).filter(tabla.Ingreso.numerodecuenta == deposito.numerodecuenta).first()
    if cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    cuenta.saldo += deposito.monto
    db.commit()
    return {"mensaje": "Depósito realizado exitosamente", "saldo_actual": cuenta.saldo}


@app.post("/retirar/", status_code=status.HTTP_200_OK)
async def retirar_dinero(retiro: RetiroBase, db: db_dependency):
    cuenta = db.query(tabla.Ingreso).filter(tabla.Ingreso.numerodecuenta == retiro.numerodecuenta).first()
    if cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    if cuenta.saldo < retiro.monto:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")
    cuenta.saldo -= retiro.monto
    db.commit()
    return {"mensaje": "Retiro realizado exitosamente", "saldo_actual": cuenta.saldo}

 
 
