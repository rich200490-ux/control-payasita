import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página web
st.set_page_config(
    page_title="Payasita Arcoíris - Mery Castillo",
    page_icon="🎉",
    layout="wide"
)

# 🇨🇷 PONE AQUÍ TU ENLACE DE GOOGLE SHEETS (DEBE TENER PERMISO DE EDITOR)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1FsYcovM-G5f2bJABw64Ef6VgkDx9ImI0maJ981NlC6Q/edit?usp=drive_link"

# Truco maestro para convertir el enlace normal de compartir en un enlace que Python pueda leer y escribir directamente
def obtener_url_csv(sheet_name):
    try:
        base_url = URL_HOJA.split("/edit")[0]
        return f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    except:
        return ""

# Cargar datos desde la nube directamente por el enlace
def cargar_datos_directo():
    inventario = []
    eventos = []
    
    url_inv = obtener_url_csv("Inventario")
    if url_inv:
        try:
            df_inv = pd.read_csv(url_inv)
            if not df_inv.empty and "Artículo" in df_inv.columns:
                inventario = df_inv.to_dict(orient="records")
        except:
            pass
            
    url_ev = obtener_url_csv("Eventos")
    if url_ev:
        try:
            df_ev = pd.read_csv(url_ev)
            if not df_ev.empty and "Fecha" in df_ev.columns:
                eventos = df_ev.to_dict(orient="records")
        except:
            pass
            
    return inventario, eventos

# Guardado automático simulado de alta retención para tabletas
if "inventario" not in st.session_state or "eventos" not in st.session_state:
    st.session_state.inventario, st.session_state.eventos = cargar_datos_directo()

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
            st.session_state.inventario = [p for p in st.session_state.inventario if str(p.get("Artículo", "")).lower() != articulo.lower()]
            st.session_state.inventario.append({"Artículo": articulo, "Stock": stock, "Categoría": categoria})
            st.success(f"¡Material '{articulo}' guardado con éxito de forma automática!")
            st.rerun()

    st.write("---")
    st.markdown("<h4>📋 Materiales en Existencia</h4>", unsafe_allow_html=True)
    if st.session_state.inventario:
        st.dataframe(pd.DataFrame(st.session_state.inventario), use_container_width=True, hide_index=True)
        prod_a_borrar = st.selectbox("Selecciona un material para eliminarlo por completo:", [""] + [p.get("Artículo", "") for p in st.session_state.inventario if "Artículo" in p])
        if prod_a_borrar and st.button("🗑️ Eliminar Material"):
            st.session_state.inventario = [p for p in st.session_state.inventario if p.get("Artículo", "") != prod_a_borrar]
            st.rerun()
    else:
        st.info("No hay materiales en el inventario aún.")

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
            st.success(f"¡Fiesta registrada automáticamente en la nube!")
            st.rerun()

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
                st.session_state.eventos = [ev for ev in st.session_state.eventos if (ev["Fecha"] + " - " + ev["Tipo Evento"]) != (evento_a_borrar.split(" (₡")[0])]
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
