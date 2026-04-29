import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. Cargar variables
load_dotenv()
url = os.getenv("DATABASE_URL")

# 2. Configurar el motor de SQLAlchemy
engine = create_engine(url)

def probar_conexion():
    try:
        # Intentar conectar y ejecutar una consulta simple
        with engine.connect() as connection:
            # Ejecutamos un SELECT simple que no requiere tablas creadas
            resultado = connection.execute(text("SELECT strftime('%Y-%m-%d %H:%M:%S', 'now') as hora" if "sqlite" in url else "SELECT NOW();"))
            print("✅ ¡Conexión exitosa a Supabase!")
            print(f"Hora del servidor: {resultado.fetchone()[0]}")
            
    except Exception as e:
        print("❌ Error al conectar:")
        print(e)

if __name__ == "__main__":
    probar_conexion()