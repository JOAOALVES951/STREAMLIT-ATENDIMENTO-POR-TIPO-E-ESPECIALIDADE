import streamlit as st
import pandas as pd
import unicodedata
import plotly.express as px

# =============================
# CONFIGURAÇÃO DA PÁGINA
# =============================
st.set_page_config(
    page_title="ATENDIMENTO POR TIPO E ESPECIALIDADE",
    layout="wide"
)

st.title("ATENDIMENTO POR TIPO E ESPECIALIDADE")
st.caption("Análise de atendimentos ambulatoriais, urgência e internação")

# =============================
# FUNÇÕES AUXILIARES
# =============================
def normalizar(txt):
    if pd.isna(txt):
        return None
    txt = unicodedata.normalize("NFD", str(txt))
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return txt.upper().strip()

@st.cache_data(show_spinner=True)
def carregar_csv(arquivo):
    # Leitura robusta de encoding
    try:
        df = pd.read_csv(arquivo, sep=";", dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(arquivo, sep=";", dtype=str, encoding="latin-1")

    # Normaliza nomes das colunas
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.normalize("NFD")
        .str.replace(r"[\u0300-\u036f]", "", regex=True)
    )

    # =============================
    # COLUNAS REAIS DO CSV
    # =============================
    # CD_ATENDIMENTO
    # DT_ATENDIMENTO  (DATA VÁLIDA)
    # DS_ESPECIALID   (ESPECIALIDADE)
    # NM_CONVENIO
    # TP_ATENDIMENTO (A / U / I)
    # TIPO
    # DATA            -> NÃO USAR
    # CD_ORI_ATE      -> NÃO USAR

    # Parse da data BR (USA SOMENTE DT_ATENDIMENTO)
    df["DATA"] = pd.to_datetime(
        df["DT_ATENDIMENTO"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df = df.dropna(subset=["DATA"])

    # Atendimento único
    df["ATENDIMENTO"] = df["CD_ATENDIMENTO"]

    # Especialidade
    df["ESPECIALIDADE_ORIGINAL"] = df["DS_ESPECIALID"]
    df["ESPECIALIDADE_NORM"] = df["DS_ESPECIALID"].apply(normalizar)

    # Tipo
    df["TIPO_ORIGINAL"] = df["TIPO"]
    df["TIPO_NORM"] = df["TIPO"].apply(normalizar)

    # Classificação
    df["CLASSIFICACAO"] = df["TP_ATENDIMENTO"].apply(normalizar)

    # Regra SUS / NÃO SUS
    SUS_VALIDOS = {
        "SUS-SIA",
        "SUS-AIH",
        "SESA PROCEDIMENTOS S/SIGTAP"
    }

    df["CONVENIO_CLASS"] = df["NM_CONVENIO"].apply(
        lambda x: "SUS" if normalizar(x) in SUS_VALIDOS else "NAO SUS"
    )

    return df

# =============================
# UPLOAD CSV
# =============================
arquivo = st.file_uploader("Carregar arquivo CSV", type=["csv"])

if not arquivo:
    st.info("Faça o upload do arquivo CSV para iniciar.")
    st.stop()

df = carregar_csv(arquivo)

# =============================
# SIDEBAR - FILTROS
# =============================
st.sidebar.header("Filtros")

data_min = df["DATA"].min().date()
data_max = df["DATA"].max().date()

periodo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

# Tratamento para 1 ou 2 datas
if isinstance(periodo, tuple):
    if len(periodo) == 2:
        data_ini, data_fim = periodo
    else:
        data_ini = data_fim = periodo[0]
else:
    data_ini = data_fim = periodo

convenios = st.sidebar.multiselect(
    "Convênio",
    options=sorted(df["CONVENIO_CLASS"].unique()),
    default=sorted(df["CONVENIO_CLASS"].unique())
)

classif = st.sidebar.multiselect(
    "Classificação",
    options=["A", "U", "I"],
    default=["A", "U", "I"]
)

especialidades = st.sidebar.multiselect(
    "Especialidade",
    options=sorted(df["ESPECIALIDADE_ORIGINAL"].dropna().unique())
)

tipos = st.sidebar.multiselect(
    "Tipo",
    options=sorted(df["TIPO_ORIGINAL"].dropna().unique())
)

# =============================
# APLICA FILTROS
# =============================
df_f = df[
    (df["DATA"] >= pd.to_datetime(data_ini)) &
    (df["DATA"] <= pd.to_datetime(data_fim)) &
    (df["CONVENIO_CLASS"].isin(convenios)) &
    (df["CLASSIFICACAO"].isin(classif))
]

if especialidades:
    df_f = df_f[df_f["ESPECIALIDADE_ORIGINAL"].isin(especialidades)]

if tipos:
    df_f = df_f[df_f["TIPO_ORIGINAL"].isin(tipos)]

# =============================
# KPIs (ATENDIMENTO ÚNICO)
# =============================
total = df_f["ATENDIMENTO"].nunique()

dias = df_f["DATA"].dt.date.nunique()
media_dia = total / dias if dias else 0

meses = df_f["DATA"].dt.to_period("M").nunique()
media_mes = total / meses if meses else 0

sus = df_f[df_f["CONVENIO_CLASS"] == "SUS"]["ATENDIMENTO"].nunique()
nao_sus = total - sus

urg = df_f[df_f["CLASSIFICACAO"] == "U"]["ATENDIMENTO"].nunique()
pct_urg = (urg / total * 100) if total else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Total de Atendimentos", f"{total:,}".replace(",", "."))
c2.metric("Média Diária", f"{media_dia:.1f}")
c3.metric("Média Mensal", f"{media_mes:.0f}")
c4.metric("SUS", f"{sus:,}".replace(",", "."))
c5.metric("Não SUS", f"{nao_sus:,}".replace(",", "."))
c6.metric("% Urgência", f"{pct_urg:.1f}%")

st.divider()

# =============================
# TABELA TOP 7
# =============================
st.subheader("Top 7 Especialidades com Mais Atendimentos")

top7 = (
    df_f.groupby("ESPECIALIDADE_ORIGINAL")["ATENDIMENTO"]
    .nunique()
    .sort_values(ascending=False)
    .head(7)
    .reset_index(name="Total")
)

top7["% do Total"] = (top7["Total"] / total * 100).round(1)

st.dataframe(top7, use_container_width=True)

st.divider()

# =============================
# GRÁFICO - ESPECIALIDADE
# =============================
fig_esp = px.bar(
    top7,
    x="ESPECIALIDADE_ORIGINAL",
    y="Total",
    title="Atendimentos por Especialidade"
)
st.plotly_chart(fig_esp, use_container_width=True)

# =============================
# GRÁFICOS - CLASSIFICAÇÃO E CONVÊNIO
# =============================
c7, c8 = st.columns(2)

with c7:
    classif_df = (
        df_f.groupby("CLASSIFICACAO")["ATENDIMENTO"]
        .nunique()
        .reset_index(name="Total")
    )

    classif_df["CLASSIFICAÇÃO"] = classif_df["CLASSIFICACAO"].map({
        "A": "Ambulatorial",
        "U": "Urgência",
        "I": "Internação"
    })

    fig_class = px.pie(
        classif_df,
        names="CLASSIFICAÇÃO",
        values="Total",
        title="Distribuição por Classificação",
        hole=0.4
    )
    st.plotly_chart(fig_class, use_container_width=True)

with c8:
    conv_df = (
        df_f.groupby("CONVENIO_CLASS")["ATENDIMENTO"]
        .nunique()
        .reset_index(name="Total")
    )

    fig_conv = px.pie(
        conv_df,
        names="CONVENIO_CLASS",
        values="Total",
        title="SUS x Não SUS",
        hole=0.4
    )
    st.plotly_chart(fig_conv, use_container_width=True)

st.divider()

# =============================
# GRÁFICO TEMPORAL INTELIGENTE
# =============================
st.subheader("Evolução dos Atendimentos")

if data_ini == data_min and data_fim == data_max:
    # Visão mensal
    temp = (
        df_f.groupby(df_f["DATA"].dt.to_period("M"))["ATENDIMENTO"]
        .nunique()
        .reset_index()
    )
    temp["DATA"] = temp["DATA"].astype(str)
    eixo_x = "DATA"
else:
    # Visão diária
    temp = (
        df_f.groupby(df_f["DATA"].dt.date)["ATENDIMENTO"]
        .nunique()
        .reset_index()
    )
    eixo_x = "DATA"

fig_temp = px.line(
    temp,
    x=eixo_x,
    y="ATENDIMENTO",
    markers=True
)

st.plotly_chart(fig_temp, use_container_width=True)

st.caption(f"Registros carregados: {len(df):,}".replace(",", "."))
