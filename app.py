import streamlit as st
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import math
import re
from datetime import datetime
import os

st.set_page_config(page_title="Registro de Conciencia (ligero)", layout="centered")

# -------------------------
# Cargar secrets / fallback
# -------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL") if "SUPABASE_URL" in st.secrets else os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") if "SUPABASE_KEY" in st.secrets else os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Falta SUPABASE_URL o SUPABASE_KEY en secrets (Streamlit Cloud) o variables de entorno.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# Utilidades
# -------------------------
def email_valido(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email or "") is not None

def registrar_usuario(username: str, password: str, email: str) -> (bool, str):
    if not username or not password or not email:
        return False, "Completa usuario, email y contraseña."
    if not email_valido(email):
        return False, "Email inválido."
    # verificar existencia
    exists = supabase.table("usuarios").select("id").or_(f"username.eq.{username},email.eq.{email}").execute()
    if exists.data:
        return False, "Usuario o email ya registrado."
    hashed = generate_password_hash(password)
    resp = supabase.table("usuarios").insert({
        "username": username,
        "password": hashed,
        "email": email
    }).execute()
    if resp.error:
        return False, "Error al registrar (revisa los datos)."
    return True, "Usuario registrado correctamente."

def autenticar_usuario(username: str, password: str):
    if not username or not password:
        return False, "Rellena usuario y contraseña."
    res = supabase.table("usuarios").select("*").eq("username", username).execute()
    if not res.data:
        return False, "Usuario no encontrado."
    user = res.data[0]
    if check_password_hash(user["password"], password):
        return True, user
    return False, "Contraseña incorrecta."

def cambiar_contrasena(email: str, nueva: str) -> (bool, str):
    if not email_valido(email):
        return False, "Email inválido."
    hashed = generate_password_hash(nueva)
    resp = supabase.table("usuarios").update({"password": hashed}).eq("email", email).execute()
    if resp.error:
        return False, "No se pudo actualizar. Verifica el email."
    if not resp.data:
        return False, "Email no encontrado."
    return True, "Contraseña actualizada."

# Preguntas / CRUD
def guardar_pregunta(usuario: str, pregunta: str) -> bool:
    if not pregunta.strip():
        return False
    resp = supabase.table("preguntas").insert({
        "usuario": usuario,
        "pregunta": pregunta,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return resp.error is None

def obtener_preguntas_usuario(usuario: str) -> pd.DataFrame:
    res = supabase.table("preguntas").select("*").eq("usuario", usuario).order("created_at", desc=True).execute()
    data = res.data or []
    if not data:
        return pd.DataFrame(columns=["id", "usuario", "pregunta", "created_at"])
    df = pd.DataFrame(data)
    # normalizar columnas si vienen con keys diferentes
    if "created_at" not in df.columns and "createdAt" in df.columns:
        df = df.rename(columns={"createdAt": "created_at"})
    return df[["id", "usuario", "pregunta", "created_at"]]

def eliminar_pregunta(id_reg: int) -> bool:
    resp = supabase.table("preguntas").delete().eq("id", id_reg).execute()
    return resp.error is None

# -------------------------
# UI: Registro / Login
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None

st.sidebar.title("Cuenta")
menu = st.sidebar.radio("Ir a:", ["Login", "Registro", "Recuperar contraseña", "Mi espacio"])

if menu == "Registro":
    st.header("Crear cuenta")
    new_user = st.text_input("Usuario", key="reg_user")
    new_email = st.text_input("Correo electrónico", key="reg_email")
    new_pass = st.text_input("Contraseña", type="password", key="reg_pass")
    if st.button("Registrarme"):
        ok, msg = registrar_usuario(new_user.strip(), new_pass, new_email.strip())
        if ok:
            st.success(msg + " — Ahora inicia sesión.")
        else:
            st.error(msg)

elif menu == "Login":
    st.header("Iniciar sesión")
    user = st.text_input("Usuario", key="login_user")
    pw = st.text_input("Contraseña", type="password", key="login_pass")
    if st.button("Ingresar"):
        ok, res = autenticar_usuario(user.strip(), pw)
        if ok:
            st.session_state.user = res
            st.success(f"Bienvenido {res['username']}")
        else:
            st.error(res)

elif menu == "Recuperar contraseña":
    st.header("Recuperar / cambiar contraseña")
    email = st.text_input("Ingresa el correo asociado")
    nueva = st.text_input("Nueva contraseña", type="password")
    if st.button("Actualizar contraseña"):
        ok, msg = cambiar_contrasena(email.strip(), nueva)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

# -------------------------
# Mi espacio (autenticado)
# -------------------------
elif menu == "Mi espacio":
    if not st.session_state.user:
        st.warning("Debes iniciar sesión antes de entrar en 'Mi espacio'.")
    else:
        usuario = st.session_state.user["username"]
        st.header(f"Bienvenido, {usuario}")

        # Form: guardar nueva pregunta
        st.subheader("➕ Nueva pregunta / reflexión")
        nueva = st.text_area("Escribe tu pregunta o reflexión", height=120, key="nueva_preg")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Guardar"):
                if guardar_pregunta(usuario, nueva):
                    st.success("Pregunta guardada ✅")
                else:
                    st.error("No se pudo guardar (campo vacío?)")
        with col2:
            if st.button("Cerrar sesión"):
                st.session_state.user = None
                st.experimental_rerun()

        st.markdown("---")

        # Mostrar historial con búsqueda y paginación (ligero)
        df = obtener_preguntas_usuario(usuario)

        if df.empty:
            st.info("Aún no tienes preguntas guardadas.")
        else:
            # Búsqueda global
            q = st.text_input("🔎 Buscar en mis preguntas")
            if q:
                ql = q.lower()
                df = df[df.apply(lambda r: r.astype(str).str.lower().str.contains(ql).any(), axis=1)]

            # Paginación
            page_size = st.selectbox("Registros por página", options=[5, 10, 20], index=0)
            total = len(df)
            total_pages = max(1, math.ceil(total / page_size))
            page = st.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)

            start = (page - 1) * page_size
            end = start + page_size
            mostrar = df.iloc[start:end].reset_index(drop=True)

            # Mostrar tabla simple
            st.write(f"Mostrando {start+1} a {min(end, total)} de {total} registros")
            st.table(mostrar[["id", "pregunta", "created_at"]].rename(columns={
                "id": "ID", "pregunta": "Pregunta", "created_at": "Fecha"
            }))

            # Opciones por fila: eliminar
            seleccionar = st.number_input("ID para eliminar (vacío si no):", value=0, step=1)
            if st.button("Eliminar ID seleccionado"):
                if seleccionar > 0:
                    if eliminar_pregunta(int(seleccionar)):
                        st.success("Registro eliminado.")
                        st.experimental_rerun()
                    else:
                        st.error("No se pudo eliminar (ID inválido).")
                else:
                    st.warning("Ingresa un ID válido (>0).")

