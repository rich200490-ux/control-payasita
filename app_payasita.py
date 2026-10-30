import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de la página web (Título e Icono en la pestaña del navegador)
st.set_page_config(
    page_title="Payasita Arcoíris - Mery Castillo",
    page_icon="🎉",
    layout="wide"
)

# Nombre del archivo donde se guardarán los datos en la nube
NOMBRE_ARCHIVO = "inventario_y_ganancias_payasita.xlsx"

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    inventario = []
    eventos = []
    if os.path.exists(NOMBRE_ARCHIVO):
        try:
            with pd.ExcelFile(NOMBRE_ARCHIVO) as xls:
                if "Inventario" in xls.sheet_names:
                    inventario = pd.read_excel(xls, sheet_name="Inventario").to_dict(orient="records")
                if "Eventos" in xls.sheet_names:
                    eventos = pd.read_excel(xls, sheet_name="Eventos").to_dict(orient="records")
        except Exception as e:
            st.error(f"Error al cargar el archivo Excel: {e}")
    return inventario, eventos

def guardar_datos(inventario, eventos):
    try:
        df_inv = pd.DataFrame(inventario) if inventario else pd.DataFrame(columns=["Artículo", "Stock", "Categoría"])
        df_ev = pd.DataFrame(eventos) if eventos else pd.DataFrame(columns=["Fecha", "Tipo Evento", "Monto", "Mes-Año", "OrdenMes"])
        
        with pd.ExcelWriter(NOMBRE_ARCHIVO, engine="openpyxl") as writer:
            df_inv.to_excel(writer, sheet_name="Inventario", index=False)
            df_ev.to_excel(writer, sheet_name="Eventos", index=False)
    except Exception as e:
        st.error(f"Error crítico al guardar los datos: {e}")

# Cargar las listas en la memoria de la página web
if "inventario" not in st.session_state or "eventos" not in st.session_state:
    st.session_state.inventario, st.session_state.eventos = cargar_datos()

# --- DISEÑO VISUAL PREMIUM (TÍTULO PRINCIPAL) ---
st.markdown("<h1 style='text-align: center; color: #ec4899;'>🎉 PAYASITA ARCOIRIS ANIMACIÓN DE EVENTOS MERY CASTILLO 🎉</h1>", unsafe_allow_html=True)
st.write("---")

# Crear las pestañas en la página web
tab_inv, tab_ganancias = st.tabs(["🎨 Inventario de Materiales", "🇨🇷 Control de Eventos y Ganancias"])

# ==========================================
# PESTAÑA 1: INVENTARIO DE MATERIALES
# ==========================================
with tab_inv:
    st.markdown("<h3 style='color: #db2777;'>📦 Registrar o Editar Material</h3>", unsafe_allow_html=True)
    
    # Crear columnas para el formulario de entrada
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        articulo = st.text_input("Artículo / Material:", key="txt_art").strip()
    with col2:
        stock = st.number_input("Cantidad / Stock:", min_value=0, value=1, step=1, key="num_stock")
    with col3:
        categoria = st.selectbox("Categoría:", ["Pinturas", "Pinceles", "Esponjas", "Stencil", "Stickers", "Otros Materiales"])
        
    if st.button("Guardar en Inventario 📦", type="primary"):
        if not articulo:
            st.warning("Por favor ingresa el nombre del artículo.")
        else:
            # Revisar si ya existe para actualizarlo o agregarlo
            existe = False
            for p in st.session_state.inventario:
                if p["Artículo"].lower() == articulo.lower():
                    p["Stock"] = stock
                    p["Categoría"] = categoria
                    existe = True
                    st.success(f"¡Cantidad de '{articulo}' actualizada con éxito!")
                    break
            
            if not existe:
                st.session_state.inventario.append({"Artículo": articulo, "Stock": stock, "Categoría": categoria})
                st.success(f"¡Material '{articulo}' registrado correctamente!")
                
            guardar_datos(st.session_state.inventario, st.session_state.eventos)
            st.rerun() # Actualiza la página instantáneamente

    st.write("---")
    st.markdown("<h4>📋 Materiales en Existencia</h4>", unsafe_allow_html=True)
    
    if st.session_state.inventario:
        df_inv_visual = pd.DataFrame(st.session_state.inventario)
        # Mostrar tabla interactiva donde se puede ordenar y buscar
        st.dataframe(df_inv_visual, use_container_width=True, hide_index=True)
        
        # Botón para borrar un elemento seleccionado por texto
        prod_a_borrar = st.selectbox("Selecciona un material si deseas eliminarlo por completo:", [""] + [p["Artículo"] for p in st.session_state.inventario])
        if prod_a_borrar and st.button("🗑️ Eliminar Material Seleccionado", type="secondary"):
            st.session_state.inventario = [p for p in st.session_state.inventario if p["Artículo"] != prod_a_borrar]
            guardar_datos(st.session_state.inventario, st.session_state.eventos)
            st.success(f"'{prod_a_borrar}' eliminado.")
            st.rerun()
    else:
        st.info("No hay materiales registrados en el inventario aún.")

# ==========================================
# PESTAÑA 2: EVENTOS Y GANANCIAS (COLONES)
# ==========================================
with tab_ganancias:
    st.markdown("<h3 style='color: #1e40af;'>💰 Registrar Fiesta / Evento Animado</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        tipo_evento = st.selectbox("Tipo de Fiesta:", ["Baby Shower", "Fiesta Infantil", "Fiesta Neón", "Otro Evento"])
    with col2:
        monto = st.number_input("Ganancia en Colones (₡):", min_value=0.0, value=0.0, step=1000.0)
    with col3:
        # 🌟 ¡Calendario web nativo! Funciona en tableta con un solo toque
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
            guardar_datos(st.session_state.inventario, st.session_state.eventos)
            st.success(f"¡Fiesta registrada! Se sumaron ₡{monto:,.2f} a {mes_ano_txt}.")
            st.rerun()

    st.write("---")
    
    # Mostrar tablas en paralelo (Historial y Cierre Mensual)
    if st.session_state.eventos:
        df_ev = pd.DataFrame(st.session_state.eventos)
        
        # Calcular Totales para el cuadro destacado
        total_general = df_ev["Monto"].sum()
        
        # Cuadro visual Premium para resaltar las ganancias totales en colones
        st.info(f"### 🇨🇷 TOTAL GENERAL GANADO EN EVENTOS: ₡ {total_general:,.2f}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4>📅 Historial de Fiestas</h4>", unsafe_allow_html=True)
            df_visual_ev = df_ev[["Fecha", "Tipo Evento", "Monto"]].copy()
            df_visual_ev["Monto"] = df_visual_ev["Monto"].map("₡{:,.2f}".format)
            st.dataframe(df_visual_ev, use_container_width=True, hide_index=True)
            
            # Opción para eliminar una fiesta errónea
            df_ev['Identificador'] = df_ev['Fecha'] + " - " + df_ev['Tipo Evento'] + " (₡" + df_ev['Monto'].map("{:,.0f}".format) + ")"
            evento_a_borrar = st.selectbox("Eliminar una fiesta por error de dedo:", [""] + df_ev['Identificador'].tolist())
            if evento_a_borrar and st.button("🗑️ Eliminar Fiesta Seleccionada"):
                idx_borrar = df_ev[df_ev['Identificador'] == evento_a_borrar].index[0]
                st.session_state.eventos.pop(int(idx_borrar))
                guardar_datos(st.session_state.inventario, st.session_state.eventos)
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
