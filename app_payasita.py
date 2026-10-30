import streamlit as st
import pandas as pd
import json
import requests
import base64
from datetime import datetime

# Configuración de la página web
st.set_page_config(
    page_title="Payasita Arcoíris - Mery Castillo",
    page_icon="🎉",
    layout="wide"
)

# 🛠️ DATOS DE TU CONFIGURACIÓN DE GITHUB (ESCRIBE LOS TUYOS AQUÍ):
GITHUB_USER = "@rich200490-ux"
GITHUB_REPO = "control-payasita"  # El nombre de tu repositorio en GitHub

# Recuperar el token desde los secretos seguros de Streamlit
TOKEN = st.secrets.get("GITHUB_TOKEN", "")

# Rutas de almacenamiento en tu nube de GitHub (Dirección de API corregida)
URL_INV = f"https://github.com{GITHUB_USER}/{GITHUB_REPO}/contents/inventario.json"
URL_EV = f"https://github.com{GITHUB_USER}/{GITHUB_REPO}/contents/eventos.json"


def leer_de_github(url):
    if not TOKEN:
        return [], None
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        datos = r.json()
        contenido = base64.b64decode(datos['content']).decode('utf-8')
        return json.loads(contenido), datos['sha']
    return [], None

def guardar_en_github(url, datos_dict, sha):
    if not TOKEN:
        return False
    headers = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}
    contenido_bytes = json.dumps(datos_dict, indent=4).encode('utf-8')
    contenido_b64 = base64.b64encode(contenido_bytes).decode('utf-8')
    
    payload = {
        "message": "Actualización de datos desde la tableta",
        "content": contenido_b64
    }
    if sha:
        payload["sha"] = sha
        
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    return r.status_code in [200, 201]

# --- CARGA INICIAL DE DATOS DESDE GITHUB ---
if "data_cargada" not in st.session_state:
    st.session_state.inventario, st.session_state.sha_inv = leer_de_github(URL_INV)
    st.session_state.eventos, st.session_state.sha_ev = leer_de_github(URL_EV)
    st.session_state.data_cargada = True

st.markdown("<h1 style='text-align: center; color: #ec4899;'>🎉 PAYASITA ARCOIRIS ANIMACIÓN DE EVENTOS MERY CASTILLO 🎉</h1>", unsafe_allow_html=True)
st.write("---")

if not TOKEN:
    st.error("⚠️ Falta configurar la llave de seguridad (Token) en los Secrets de Streamlit. Sigue el Paso 3.")

tab_inv, tab_ganancias = st.tabs(["🎨 Inventario de Materiales", "🇨🇷 Control de Eventos y Ganancias"])

# ==========================================
# PESTAÑA 1: INVENTARIO DE MATERIALES
# ==========================================
with tab_inv:
    st.markdown("<h3 style='color: #db2777;'>📦 Registrar o Editar Material</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        articulo = st.text_input("Artículo / Material:", key="txt_art").strip()
    with col2:
        stock = st.number_input("Cantidad / Stock:", min_value=0, value=1, step=1)
    with col3:
        categoria = st.selectbox("Categoría:", ["Pinturas", "Pinceles", "Esponjas", "Stencil", "Stickers", "Otros Materiales"])
        
    if st.button("Guardar en Inventario 📦", type="primary"):
        if not articulo:
            st.warning("Por favor ingresa el nombre del artículo.")
        else:
            st.session_state.inventario = [p for p in st.session_state.inventario if p.get("Artículo", "").lower() != articulo.lower()]
            st.session_state.inventario.append({"Artículo": articulo, "Stock": stock, "Categoría": categoria})
            
            exito = guardar_en_github(URL_INV, st.session_state.inventario, st.session_state.sha_inv)
            if exito:
                st.success(f"¡Material '{articulo}' guardado de forma permanente en la nube!")
                st.session_state.inventario, st.session_state.sha_inv = leer_de_github(URL_INV)
                st.rerun()
            else:
                st.error("Error al guardar en la nube. Revisa los permisos de tu Token.")

    st.write("---")
    st.markdown("<h4>📋 Materiales en Existencia</h4>", unsafe_allow_html=True)
    if st.session_state.inventario:
        st.dataframe(pd.DataFrame(st.session_state.inventario), use_container_width=True, hide_index=True)
        prod_a_borrar = st.selectbox("Selecciona un material para eliminarlo:", [""] + [p.get("Artículo", "") for p in st.session_state.inventario])
        if prod_a_borrar and st.button("🗑️ Eliminar Material"):
            st.session_state.inventario = [p for p in st.session_state.inventario if p.get("Artículo", "") != prod_a_borrar]
            guardar_en_github(URL_INV, st.session_state.inventario, st.session_state.sha_inv)
            st.session_state.inventario, st.session_state.sha_inv = leer_de_github(URL_INV)
            st.rerun()
    else:
        st.info("No hay materiales en el inventario.")

# ==========================================
# PESTAÑA 2: EVENTOS Y GANANCIAS (COLONES)
# ==========================================
with tab_ganancias:
    st.markdown("<h3 style='color: #1e40af;'>💰 Registrar Fiesta / Evento Animado</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_evento = st.selectbox("Tipo de Fiesta:", ["Baby Shower", "Fiesta Infantil", "Fiesta Neón", "Otro Evento"])
    with col2:
        monto = st.number_input("Ganancia en Colones (₡):", min_value=0.0, value=0.0, step=5000.0)
    with col3:
        fecha_sel = st.date_input("Fecha de la Fiesta:", datetime.today())
        
    if st.button("Registrar Evento 💰", type="primary"):
        if monto <= 0:
            st.warning("Ingresa un monto válido.")
        else:
            fecha_str = fecha_sel.strftime('%d/%m/%Y')
            meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            mes_ano_txt = f"{meses_nombres[fecha_sel.month - 1]} {fecha_sel.year}"
            orden_mes = f"{fecha_sel.year}-{fecha_sel.month:02d}"
            
            st.session_state.eventos.append({
                "Fecha": fecha_str, "Tipo Evento": tipo_evento, "Monto": monto, "Mes-Año": mes_ano_txt, "OrdenMes": orden_mes
            })
            
            exito = guardar_en_github(URL_EV, st.session_state.eventos, st.session_state.sha_ev)
            if exito:
                st.success(f"¡Fiesta guardada permanentemente en la nube!")
                st.session_state.eventos, st.session_state.sha_ev = leer_de_github(URL_EV)
                st.rerun()
            else:
                st.error("Error al registrar la fiesta.")

    st.write("---")
    
    if st.session_state.eventos:
        df_ev = pd.DataFrame(st.session_state.eventos)
        total_general = pd.to_numeric(df_ev["Monto"]).sum()
        st.info(f"### 🇨🇷 TOTAL GENERAL GANADO EN EVENTOS: ₡ {total_general:,.2f}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4>📅 Historial de Fiestas</h4>", unsafe_allow_html=True)
            df_v = df_ev[["Fecha", "Tipo Evento", "Monto"]].copy()
            df_v["Monto"] = pd.to_numeric(df_v["Monto"]).map("₡{:,.2f}".format)
            st.dataframe(df_v, use_container_width=True, hide_index=True)
            
            df_ev['Identificador'] = df_ev['Fecha'] + " - " + df_ev['Tipo Evento'] + " (₡" + pd.to_numeric(df_ev['Monto']).map("{:,.0f}".format) + ")"
            evento_a_borrar = st.selectbox("Eliminar una fiesta por error de dedo:", [""] + df_ev['Identificador'].tolist())
            if evento_a_borrar and st.button("🗑️ Eliminar Fiesta Seleccionada"):
                st.session_state.eventos = [ev for ev in st.session_state.eventos if (ev["Fecha"] + " - " + ev["Tipo Evento"]) != (evento_a_borrar.split(" - ")[0], evento_a_borrar.split(" - ")[1].split(" (")[0])]
                guardar_en_github(URL_EV, st.session_state.eventos, st.session_state.sha_ev)
                st.session_state.eventos, st.session_state.sha_ev = leer_de_github(URL_EV)
                st.success("Fiesta eliminada.")
                st.rerun()
                
        with c2:
            st.markdown("<h4>📊 Acumulado Total por Mes</h4>", unsafe_allow_html=True)
            df_ev["Monto"] = pd.to_numeric(df_ev["Monto"])
            df_meses = df_ev.groupby(["OrdenMes", "Mes-Año"])["Monto"].sum().reset_index()
            df_meses = df_meses.sort_values(by="OrdenMes")
            df_m_v = df_meses[["Mes-Año", "Monto"]].copy()
            df_m_v["Monto"] = df_m_v["Monto"].map("₡{:,.2f}".format)
            st.dataframe(df_m_v, use_container_width=True, hide_index=True)
    else:
        st.info("No se han registrado eventos todavía.")
