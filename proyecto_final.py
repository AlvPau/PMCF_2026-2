import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.stats import norm, t, skew, kurtosis
from datetime import date

# Parámetros Globales
TICKER = "JPM"
START = "2010-01-01"

class MarketRiskModel:
    def __init__(self, returns, window=252):
        self.returns = returns
        self.window = window

    def calculate_metrics(self, alpha):
        mu = self.returns.rolling(window=self.window).mean()
        sigma = self.returns.rolling(window=self.window).std()
        z_score = norm.ppf(1 - alpha)
        var_parametric = mu + sigma * z_score
        var_historical = self.returns.rolling(window=self.window).quantile(1 - alpha)

        def rolling_es(window_data):
            cutoff = window_data.quantile(1 - alpha)
            outliers = window_data[window_data <= cutoff]
            return outliers.mean()
        
        es_historical = self.returns.rolling(window=self.window).apply(rolling_es)
        return var_parametric, var_historical, es_historical

def color_pct(val):
    if isinstance(val, (int, float)):
        if val > 5:
            return "color: red"
        elif val > 2.5:
            return "color: orange"
        else:
            return "color: green"
    return ""

def obtener_datos(tickers, start="2010-01-01", end=None):
    if end is None:
        end = date.today().strftime("%Y-%m-%d")
    df = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series):
        nombre = tickers if isinstance(tickers, str) else tickers[0]
        df = df.to_frame(name=nombre)
    return df.dropna(how="all")

def calcular_rendimientos(df):
    return df.pct_change().dropna()

def render_inciso_a():
    st.header("(a) Descarga de datos")
    st.markdown(
        """
**JPMorgan Chase & Co. (NYSE: JPM)** es una de las instituciones financieras
más grandes del mundo y el banco más grande de Estados Unidos por activos.
Opera en banca de inversión, banca comercial, gestión de activos y servicios
al consumidor.

**Por qué este activo:**
- Pertenece al sector financiero, muy sensible a tasas de interés, ciclo
  económico y eventos de riesgo sistémico (crisis 2008-2009, COVID-19, ciclo
  de alzas de la Fed 2022-2023).
- Tiene historia bursátil amplia y líquida, ideal para estimar VaR, ES,
  momentos estadísticos y pruebas de normalidad.
- Su volatilidad moderada–alta lo hace un buen caso de estudio para los
  modelos paramétricos, históricos y de Monte Carlo vistos en clase.
- Yahoo Finance dispone de precios diarios desde antes de 2010, así que
  cumple con el requisito de descargar datos desde 2010.
        """
    )
    st.markdown(f"Análisis de {TICKER} desde {START}.")
    precios = obtener_datos(TICKER, start=START)
    with st.expander("Ver registros de precios"):
        st.dataframe(precios.head())
        st.dataframe(precios.tail())
    st.divider()
    return precios

def render_inciso_b(precios):
    st.header("(b) Rendimientos e indicadores estadísticos")
    rendimientos = calcular_rendimientos(precios)
    serie_rend = rendimientos[TICKER]
    media = serie_rend.mean()
    sesgo = skew(serie_rend)
    exc_curtosis = kurtosis(serie_rend)
    col1, col2, col3 = st.columns(3)
    col1.metric("Media diaria", f"{media:.6f}")
    col2.metric("Sesgo", f"{sesgo:.4f}")
    col3.metric("Exceso de curtosis", f"{exc_curtosis:.4f}")
    st.divider()
    return serie_rend

def render_inciso_c(serie_rend):
    st.header("(c) VaR y ES — Serie completa")
    alphas = [0.95, 0.975, 0.99]
    mu = serie_rend.mean()
    sigma = serie_rend.std(ddof=1)
    df_t, loc_t, scale_t = t.fit(serie_rend)
    np.random.seed(42)
    rend_simulados = np.random.normal(mu, sigma, 100000)
    resultados = {"Metodología": ["Paramétrico (Normal)", "Paramétrico (t-Student)", "Histórico", "Monte Carlo"]}
    for alpha in alphas:
        q = 1 - alpha
        z_val = norm.ppf(q)
        var_norm = -(mu + sigma * z_val)
        es_norm = -(mu - sigma * (norm.pdf(z_val) / (1 - alpha)))
        t_val = t.ppf(q, df_t)
        var_t_ = -(loc_t + scale_t * t_val)
        es_t_ = -(loc_t - scale_t * (t.pdf(t_val, df_t) / (1 - alpha)) * ((df_t + t_val**2) / (df_t - 1)))
        var_hist = -np.percentile(serie_rend, q * 100)
        es_hist = -serie_rend[serie_rend <= -var_hist].mean()
        var_mc = -np.percentile(rend_simulados, q * 100)
        es_mc = -rend_simulados[rend_simulados <= -var_mc].mean()
        resultados[f"VaR {alpha*100:g}%"] = [f"{var_norm:.4%}", f"{var_t_:.4%}", f"{var_hist:.4%}", f"{var_mc:.4%}"]
        resultados[f"ES {alpha*100:g}%"] = [f"{es_norm:.4%}", f"{es_t_:.4%}", f"{es_hist:.4%}", f"{es_mc:.4%}"]
    st.dataframe(pd.DataFrame(resultados).set_index("Metodología"), use_container_width=True)
    st.divider()

def render_inciso_d(serie_rend):
    st.sidebar.header("Configuración de Datos")
    uploaded_file = st.sidebar.file_uploader("Carga tu CSV", type="csv")
    serie_d = serie_rend
    if uploaded_file is not None:
        df_csv = pd.read_csv(uploaded_file)
        if "retornos" in df_csv.columns:
            serie_d = df_csv["retornos"].dropna()
    alpha = st.sidebar.select_slider("Confianza", options=[0.90, 0.95, 0.99], value=0.95)
    st.header("(d) VaR y ES con rolling window de 252 días")
    model = MarketRiskModel(serie_d, window=252)
    var_p, var_h, es_h = model.calculate_metrics(alpha)
    vp95, vh95, eh95 = model.calculate_metrics(0.95)
    vp99, vh99, eh99 = model.calculate_metrics(0.99)
    df_95 = pd.DataFrame({"Retorno": serie_d, "VaR_Param": vp95, "VaR_Hist": vh95, "ES_Hist": eh95}).dropna()
    df_99 = pd.DataFrame({"Retorno": serie_d, "VaR_Param": vp99, "VaR_Hist": vh99, "ES_Hist": eh99}).dropna()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(serie_d, label="Retornos", color='lightgray', alpha=0.6)
    ax.plot(var_p, label="VaR Paramétrico", color='blue', linestyle='--')
    ax.plot(var_h, label="VaR Histórico", color='orange')
    ax.plot(es_h, label="ES", color='red', linewidth=2)
    ax.legend()
    st.pyplot(fig)
    c1, c2, c3 = st.columns(3)
    c1.metric("Último VaR Param", f"{var_p.iloc[-1]:.4%}")
    c2.metric("Último VaR Hist", f"{var_h.iloc[-1]:.4%}")
    c3.metric("Último ES Hist", f"{es_h.iloc[-1]:.4%}")
    st.divider()
    return df_95, df_99

def render_inciso_e(df_95, df_99):
    st.header("(e) Backtesting — Violaciones")
    filas = []
    for a, df_r in [(0.95, df_95), (0.99, df_99)]:
        for col, med, met in [("VaR_Hist", "VaR", "Hist"), ("ES_Hist", "ES", "Hist"), ("VaR_Param", "VaR", "Param")]:
            viol = int((df_r["Retorno"] < df_r[col]).sum())
            filas.append({
                "Nivel": f"{a:.1%}", 
                "Medida": med, 
                "Método": met, 
                "Violaciones": viol, 
                "% Muestra": round(viol/len(df_r)*100, 2)
            })
    df_final = pd.DataFrame(filas)
    try:
        st.dataframe(df_final.style.map(color_pct, subset=["% Muestra"]), use_container_width=True)
    except AttributeError:
        st.dataframe(df_final.style.applymap(color_pct, subset=["% Muestra"]), use_container_width=True)
    st.divider()

def render_inciso_f(serie_rend):
    st.header("(f) VaR con volatilidad móvil")
    std_roll = serie_rend.rolling(252).std(ddof=1)
    v95 = norm.ppf(0.05) * std_roll
    v99 = norm.ppf(0.01) * std_roll
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(serie_rend, color="steelblue", alpha=0.4, label="Retornos")
    ax.plot(v95, color="red", label="VaR 95%")
    ax.plot(v99, color="darkred", linestyle="--", label="VaR 99%")
    ax.legend()
    st.pyplot(fig)
 
    # Backtesting: violaciones del VaR con volatilidad móvil
    st.subheader("Backtesting — Violaciones VaR volatilidad móvil")
    df_vol = pd.DataFrame({
        "Retorno": serie_rend,
        "VaR_95": v95,
        "VaR_99": v99
    }).dropna()
 
    filas = []
    for nivel, col in [(0.95, "VaR_95"), (0.99, "VaR_99")]:
        viol = int((df_vol["Retorno"] < df_vol[col]).sum())
        filas.append({
            "Nivel": f"{nivel:.1%}",
            "Medida": "VaR",
            "Método": "Vol. móvil (Normal)",
            "Violaciones": viol,
            "% Muestra": round(viol / len(df_vol) * 100, 2)
        })
    df_viol_f = pd.DataFrame(filas)
    try:
        st.dataframe(df_viol_f.style.map(color_pct, subset=["% Muestra"]), use_container_width=True)
    except AttributeError:
        st.dataframe(df_viol_f.style.applymap(color_pct, subset=["% Muestra"]), use_container_width=True)
    st.caption("Recordatorio: una buena estimación genera un porcentaje de violaciones menor al 2.5%.")
    st.divider()
 
def main():
    st.set_page_config(page_title="Proyecto MCF", layout="wide")
    st.title("Proyecto I – Métodos Cuantitativos en Finanzas")
    st.markdown("Integrantes: Paulina Álvarez, Vanessa Escobar, Vanessa Jiménez, Elias Santana")
    precios = render_inciso_a()
    serie_rend = render_inciso_b(precios)
    render_inciso_c(serie_rend)
    d95, d99 = render_inciso_d(serie_rend)
    render_inciso_e(d95, d99)
    render_inciso_f(serie_rend)

if __name__ == "__main__":
    main()