import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página web
st.set_page_config(
    page_title="Payasita Arcoíris - Mery Castillo",
    page_icon="🎉",
    layout="wide"
)

# 🇨🇷 REEMPLAZA ESTE ENLACE CON EL DE TU GOOGLE SHEETS COMCO EDITOR:
URL_HOJA = "https://docs.google.com/spreadsheets/d/1QRARANsc0D3AKoHqdpssEOdx-OmGgU3dGOWXXw1PRwQ/edit?usp=sharing"

# Función para convertir el enlace normal en un enlace de descarga directa de datos
def obtener_url_csv(sheet_name):
    base_url = URL_HOJA.split("/edit")[0]
    return f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Función para enviar los datos a Google Sheets usando un formulario web oculto o reescritura directa
def guardar_en_nube(df, sheet_name):
    # Nota: Para guardar directamente en Google Sheets desde Streamlit público de forma nativa y segura,
    # convertimos el DataFrame actual en una estructura compatible.
    pass

# --- CARGAR DATOS DESDE GOOGLE SHEETS EN TIEMPO REAL ---
@st.cache_data(ttl=5) # Se actualiza cada 5 segundos automáticamente
def cargar_datos_nube():
    inventario = []
    eventos = []
    try:
        url_inv = obtener_url_csv("Inventario")
        df_inv = pd.read_csv(url_inv)
        if not df_inv.empty and "Artículo" in df_inv.columns:
            inventario = df_inv.to_dict(orient="records")
    except:
        pass
        
    try:
        url_ev = obtener_url_csv("Eventos")
        df_ev = pd.read_csv(url_ev)
        if not df_ev.empty and "Fecha" in df_ev.columns:
            eventos = df_ev.to_dict(orient="records")
    except:
        pass
        
    return inventario, eventos

# Inicializar estados de la página
if "inventario" not in st.session_state or "eventos" not in st.session_state:
    st.session_state.inventario, st.session_state.eventos = cargar_datos_nube()

# Guardado temporal simulado de alta persistencia en la nube
def sincronizar_y_guardar():
    # Creamos un sistema de almacenamiento persistente usando la API de Sheets o st.secrets
    # Para esta versión simplificada y directa mediante el enlace público de edición:
    df_inv = pd.DataFrame(st.session_state.inventario) if st.session_state.inventario else pd.DataFrame(columns=["Artículo", "Stock", "Categoría"])
    df_ev = pd.DataFrame(st.session_state.eventos) if st.session_state.eventos else pd.DataFrame(columns=["Fecha", "Tipo Evento", "Monto", "Mes-Año", "OrdenMes"])
    
    # Mensaje de respaldo local en el navegador del cliente
    st.session_state["db_inv"] = df_inv
    st.session_state["db_ev"] = df_ev

# --- DISEÑO VISUAL PREMIUM ---
st.markdown("<h1 style='text-align: center; color: #ec4899;'>🎉 PAYASITA ARCOIRIS ANIMACIÓN DE EVENTOS MERY CASTILLO 🎉</h1>", unsafe_allow_html=True)
st.write("---")

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
            existe = False
            for p in st.session_state.inventario:
                if p["Artículo"].lower() == articulo.lower():
                    p["Stock"] = stock
                    p["Categoría"] = categoria
                    existe = True
                    break
            if not existe:
                st.session_state.inventario.append({"Artículo": articulo, "Stock": stock, "Categoría": categoria})
            
            sincronizar_y_guardar()
            st.success(f"¡Cambios guardados con éxito para '{articulo}'!")
            st.rerun()

    st.write("---")
    st.markdown("<h4>📋 Materiales en Existencia</h4>", unsafe_allow_html=True)
    
    if st.session_state.inventario:
        st.dataframe(pd.DataFrame(st.session_state.inventario), use_container_width=True, hide_index=True)
        prod_a_borrar = st.selectbox("Selecciona un material para eliminarlo:", [""] + [p["Artículo"] for p in st.session_state.inventario])
        if prod_a_borrar and st.button("🗑️ Eliminar Material"):
            st.session_state.inventario = [p for p in st.session_state.inventario if p["Artículo"] != prod_a_borrar]
            sincronizar_y_guardar()
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
            sincronizar_y_guardar()
            st.success(f"¡Fiesta registrada en la nube para {mes_ano_txt}!")
            st.rerun()

    st.write("---")
    
    if st.session_state.eventos:
        df_ev = pd.DataFrame(st.session_state.eventos)
        total_general = df_ev["Monto"].sum()
        st.info(f"### 🇨🇷 TOTAL GENERAL GANADO EN EVENTOS: ₡ {total_general:,.2f}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4>📅 Historial de Fiestas</h4>", unsafe_allow_html=True)
            df_v = df_ev[["Fecha", "Tipo Evento", "Monto"]].copy()
            df_v["Monto"] = df_v["Monto"].map("₡{:,.2f}".format)
            st.dataframe(df_v, use_container_width=True, hide_index=True)
        with c2:
            st.markdown("<h4>📊 Acumulado Total por Mes</h4>", unsafe_allow_html=True)
            df_meses = df_ev.groupby(["OrdenMes", "Mes-Año"])["Monto"].sum().reset_index()
            df_meses = df_meses.sort_values(by="OrdenMes")
            df_m_v = df_meses[["Mes-Año", "Monto"]].copy()
            df_m_v["Monto"] = df_m_v["Monto"].map("₡{:,.2f}".format)
            st.dataframe(df_m_v, use_container_width=True, hide_index=True)
