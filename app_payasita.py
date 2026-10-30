import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuración de la página web
st.set_page_config(
    page_title="Payasita Arcoíris - Mery Castillo",
    page_icon="🎉",
    layout="wide"
)

st.markdown("<h1 style='text-align: center; color: #ec4899;'>🎉 PAYASITA ARCOIRIS ANIMACIÓN DE EVENTOS MERY CASTILLO 🎉</h1>", unsafe_allow_html=True)
st.write("---")

# Conexión oficial y protegida con la base de datos de Google Drive
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Cargar Inventario existente
    try:
        df_inv_prev = conn.read(worksheet="Inventario", ttl="2s")
        inventario = df_inv_prev.to_dict(orient="records") if not df_inv_prev.empty else []
    except:
        inventario = []
        
    # Cargar Eventos existentes
    try:
        df_ev_prev = conn.read(worksheet="Eventos", ttl="2s")
        eventos = df_ev_prev.to_dict(orient="records") if not df_ev_prev.empty else []
    except:
        eventos = []
except Exception as e:
    st.error("Conectando con el almacén seguro de Google Drive...")
    inventario = []
    eventos = []

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
            # Eliminar si ya existe para actualizar stock
            inventario = [p for p in inventario if str(p.get("Artículo", "")).lower() != articulo.lower()]
            inventario.append({"Artículo": articulo, "Stock": stock, "Categoría": categoria})
            
            try:
                conn.update(worksheet="Inventario", data=pd.DataFrame(inventario))
                st.success(f"¡Material '{articulo}' guardado automáticamente en la nube!")
                st.rerun()
            except Exception as e:
                st.error("Vincula el enlace en los Secrets de Streamlit para activar el guardado automático.")

    st.write("---")
    st.markdown("<h4>📋 Materiales en Existencia</h4>", unsafe_allow_html=True)
    if inventario:
        st.dataframe(pd.DataFrame(inventario), use_container_width=True, hide_index=True)
        prod_a_borrar = st.selectbox("Selecciona un material para eliminarlo por completo:", [""] + [p.get("Artículo", "") for p in inventario if "Artículo" in p])
        if prod_a_borrar and st.button("🗑️ Eliminar Material"):
            inventario = [p for p in inventario if p.get("Artículo", "") != prod_a_borrar]
            conn.update(worksheet="Inventario", data=pd.DataFrame(inventario))
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
            
            eventos.append({
                "Fecha": fecha_str, "Tipo Evento": tipo_evento, "Monto": monto, "Mes-Año": mes_ano_txt, "OrdenMes": orden_mes
            })
            
            try:
                conn.update(worksheet="Eventos", data=pd.DataFrame(eventos))
                st.success(f"¡Fiesta registrada automáticamente!")
                st.rerun()
            except Exception as e:
                st.error("Error de guardado.")

    st.write("---")
    
    if eventos:
        df_ev = pd.DataFrame(eventos)
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
                df_ev = df_ev[df_ev['Identificador'] != evento_a_borrar]
                df_save_ev = df_ev[["Fecha", "Tipo Evento", "Monto", "Mes-Año", "OrdenMes"]]
                conn.update(worksheet="Eventos", data=df_save_ev)
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
