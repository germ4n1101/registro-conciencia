import streamlit as st
from sqlalchemy import create_engine, text
import psycopg2

# Credenciales Supabase
DB_HOST = "db.fploheqxhzpihgexlrkr.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "Ninguna123."  # La copias del panel "Connect"

# Crear conexión
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Crear tablas si no existen
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historicos (
                id SERIAL PRIMARY KEY,
                usuario_id INT REFERENCES usuarios(id),
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reflexion TEXT
            );
        """))
        conn.commit()

# Guardar usuario nuevo
def registrar_usuario(username, password):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO usuarios (username, password) VALUES (:u, :p)"),
                     {"u": username, "p": password})
        conn.commit()

# Guardar reflexión
def guardar_reflexion(usuario_id, reflexion):
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO historicos (usuario_id, reflexion) VALUES (:uid, :r)"),
                     {"uid": usuario_id, "r": reflexion})
        conn.commit()

# Ejemplo de uso
if __name__ == "__main__":
    init_db()
    st.write("Base de datos inicializada correctamente.")
