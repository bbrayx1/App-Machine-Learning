import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Heart Dashboard", layout="wide")

# --- CARGA DEL MODELO ---
model_bundle = joblib.load("models/meta_model.pkl")
model = model_bundle["model"]
feature_names = model_bundle["features"]

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        .sidebar .sidebar-content {
            background-color: #202124;
            color: white;
        }
        .css-1d391kg p, .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
            color: white;
        }
        .rounded-card {
            background-color: #2C2D31;
            padding: 1.2rem;
            border-radius: 16px;
            box-shadow: 0 0 12px rgba(0, 0, 0, 0.3);
            margin-bottom: 1.2rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <img src='https://static.vecteezy.com/system/resources/thumbnails/008/442/086/small/illustration-of-human-icon-user-symbol-icon-modern-design-on-blank-background-free-vector.jpg' style='border-radius: 50%; width: 100px; height: 100px; object-fit: cover;'>
            <h3 style='color: white; margin-top: 0.5rem;'>ADMIN 123</h3>
            <p style='color: #bbbbbb; font-size: 0.9rem;'>admin@salud.com</p>
        </div>
        <hr style='border: 1px solid #444;'>
    """, unsafe_allow_html=True)

    st.markdown("### Navegación")
    if "menu" not in st.session_state:
        st.session_state.menu = "Predicción Individual"

    if st.button("Predicción Individual"):
        st.session_state.menu = "Predicción Individual"
    if st.button("CSV Masivo"):
        st.session_state.menu = "CSV Masivo"

# --- FUNCIÓN DE PREDICCIÓN ---
def predict_patient(data):
    data = data[feature_names]
    return model.predict_proba(data)[0]

# --- PREDICCIÓN INDIVIDUAL ---
if st.session_state.menu == "Predicción Individual":
    st.title("Evaluación individual de paciente")
    col1, spacer, col2 = st.columns([1.2, 0.2, 1.8])

    with col1:
        st.subheader("Datos personales")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            age = st.slider('Edad (años)', 20, 100, 50)
        with col_a2:
            sex = st.radio("Sexo", options=[0, 1], format_func=lambda x: "Femenino" if x == 0 else "Masculino", horizontal=True)

        st.markdown("---")
        st.subheader("Exámenes clínicos")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            ef = st.slider('Fracción de eyección (%)', 10, 80, 50)
            cpk = st.slider('Creatinina fosfoquinasa (CPK)', 10, 800, 200)
            platelets = st.slider('Plaquetas (x10⁵ / μL)', 100.0, 800.0, 250.0)
        with col_b2:
            sc = st.slider('Creatinina sérica (mg/dL)', 0.0, 10.0, 1.0)
            ss = st.slider('Sodio sérico (mEq/L)', 100, 200, 140)
            time = st.slider('Tiempo de seguimiento (días)', 0, 300, 100)

        st.markdown("---")
        st.subheader("Condiciones clínicas")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            anaemia = st.radio("Anemia", options=[0, 1], format_func=lambda x: "No" if x == 0 else "Sí", horizontal=True)
            hbp = st.radio("Presión Alta", options=[0, 1], format_func=lambda x: "No" if x == 0 else "Sí", horizontal=True)
        with col_c2:
            diabetes = st.radio("Diabetes", options=[0, 1], format_func=lambda x: "No" if x == 0 else "Sí", horizontal=True)
            smoking = st.radio("Fumador", options=[0, 1], format_func=lambda x: "No" if x == 0 else "Sí", horizontal=True)

        patient_data = pd.DataFrame([{
            'age': age,
            'anaemia': anaemia,
            'creatinine_phosphokinase': cpk,
            'diabetes': diabetes,
            'ejection_fraction': ef,
            'high_blood_pressure': hbp,
            'platelets': platelets,
            'serum_creatinine': sc,
            'serum_sodium': ss,
            'sex': sex,
            'smoking': smoking,
            'time': time
        }])
        patient_data = patient_data[feature_names]

    with col2:
        st.subheader("Evaluación del modelo")
        normales = {"Fracción de eyección": 50, "CPK": 80, "Plaquetas": 300.0}
        datos_usuario = {"Fracción de eyección": ef, "CPK": cpk, "Plaquetas": platelets}

        try:
            proba = predict_patient(patient_data)
            proba_riesgo, proba_sano = round(proba[1]*100), round(proba[0]*100)
        except Exception as e:
            st.error(f"Error al predecir: {e}")
            st.stop()

        col_riesgo, col_sano = st.columns(2)
        with col_riesgo:
            st.markdown(f"""
                <div style='text-align:center; background-color:#2f2f3f; border-radius:16px;
                            padding:1rem; margin-bottom:1rem; border: 2px solid red;'>
                    <h3 style='color:red;'>Con Riesgo</h3>
                    <div style='font-size:2rem; color:white;'>{proba_riesgo} %</div>
                </div>
            """, unsafe_allow_html=True)
        with col_sano:
            st.markdown(f"""
                <div style='text-align:center; background-color:#2f2f3f; border-radius:16px;
                            padding:1rem; margin-bottom:1rem; border: 2px solid green;'>
                    <h3 style='color:lime;'>Sin Riesgo</h3>
                    <div style='font-size:2rem; color:white;'>{proba_sano} %</div>
                </div>
            """, unsafe_allow_html=True)

        for var, val in datos_usuario.items():
            normal = normales[var]
            st.markdown(f"#### {var} (Normal: {normal})")
            fig = go.Figure(go.Bar(
                x=[val, normal],
                y=['Paciente', 'Valor normal'],
                orientation='h',
                marker_color=['#00BFFF', 'gray']
            ))
            fig.update_layout(
                height=140,
                margin=dict(t=20, b=20),
                template="plotly_dark",
                xaxis=dict(title='Valor')
            )
            st.plotly_chart(fig, use_container_width=True)

# --- CSV MASIVO ---
elif st.session_state.menu == "CSV Masivo":
    st.title("Evaluación masiva de pacientes")
    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        missing_cols = [col for col in feature_names if col not in df.columns]
        if missing_cols:
            st.error("Faltan columnas en el archivo:")
            st.code(", ".join(missing_cols))
        else:
            df = df[feature_names]
            st.dataframe(df.head())
            try:
                predictions = model.predict(df)
                df['Predicción'] = ["Sí" if p == 1 else "No" for p in predictions]
                st.success("Predicciones realizadas correctamente")
                st.dataframe(df)

                pred_counts = df['Predicción'].value_counts()
                pie_chart = px.pie(
                    values=pred_counts.values,
                    names=pred_counts.index,
                    title="Distribución de predicciones",
                    color_discrete_sequence=["#EF553B", "#00CC96"]
                )
                st.plotly_chart(pie_chart, use_container_width=True)

                variable = st.selectbox("Comparar variable:", feature_names)
                box_plot = px.box(
                    df, x="Predicción", y=variable, color="Predicción",
                    title=f"{variable.capitalize()} según predicción",
                    color_discrete_sequence=["#EF553B", "#00CC96"],
                    points="all"
                )
                st.plotly_chart(box_plot, use_container_width=True)
            except Exception as e:
                st.error(f"Error al procesar las predicciones: {e}")
