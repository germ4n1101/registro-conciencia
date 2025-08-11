import streamlit as st
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 🔗 Conexión a Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="🧠 Registro de Conciencia", page_icon="🧠", layout="centered")

# 📌 Funciones de usuario
def register_user(username, password):
    hashed_pw = generate_password_hash(password)
    existing = supabase.table("users").select("*").eq("username", username).execute()
    if existing.data:
        return False, "❌ El usuario ya existe."
    supabase.table("users").insert({"username": username, "password": hashed_pw}).execute()
    return True, "✅ Usuario registrado."

def login_user(username, password):
    result = supabase.table("users").select("*").eq("username", username).execute()
    if not result.data:
        return False, "❌ Usuario no encontrado."
    user = result.data[0]
    if check_password_hash(user["password"], password):
        return True, user
    return False, "❌ Contraseña incorrecta."

def save_reflection(user_id, text):
    supabase.table("reflections").insert({
        "user_id": user_id,
        "text": text,
        "created_at": datetime.now().isoformat()
    }).execute()

def get_reflections(user_id):
    return supabase.table("reflections").select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data

# 📌 Menú lateral
menu = st.sidebar.selectbox("Menú", ["Registro", "Login", "Reflexiones"])

if menu == "Registro":
    st.subheader("Crear cuenta")
    new_user = st.text_input("Usuario")
    new_password = st.text_input("Contraseña", type="password")
    if st.button("Registrar"):
        ok, msg = register_user(new_user, new_password)
        st.success(msg) if ok else st.error(msg)

elif menu == "Login":
    st.subheader("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        ok, data = login_user(username, password)
        if ok:
            st.session_state["logged_in"] = True
            st.session_state["user"] = data
            st.success(f"✅ Bienvenido {data['username']}")
        else:
            st.error(data)

elif menu == "Reflexiones":
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("⚠️ Debes iniciar sesión primero.")
    else:
        st.subheader("✏️ Nueva reflexión")
        reflection = st.text_area("Escribe tu reflexión aquí...")
        if st.button("Guardar reflexión"):
            save_reflection(st.session_state["user"]["id"], reflection)
            st.success("✅ Reflexión guardada.")

        st.subheader("📜 Historial de reflexiones")
        reflections = get_reflections(st.session_state["user"]["id"])
        if reflections:
            for r in reflections:
                st.markdown(f"**{r['created_at']}** — {r['text']}")
        else:
            st.info("Aún no tienes reflexiones guardadas.")

