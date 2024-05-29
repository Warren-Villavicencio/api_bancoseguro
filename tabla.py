from sqlalchemy import String, Integer, Column, Float

from base_de_datos import Base

class Ingreso(Base):
    __tablename__ = "cuentabancaria"
    id = Column(Integer, primary_key=True, autoincrement=True)
    numerodecuenta = Column(String(20))
    
    titular = Column(String(100))
    tarjeta_de_debito = Column(String(16))
    clavetarjeta = Column(String(4))
    correoelectronico = Column(String(100))
    claveanterior = Column(String(20))
    clavenueva = Column(String(20))
    saldo = Column(Float)


