import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración de la página web
st.set_page_config(
    page_title="Payasita Arcoíris - Mery Castillo",
    page_icon="🎉",
    layout="wide"
)

# Inicializar los almacenes de datos internos y seguros en el navegador
if "inventario" not in st.session_state:
    st.session_state.inventario = []
if "eventos" not in st.session_state:
    st.session_state.eventos = []

# --- DISEÑO VISUAL PREMIUM (TÍTULO PRINCIPAL) ---
st.markdown("<h1 style='text-align: center; color: #ec4899;'>🎉 PAYASITA ARCOIRIS ANIMACIÓN DE EVENTOS MERY CASTILLO 🎉</h1>", unsafe_allow_html=True)
st.write("---")

# Crear las pestañas en la página web
tab_inv, tab_ganancias, tab_respaldo = st.tabs(["🎨 Inventario de Materiales", "🇨🇷 Control de Eventos y Ganancias", "💾 Respaldar Datos"])

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
            # Reemplazar si el artículo ya existe para actualizar stock
            st.session_state.inventario = [p for p in st.session_state.inventario if p.get("Artículo", "").lower() != articulo.lower()]
            st.session_state.inventario.append({"Artículo": articulo, "Stock": stock, "Categoría": categoria})
            st.success(f"¡Material '{articulo}' guardado con éxito!")
            st.rerun()

    st.write("---")
    st.markdown("<h4>📋 Materiales en Existencia</h4>", unsafe_allow_html=True)
    
    if st.session_state.inventario:
        df_inv_visual = pd.DataFrame(st.session_state.inventario)
        st.dataframe(df_inv_visual, use_container_width=True, hide_index=True)
        
        prod_a_borrar = st.selectbox("Selecciona un material si deseas eliminarlo:", [""] + [p["Artículo"] for p in st.session_state.inventario])
        if prod_a_borrar and st.button("🗑️ Eliminar Material Seleccionado"):
            st.session_state.inventario = [p for p in st.session_state.inventario if p["Artículo"] != prod_a_borrar]
            st.success(f"'{prod_a_borrar}' eliminado.")
            st.rerun()
    else:
        st.info("No hay materiales registrados en el inventario aún.")

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
            st.warning("Por favor ingresa un monto mayor a ₡0.")
        else:
            fecha_str = fecha_sel.strftime('%d/%m/%Y')
            meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            mes_ano_txt = f"{meses_nombres[fecha_sel.month - 1]} {fecha_sel.year}"
            orden_mes = f"{fecha_sel.year}-{fecha_sel.month:02d}"
            
            st.session_state.eventos.append({
                "Fecha": fecha_str,
                "Tipo Evento": tipo_evento,
                "Monto": monto,
                "Mes-Año": mes_ano_txt,
                "OrdenMes": orden_mes
            })
            st.success(f"¡Fiesta registrada con éxito para {mes_ano_txt}!")
            st.rerun()

    st.write("---")
    
    if st.session_state.eventos:
        df_ev = pd.DataFrame(st.session_state.eventos)
        total_general = df_ev["Monto"].sum()
        
        # Cuadro visual destacado para las ganancias totales
        st.info(f"### 🇨🇷 TOTAL GENERAL GANADO EN EVENTOS: ₡ {total_general:,.2f}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4>📅 Historial de Fiestas</h4>", unsafe_allow_html=True)
            df_visual_ev = df_ev[["Fecha", "Tipo Evento", "Monto"]].copy()
            df_visual_ev["Monto"] = df_visual_ev["Monto"].map("₡{:,.2f}".format)
            st.dataframe(df_visual_ev, use_container_width=True, hide_index=True)
            
            df_ev['Identificador'] = df_ev['Fecha'] + " - " + df_ev['Tipo Evento'] + " (₡" + df_ev['Monto'].map("{:,.0f}".format) + ")"
            evento_a_borrar = st.selectbox("Eliminar una fiesta por error de dedo:", [""] + df_ev['Identificador'].tolist())
            if evento_a_borrar and st.button("🗑️ Eliminar Fiesta Seleccionada"):
                idx_borrar = df_ev[df_ev['Identificador'] == evento_a_borrar].index
                st.session_state.eventos.pop(int(idx_borrar))
                st.success("Fiesta eliminada correctamente del registro.")
                st.rerun()
                
        with c2:
            st.markdown("<h4>📊 Acumulado Total por Mes</h4>", unsafe_allow_html=True)
            df_meses = df_ev.groupby(["OrdenMes", "Mes-Año"])["Monto"].sum().reset_index()
            df_meses = df_meses.sort_values(by="OrdenMes")
            df_meses_visual = df_meses[["Mes-Año", "Monto"]].copy()
            df_meses_visual["Monto"] = df_meses_visual["Monto"].map("₡{:,.2f}".format)
            st.dataframe(df_meses_visual, use_container_width=True, hide_index=True)
    else:
        st.info("No se han registrado eventos ni ganancias todavía.")

# ==========================================
# PESTAÑA 3: RESPALDAR DATOS EN LA TABLETA
# ==========================================
with tab_respaldo:
    st.markdown("<h3 style='color: #1f2937;'>💾 Guardar y Descargar Base de Datos</h3>", unsafe_allow_html=True)
    st.write("Para asegurar que la información quede protegida, genera tu archivo de Excel de respaldo en la memoria de tu tableta antes de cerrar la página.")
    
    # Crear archivo Excel en la memoria en tiempo real
    buffer = io.BytesIO()
    df_inv_save = pd.DataFrame(st.session_state.inventario) if st.session_state.inventario else pd.DataFrame(columns=["Artículo", "Stock", "Categoría"])
    df_ev_save = pd.DataFrame(st.session_state.eventos) if st.session_state.eventos else pd.DataFrame(columns=["Fecha", "Tipo Evento", "Monto", "Mes-Año", "OrdenMes"])
    
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_inv_save.to_excel(writer, sheet_name="Inventario", index=False)
        df_ev_save.to_excel(writer, sheet_name="Eventos", index=False)
    
    buffer.seek(0)
    
    st.download_button(
        label="📥 DESCARGAR RESPALDO DE EXCEL EN LA TABLETA",
        data=buffer,
        file_name="inventario_y_ganancias_payasita.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
