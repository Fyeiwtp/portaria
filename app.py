import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo
import html
import time
import hmac

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    LongTable,
    TableStyle,
)

# ============================================================
# CONFIGURAÇÃO
# ============================================================
st.set_page_config(
    page_title="Portaria e Quartos",
    page_icon="📝",
    layout="wide",
)

FUSO_HORARIO = ZoneInfo("Atlantic/Azores")
BASE_DADOS = Path(__file__).with_name("portaria_registos.sqlite3")
PASTA_RELATORIOS = Path(__file__).with_name("relatorios")
PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)

# ============================================================
# ACESSO DOS FUNCIONÁRIOS
# ============================================================
FUNCIONARIOS = {
    "tiago": "Tiago Penacho",
    "pedro": "Pedro Medeiros",
    "daniel": "Daniel Picado",
    "joao": "João Botelho",
}

# Definir em Streamlit Cloud > App settings > Secrets:
# PORTARIA_PASSWORD = "123"
try:
    SENHA_PORTARIA = str(st.secrets.get("PORTARIA_PASSWORD", ""))
except Exception:
    SENHA_PORTARIA = ""

if not SENHA_PORTARIA:
    st.error("Falta configurar PORTARIA_PASSWORD nas Secrets do Streamlit Cloud.")
    st.stop()

if "funcionario_autenticado" not in st.session_state:
    st.session_state["funcionario_autenticado"] = None

if st.session_state["funcionario_autenticado"] not in FUNCIONARIOS:
    st.title("🔒 Acesso à Portaria Residencial")
    st.caption("Acesso reservado aos funcionários da portaria")
    with st.form("login_portaria"):
        utilizador = st.selectbox(
            "Funcionário", list(FUNCIONARIOS),
            format_func=lambda u: FUNCIONARIOS[u],
        )
        senha = st.text_input("Palavra-passe", type="password")
        entrar = st.form_submit_button("Entrar", type="primary")
    if entrar:
        if hmac.compare_digest(senha, SENHA_PORTARIA):
            st.session_state["funcionario_autenticado"] = utilizador
            st.rerun()
        else:
            st.error("Palavra-passe incorreta.")
    st.stop()

FUNCIONARIO_ATUAL = FUNCIONARIOS[st.session_state["funcionario_autenticado"]]
with st.sidebar:
    st.success(f"👤 {FUNCIONARIO_ATUAL}")
    if st.button("🚪 Terminar sessão", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ============================================================
# DESIGN / INTERFACE
# ============================================================
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  :root { --navy:#12213a; --blue:#2563eb; --muted:#64748b; --line:#e2e8f0; }
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stApp { background: #f4f7fb; }
  [data-testid="stHeader"] { background: rgba(244,247,251,.9); }
  .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }
  [data-testid="stSidebar"] { background: #101d33; }
  [data-testid="stSidebar"] * { color: #e7eefb !important; }
  .hero { padding: 1.55rem 1.8rem; border-radius: 22px; color: white;
          background: linear-gradient(120deg,#12213a 0%,#1e40af 62%,#3b82f6 100%);
          box-shadow: 0 14px 35px rgba(30,64,175,.18); margin-bottom: 1.25rem; }
  .hero-kicker { font-size:.78rem; text-transform:uppercase; letter-spacing:.14em; opacity:.78; font-weight:700; }
  .hero h1 { color:white; font-size:2rem; font-weight:800; margin:.35rem 0 .3rem 0; }
  .hero p { color:#e0eaff; margin:0; font-size:.98rem; }
  .section-title { color:#12213a; font-size:1.18rem; font-weight:800; margin:1.25rem 0 .7rem 0; }
  [data-testid="stMetric"] { background:white; padding:1rem 1.1rem; border:1px solid #e5eaf2;
      border-radius:16px; box-shadow:0 4px 15px rgba(15,23,42,.035); }
  [data-testid="stMetricLabel"] { color:#64748b; font-weight:600; }
  [data-testid="stMetricValue"] { color:#12213a; font-weight:800; }
  div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:16px; }
  .stButton > button, .stDownloadButton > button { border-radius:11px; font-weight:700; min-height:2.7rem; border:1px solid #dbe4f0; }
  .stButton > button[kind="primary"] { background:linear-gradient(120deg,#1d4ed8,#2563eb); border:0; }
  .stSelectbox [data-baseweb="select"] > div, .stTextInput input { border-radius:10px; }
  [data-testid="stDataFrame"] { border:1px solid #e2e8f0; border-radius:13px; overflow:hidden; }
  hr { border-color:#e1e8f0; }
  @media (max-width: 700px) { .hero { padding:1.1rem; } .hero h1 { font-size:1.5rem; } }
</style>
<div class="hero">
  <div class="hero-kicker">Gestão residencial · Portaria</div>
  <h1>Centro de controlo da portaria</h1>
  <p>Entradas e saídas, estado dos quartos e relatórios num só lugar.</p>
</div>
""", unsafe_allow_html=True)
st.caption("🔒 Os movimentos ficam guardados numa base de dados local e mantêm-se ao atualizar a página.")


# ============================================================
# BASE DE DADOS PERMANENTE
# ============================================================
def ligar_bd():
    conn = sqlite3.connect(BASE_DADOS, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_bd():
    with ligar_bd() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT NOT NULL,
                quarto TEXT NOT NULL,
                nome_aluno TEXT NOT NULL,
                movimento TEXT NOT NULL,
                periodo TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_movimentos_periodo
            ON movimentos(periodo)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS relatorios_fechados (
                periodo TEXT PRIMARY KEY,
                caminho_pdf TEXT NOT NULL,
                data_fecho TEXT NOT NULL
            )
        """)
        conn.execute("""CREATE TABLE IF NOT EXISTS correcoes_estado (
            movimento_id INTEGER PRIMARY KEY,
            motivo TEXT NOT NULL,
            FOREIGN KEY(movimento_id) REFERENCES movimentos(id)
        )""")
        # Atualização compatível com bases de dados existentes.
        colunas = {r[1] for r in conn.execute("PRAGMA table_info(movimentos)").fetchall()}
        if "funcionario" not in colunas:
            conn.execute("ALTER TABLE movimentos ADD COLUMN funcionario TEXT")
        conn.commit()


inicializar_bd()


def agora_local():
    return datetime.now(FUSO_HORARIO)


def periodo_operacional(momento=None):
    """
    O dia operacional vai das 01:00 até às 00:59:59 do dia seguinte.
    Ex.: às 00:30 de 10/10, o registo pertence ao período iniciado em 09/10.
    """
    momento = momento or agora_local()
    if momento.hour < 1:
        data_inicio = (momento - timedelta(days=1)).date()
    else:
        data_inicio = momento.date()
    return data_inicio.isoformat()


def periodo_fechado_mais_recente():
    """
    Depois das 01:00, o período que terminou é o dia operacional anterior.
    Antes das 01:00, ainda não se considera concluído o período atual.
    """
    agora = agora_local()
    if agora.hour >= 1:
        inicio_periodo_terminado = (agora - timedelta(days=1)).date()
    else:
        inicio_periodo_terminado = (agora - timedelta(days=2)).date()
    return inicio_periodo_terminado.isoformat()


def adicionar_movimento(quarto, nome, movimento):
    agora = agora_local()
    momento_texto = agora.strftime("%d/%m/%Y %H:%M:%S")
    periodo = periodo_operacional(agora)
    with ligar_bd() as conn:
        conn.execute(
            """
            INSERT INTO movimentos
            (data_hora, quarto, nome_aluno, movimento, periodo, funcionario)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (momento_texto, f"Quarto {quarto}", nome, movimento, periodo, FUNCIONARIO_ATUAL),
        )
        conn.commit()



def corrigir_estado(quarto, nome, movimento, motivo):
    """Regista uma correção auditável, sem alterar ou apagar movimentos antigos."""
    agora = agora_local()
    with ligar_bd() as conn:
        cursor = conn.execute(
            "INSERT INTO movimentos (data_hora, quarto, nome_aluno, movimento, periodo, funcionario) VALUES (?, ?, ?, ?, ?, ?)",
            (agora.strftime("%d/%m/%Y %H:%M:%S"), f"Quarto {quarto}", nome,
             movimento, periodo_operacional(agora), FUNCIONARIO_ATUAL),
        )
        conn.execute(
            "INSERT INTO correcoes_estado (movimento_id, motivo) VALUES (?, ?)",
            (cursor.lastrowid, motivo.strip()),
        )
        conn.commit()


def carregar_movimentos(periodo=None):
    with ligar_bd() as conn:
        if periodo:
            rows = conn.execute(
                """
                SELECT data_hora AS 'Data/Hora',
                       quarto AS 'Quarto',
                       nome_aluno AS 'Nome do Aluno',
                       movimento AS 'Movimento',
                       periodo AS 'Dia Operacional',
                        COALESCE(NULLIF(TRIM(funcionario), ''), '—') AS 'Vigilante',
                       CASE WHEN EXISTS (SELECT 1 FROM correcoes_estado c WHERE c.movimento_id = movimentos.id)
                            THEN 'CORREÇÃO MANUAL' ELSE 'REGISTO NORMAL' END AS 'Origem'
                FROM movimentos
                WHERE periodo = ?
                ORDER BY id ASC
                """,
                (periodo,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT data_hora AS 'Data/Hora',
                       quarto AS 'Quarto',
                       nome_aluno AS 'Nome do Aluno',
                       movimento AS 'Movimento',
                       periodo AS 'Dia Operacional',
                        COALESCE(NULLIF(TRIM(funcionario), ''), '—') AS 'Vigilante',
                       CASE WHEN EXISTS (SELECT 1 FROM correcoes_estado c WHERE c.movimento_id = movimentos.id)
                            THEN 'CORREÇÃO MANUAL' ELSE 'REGISTO NORMAL' END AS 'Origem'
                FROM movimentos
                ORDER BY id ASC
                """
            ).fetchall()
    return pd.DataFrame([dict(r) for r in rows])


def ultimo_movimento_aluno(quarto, nome):
    """Último registo deste residente, mesmo em dias operacionais anteriores."""
    with ligar_bd() as conn:
        row = conn.execute(
            """SELECT movimento, data_hora FROM movimentos
               WHERE quarto = ? AND nome_aluno = ?
               ORDER BY id DESC LIMIT 1""",
            (f"Quarto {quarto}", nome),
        ).fetchone()
    return dict(row) if row else None


def alunos_atualmente_fora(alunos):
    """Um aluno é contado uma vez, se a última movimentação for SAÍDA."""
    with ligar_bd() as conn:
        rows = conn.execute("""
            SELECT m.quarto, m.nome_aluno, m.data_hora, m.movimento
            FROM movimentos m
            INNER JOIN (
                SELECT quarto, nome_aluno, MAX(id) AS ultimo_id
                FROM movimentos GROUP BY quarto, nome_aluno
            ) ult ON ult.ultimo_id = m.id
            WHERE m.movimento = 'SAÍDA'
        """).fetchall()
    ativos = {(str(r['Numero']), str(r['Nome'])) for _, r in alunos.iterrows()}
    return [dict(r) for r in rows
            if (r['quarto'].removeprefix('Quarto '), r['nome_aluno']) in ativos]


# ============================================================
# LISTA DE ALUNOS
# ============================================================
dados_brutos = [
    ("1.9A", "Safira Coelho Curado"), ("1.9B", "Yolanta Yermakova"), ("110A", "Iara Victoria Amorim Senra"),
    ("110B", "Bárbara da Rocha Soares"), ("111A", "Abel Cabral Costa"), ("111B", "Paulo Henrique Pacheco de Sousa Duarte"),
    ("112A", "Sizikelly Soares da Gama"), ("112B", "Beatriz Mendonça da Silva"), ("113A", "Afonso Luís Medeiros Freitas"),
    ("113B", "Carolina Nunes Correia"), ("114A", "Joana Natal Pinto de Magalhães"), ("114B", "Luana Vitória Rodrigues Rachão Lopes"),
    ("115A", "Júlia Beatriz Rodrigues de Freitas Pereira"), ("115B", "Inês Sofia Untea Machado"), ("116A", "Henrique Barbosa Pereira"),
    ("116B", "Ricardo Barbosa Pereira"), ("117A", "José Carlos Oliveira da Silva Rocha"), ("117B", "Pedro Calvinho"),
    ("118A", "Alícia Dias Marcos"), ("118B", "Ema Alves da Silva Neves de Barros"), ("119A", "Bruno Nunes Pereira"),
    ("119B", "Luís Gabriel Lemos da Silva"), ("120A", "Lanna Lajarin de Oliveira Costa"), ("120B", "Maria Miguel Dias Mandim Lino"),
    ("121A", "Ana Margarida Silva Ferreira"), ("121B", "Núria Silva Teixeira"), ("122A", "Rodrigo Sousa Mendonça"),
    ("122B", "Duarte Nuno Dias Marques"), ("123A", "Rodrigo Miguel Pacheco Talaia"), ("123B", "André Brito Palma"),
    ("124A", "Bruno Jorge Câmara Silva"), ("124B", "Tiago Belchior Soares de Albergaria"), ("125A", "Paulo Jorge Medeiros Alexandre"),
    ("125B", "Mateus Oliveira"), ("126A", "Pedro Soares Casado"), ("126B", "Dinis Manuel Martins Santos"),
    ("127A", "Inês Luzia Leal Fagundes"), ("127B", "Ana Luísa Leite Matos"), ("128A", "Vitória Skrzypietz"),
    ("128B", "Suzana Sousa Dos Santos"), ("129A", "Mafalda Ferreira Martins"), ("129B", "Carolina Relva Mendonça"),
    ("130A", "Dinis Karpov"), ("130B", "João António Silveira Ramalho"), ("210A", "Alice Francisca Ladeiras Caldeira"),
    ("210B", "Camila Afonso Brás Matos Pereira"), ("211A", "Tomás Miranda"), ("211B", "Luis Carlos Rego Pacheco"),
    ("212A", "Mafalda Machado Cabral"), ("212B", "Soraia Filipa Andrade"), ("213A", "Gabriela Nogueira Ferreira"),
    ("213B", "Mariana Gonçalves"), ("214A", "Bianca Antonio"), ("214B", "Sara Sofia Vieira Cró"),
    ("215A", "Jorge Miguel Pacheco Botelho"), ("215B", "Jahyr Isney Morales Correia"), ("216A", "Anastasia Belilovets"),
    ("216B", "Gabriela Filipa Rodrigues Santos"), ("217A", "Rodrigo Freitas Spínola"), ("217B", "Guilherme Bento da Cruz Marques"),
    ("218A", "Anastácia Dikovych"), ("218B", "Leonor José Abreu Sousa"), ("219A", "Leandro Medeiros Amaral"),
    ("219B", "Rafael Cabral da Silva"), ("220A", "Margarida Pereira"), ("220B", "Carlota Oliveira Baptista Reis"),
    ("221A", "Daniela Alexandra Marques Carreira"), ("221B", "Matilde Bairos Fumo"), ("222A", "Maria Elvira Basílio Canada"),
    ("222B", "João Gonçalo Nascimento Abreu"), ("223A", "Bruno Miguel Pereira Medeiros"), ("223B", "Raquel Viveiros Sousa"),
    ("224A", "Ana Cristina Marques da Silva"), ("224B", "Carolina Alexandra Pereira Fernandes"), ("225A", "Érica Brites Freitas"),
    ("225B", "Maria Amália Poças"), ("226A", "Jacinta Borges"), ("226B", "Carlota Abreu Freitas"),
    ("227A", "Gabrielle Cristina da Silva"), ("227B", "Joana Isabel Pereira Reis Rato"), ("229A", "Luana Filipa da Silva Cabral"),
    ("229B", "Jéssica Inês Alves Teixeira"), ("228A", "Maria Inês Figueiredo Bentes"), ("228B", "Mariana Alves Barrinha"),
    ("230A", "Helena Isabel Ramos da Costa"), ("230B", "Joana Margarida Paim Gregório"), ("231A", "Pedro Guilherme Baptista Silva"),
    ("231B", "Duarte Carreno Novais"),
]
alunos_db = pd.DataFrame(dados_brutos, columns=["Numero", "Nome"])
placeholder_pesquisa = "-- Clique para selecionar Quarto ou Nome --"
opcoes_pesquisa = [placeholder_pesquisa] + [
    f"{row['Numero']} | {row['Nome']}"
    for _, row in alunos_db.iterrows()
]

# Resumo rápido do dia operacional
_df_resumo = carregar_movimentos(periodo_operacional())
_total_entradas = int((_df_resumo["Movimento"] == "ENTRADA").sum()) if not _df_resumo.empty else 0
_total_saidas = int((_df_resumo["Movimento"] == "SAÍDA").sum()) if not _df_resumo.empty else 0
_total_movimentos = len(_df_resumo)
_fora = alunos_atualmente_fora(alunos_db)
st.markdown('<div class="section-title">Visão geral de hoje</div>', unsafe_allow_html=True)
_m1, _m2, _m3, _m4 = st.columns(4)
_m1.metric("Quartos na lista", len(alunos_db))
_m2.metric("Movimentos hoje", _total_movimentos)
_m3.metric("Entradas", _total_entradas)
_m4.metric("Alunos fora", len(_fora))
st.write("")


# ============================================================
# PDF VERDADEIRO
# ============================================================
def criar_pdf(df, titulo_relatorio, periodo, intervalo_calendario=False):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=titulo_relatorio,
        author="Sistema de Portaria",
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloRelatorio",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    estilo_celula = ParagraphStyle(
        "CelulaTabela",
        parent=estilos["BodyText"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9,
        splitLongWords=True,
    )
    estilo_cabecalho = ParagraphStyle(
        "CabecalhoTabela",
        parent=estilo_celula,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    elementos = [
        Paragraph(html.escape(titulo_relatorio), estilo_titulo),
        Paragraph(
            (f"<b>Datas selecionadas:</b> {html.escape(periodo)} (00:00 às 23:59)"
             if intervalo_calendario else
             f"<b>Período operacional:</b> {html.escape(periodo)} (01:00 até 00:59 do dia seguinte)"),
            estilos["Normal"],
        ),
        Paragraph(
            f"<b>Data de emissão:</b> {agora_local().strftime('%d/%m/%Y %H:%M:%S')}",
            estilos["Normal"],
        ),
        Spacer(1, 7 * mm),
    ]

    colunas = ["Data/Hora", "Quarto", "Nome do Aluno", "Movimento", "Origem", "Vigilante"]
    dados = [[Paragraph(c, estilo_cabecalho) for c in colunas]]

    if df.empty:
        dados.append([
            Paragraph("-", estilo_celula),
            Paragraph("-", estilo_celula),
            Paragraph("Sem movimentos registados neste período.", estilo_celula),
            Paragraph("-", estilo_celula),
            Paragraph("-", estilo_celula),
            Paragraph("-", estilo_celula),
        ])
    else:
        df_pdf = df[colunas].fillna("")
        for linha in df_pdf.astype(str).itertuples(index=False, name=None):
            dados.append([
                Paragraph(html.escape(valor), estilo_celula)
                for valor in linha
            ])

    largura_util = landscape(A4)[0] - 24 * mm
    larguras = [
        largura_util * 0.16,
        largura_util * 0.10,
        largura_util * 0.29,
        largura_util * 0.12,
        largura_util * 0.15,
        largura_util * 0.18,
    ]
    tabela = LongTable(
        dados, colWidths=larguras, repeatRows=1, hAlign="LEFT",
        splitByRow=1, longTableOptimize=1,
    )
    comandos = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(dados)):
        cor = "#F3F4F6" if i % 2 == 0 else "#FFFFFF"
        comandos.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(cor)))
    tabela.setStyle(TableStyle(comandos))
    elementos.append(tabela)

    # Uma página vertical contínua: a altura acompanha a quantidade de registos.
    # O PDF padrão limita o tamanho da página; para relatórios excecionalmente
    # extensos, conserva-se a paginação para não perder qualquer movimento.
    largura_pagina = landscape(A4)[0]
    _, altura_tabela = tabela.wrap(largura_util, 1000000)
    altura_cabecalho = 125  # título, datas, emissão e espaçamento
    altura_necessaria = altura_tabela + altura_cabecalho + 24 * mm
    limite_pagina = 14000  # pontos; compatível com leitores PDF habituais
    if altura_necessaria <= limite_pagina:
        doc.pagesize = (largura_pagina, max(landscape(A4)[1], altura_necessaria))
        doc._calc()
    else:
        doc.pagesize = landscape(A4)
        doc._calc()

    def numerar_paginas(canvas, documento):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawRightString(documento.pagesize[0] - 12 * mm, 7 * mm,
                               f"Página {documento.page}")
        canvas.restoreState()

    doc.build(elementos, onFirstPage=numerar_paginas,
              onLaterPages=numerar_paginas)

    resultado = buffer.getvalue()
    buffer.close()
    return resultado


def caminho_pdf_periodo(periodo):
    return PASTA_RELATORIOS / f"relatorio_portaria_{periodo}.pdf"


def periodo_ja_fechado(periodo):
    with ligar_bd() as conn:
        row = conn.execute(
            "SELECT caminho_pdf FROM relatorios_fechados WHERE periodo = ?",
            (periodo,),
        ).fetchone()
    return dict(row) if row else None


def fechar_periodo(periodo):
    """
    Cria e arquiva o PDF do período, sem duplicar fechos.
    Esta função é executada quando a aplicação está ativa depois das 01:00
    ou quando o utilizador abre a secção de fechos.
    """
    existente = periodo_ja_fechado(periodo)
    if existente and Path(existente["caminho_pdf"]).exists():
        return Path(existente["caminho_pdf"])

    df = carregar_movimentos(periodo)
    pdf = criar_pdf(df, "RELATÓRIO DE PORTARIA E VIGILÂNCIA", periodo)
    destino = caminho_pdf_periodo(periodo)
    destino.write_bytes(pdf)

    with ligar_bd() as conn:
        conn.execute(
            """
            INSERT INTO relatorios_fechados (periodo, caminho_pdf, data_fecho)
            VALUES (?, ?, ?)
            ON CONFLICT(periodo) DO UPDATE SET
                caminho_pdf = excluded.caminho_pdf,
                data_fecho = excluded.data_fecho
            """,
            (periodo, str(destino), agora_local().isoformat()),
        )
        conn.commit()
    return destino


# ============================================================
# FECHO DIÁRIO À 01:00
# ============================================================
agora = agora_local()
if agora.hour >= 1:
    periodo_para_fechar = (agora.date() - timedelta(days=1)).isoformat()
    try:
        fechar_periodo(periodo_para_fechar)
    except Exception as exc:
        st.warning(f"Não foi possível criar o relatório automático: {exc}")

# ============================================================
# CONSULTA DE PRESENÇA DOS RESIDENTES
# ============================================================
st.markdown('<div class="section-title">🏠 Consultar se o aluno está dentro ou fora</div>', unsafe_allow_html=True)
consulta_aluno = st.selectbox(
    "Selecione ou pesquise o quarto ou nome do aluno:",
    options=opcoes_pesquisa,
    key="consulta_presenca",
)
if consulta_aluno != placeholder_pesquisa:
    q_consulta = consulta_aluno.split(" | ", 1)[0]
    nome_consulta = str(alunos_db.loc[alunos_db["Numero"] == q_consulta, "Nome"].iloc[0])
    ultimo = ultimo_movimento_aluno(q_consulta, nome_consulta)
    if ultimo is None:
        st.info(f"⚪ **{nome_consulta} — Quarto {q_consulta}:** sem registos. Estado desconhecido.")
    elif ultimo["movimento"] == "SAÍDA":
        st.warning(f"🟠 **{nome_consulta} — Quarto {q_consulta}: FORA da residência**")
        st.caption(f"Última saída: {ultimo['data_hora']}")
    else:
        st.success(f"🟢 **{nome_consulta} — Quarto {q_consulta}: DENTRO da residência**")
        st.caption(f"Última entrada: {ultimo['data_hora']}")

st.markdown('<div class="section-title">🛠️ Corrigir estado do aluno</div>', unsafe_allow_html=True)
with st.expander("Corrigir presença quando uma entrada ou saída não foi observada"):
    st.caption("Use apenas depois de confirmar a situação. A correção fica registada no histórico com data, hora e motivo.")
    with st.form("form_corrigir_estado"):
        aluno_corrigir = st.selectbox("Aluno ou quarto", opcoes_pesquisa, key="aluno_corrigir")
        estado_corrigido = st.radio("Estado confirmado", ["FORA", "DENTRO"], horizontal=True)
        motivo_corrigido = st.text_input("Motivo da correção (obrigatório)", placeholder="Ex.: saída confirmada pelo responsável de turno")
        confirmar_correcao = st.form_submit_button("Guardar correção", type="primary")
    if confirmar_correcao:
        if aluno_corrigir == placeholder_pesquisa:
            st.error("Escolha um aluno.")
        elif not motivo_corrigido.strip():
            st.error("Indique o motivo da correção.")
        else:
            q = aluno_corrigir.split(" | ", 1)[0]
            n = str(alunos_db.loc[alunos_db["Numero"] == q, "Nome"].iloc[0])
            mov = "SAÍDA" if estado_corrigido == "FORA" else "ENTRADA"
            anterior = ultimo_movimento_aluno(q, n)
            if anterior and anterior["movimento"] == mov:
                st.warning(f"O último registo já indica {estado_corrigido}. Não foi criada uma correção duplicada.")
            else:
                corrigir_estado(q, n, mov, motivo_corrigido)
                st.success("Correção guardada e estado atualizado.")
                st.rerun()

st.markdown('<div class="section-title">🚶 Alunos atualmente fora da residência</div>', unsafe_allow_html=True)
if _fora:
    df_fora = pd.DataFrame([{
        "Quarto": r["quarto"],
        "Nome do Aluno": r["nome_aluno"],
        "Hora da última saída": r["data_hora"],
    } for r in _fora])
    st.dataframe(df_fora, use_container_width=True, hide_index=True)
else:
    st.info("Não há alunos com uma saída pendente de entrada.")
st.caption("Estados baseados nos registos e correções introduzidos; podem diferir da presença real. Sem registos, o estado é desconhecido.")

st.write("---")

# ============================================================
# REGISTO DE ENTRADAS E SAÍDAS
# ============================================================
col_esquerda, col_direita = st.columns(2, gap="large")

with col_esquerda:
    st.markdown('<div class="section-title">🔍 Registo de entradas e saídas</div>', unsafe_allow_html=True)
    # Duas listas pesquisáveis: cada campo mostra apenas o seu valor.
    # Os identificadores internos permitem distinguir nomes completos repetidos.
    mapa_quartos = {
        str(r["Numero"]).strip().upper(): str(r["Nome"]).strip()
        for _, r in alunos_db.iterrows()
    }
    vazio_quarto = "-- Selecionar quarto --"
    vazio_nome = "-- Selecionar aluno --"
    opcoes_quartos = [vazio_quarto] + list(mapa_quartos)
    opcoes_nomes = [vazio_nome] + sorted(
        mapa_quartos, key=lambda q: (mapa_quartos[q].casefold(), q)
    )

    from collections import Counter
    contagem_nomes = Counter(n.casefold() for n in mapa_quartos.values())

    def mostrar_nome(quarto):
        if quarto == vazio_nome:
            return vazio_nome
        nome = mapa_quartos[quarto]
        # Só mostra o quarto quando existem nomes completos iguais.
        if contagem_nomes[nome.casefold()] > 1:
            return f"{nome} ({quarto})"
        return nome

    def atualizar_pelo_quarto():
        quarto = st.session_state.get("registo_pesquisa_quarto", vazio_quarto)
        st.session_state["registo_pesquisa_nome"] = (
            quarto if quarto in mapa_quartos else vazio_nome
        )

    def atualizar_pelo_nome():
        quarto = st.session_state.get("registo_pesquisa_nome", vazio_nome)
        st.session_state["registo_pesquisa_quarto"] = (
            quarto if quarto in mapa_quartos else vazio_quarto
        )

    st.selectbox(
        "🔢 Número do quarto",
        options=opcoes_quartos,
        key="registo_pesquisa_quarto",
        on_change=atualizar_pelo_quarto,
        help="Clica e escreve o número do quarto para filtrar sem Enter.",
    )
    st.selectbox(
        "👤 Nome do aluno",
        options=opcoes_nomes,
        format_func=mostrar_nome,
        key="registo_pesquisa_nome",
        on_change=atualizar_pelo_nome,
        help="Clica e escreve o nome para filtrar sem Enter.",
    )
    # O texto digitado no filtro do selectbox não constitui uma seleção.
    # Só se considera o aluno confirmado após clicar numa sugestão.
    quarto_escolhido = st.session_state.get("registo_pesquisa_quarto")
    nome_escolhido = st.session_state.get("registo_pesquisa_nome")
    if quarto_escolhido in mapa_quartos and nome_escolhido != quarto_escolhido:
        st.warning("Seleciona uma sugestão da lista para confirmar o aluno e sincronizar o quarto.")
        quarto_escolhido = None
    if quarto_escolhido not in mapa_quartos:
        quarto_escolhido = None

    # Callbacks dos botões correm antes da criação dos widgets no novo rerun.
    # É seguro limpar os dois selectboxes aqui (não depois de st.button).
    def registar_e_limpar(tipo):
        quarto = st.session_state.get("registo_pesquisa_quarto")
        nome_id = st.session_state.get("registo_pesquisa_nome")
        if quarto not in mapa_quartos or nome_id != quarto:
            st.session_state["aviso_registo"] = (
                "warning", "Seleciona um aluno na lista antes de registar."
            )
            return

        nome_aluno = mapa_quartos[quarto]
        ultimo = ultimo_movimento_aluno(quarto, nome_aluno)
        if ultimo and ultimo["movimento"] == tipo:
            st.session_state["aviso_registo"] = (
                "warning", f"{nome_aluno} já tem uma {tipo} como último registo. Não foi duplicada."
            )
            return

        try:
            adicionar_movimento(quarto, nome_aluno, tipo)
        except Exception as exc:
            st.session_state["aviso_registo"] = (
                "error", f"Não foi possível guardar o registo: {exc}"
            )
            return

        st.session_state["registo_pesquisa_quarto"] = vazio_quarto
        st.session_state["registo_pesquisa_nome"] = vazio_nome
        st.session_state["aviso_registo"] = (
            "success", f"{tipo} registada para {nome_aluno} (Quarto {quarto})."
        )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button(
            "📥 Registar ENTRADA",
            type="primary",
            use_container_width=True,
            on_click=registar_e_limpar,
            args=("ENTRADA",),
        )
    with col_btn2:
        st.button(
            "📤 Registar SAÍDA",
            use_container_width=True,
            on_click=registar_e_limpar,
            args=("SAÍDA",),
        )

    aviso = st.session_state.pop("aviso_registo", None)
    if aviso:
        tipo_aviso, mensagem = aviso
        if tipo_aviso == "success":
            st.success(mensagem)
        elif tipo_aviso == "warning":
            st.warning(mensagem)
        else:
            st.error(mensagem)

with col_direita:
    st.markdown('<div class="section-title">🕒 Histórico de movimentos</div>', unsafe_allow_html=True)
    periodo_atual = periodo_operacional()
    df_atual = carregar_movimentos(periodo_atual)
    if not df_atual.empty:
        st.dataframe(
            df_atual[["Data/Hora", "Quarto", "Nome do Aluno", "Movimento", "Origem", "Vigilante"]].iloc[::-1],
            use_container_width=True,
            height=400,
        )
    else:
        st.info("Nenhum movimento registado no período operacional atual.")

# ============================================================
# RELATÓRIOS E EXPORTAÇÕES
# ============================================================
st.write("---")
st.markdown('<div class="section-title">⬇️ Relatórios e exportações</div>', unsafe_allow_html=True)

st.caption("Escolhe o dia anterior ou um intervalo de datas. O PDF inclui movimentos entre as 00:00 da primeira data e as 23:59 da última.")

hoje = agora_local().date()
ontem = hoje - timedelta(days=1)
col_inicio, col_fim = st.columns(2)
with col_inicio:
    data_inicio = st.date_input("📅 Data inicial", value=ontem, format="DD/MM/YYYY", key="relatorio_inicio")
with col_fim:
    data_fim = st.date_input("📅 Data final", value=ontem, format="DD/MM/YYYY", key="relatorio_fim")

if data_inicio > data_fim:
    st.error("A data inicial não pode ser posterior à data final.")
else:
    df_todos = carregar_movimentos()
    if df_todos.empty:
        df_export = pd.DataFrame(columns=["Data/Hora", "Quarto", "Nome do Aluno", "Movimento", "Origem", "Vigilante"])
    else:
        # A base de dados conserva a data como DD/MM/AAAA HH:MM:SS, por vezes com fuso no fim.
        # Converter apenas os 19 primeiros caracteres permite consultar registos antigos e novos.
        datas_movimentos = pd.to_datetime(
            df_todos["Data/Hora"].astype(str).str.slice(0, 19),
            format="%d/%m/%Y %H:%M:%S", errors="coerce"
        )
        filtro = (datas_movimentos.dt.date >= data_inicio) & (datas_movimentos.dt.date <= data_fim)
        df_export = df_todos.loc[filtro, ["Data/Hora", "Quarto", "Nome do Aluno", "Movimento", "Origem", "Vigilante"]].copy()
        df_export["_ordem"] = datas_movimentos.loc[filtro]
        df_export = df_export.sort_values("_ordem", kind="stable").drop(columns="_ordem")

    rotulo = f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    st.info(f"📋 {len(df_export)} movimento(s) encontrado(s) de {rotulo}.")
    if not df_export.empty:
        with st.expander("👁️ Ver movimentos deste período"):
            st.dataframe(df_export, use_container_width=True, hide_index=True)

    pdf_bytes = criar_pdf(df_export, "RELATÓRIO DE PORTARIA E VIGILÂNCIA", rotulo, intervalo_calendario=True)
    csv_bytes = df_export.to_csv(index=False).encode("utf-8-sig")
    nome_intervalo = f"{data_inicio.isoformat()}_a_{data_fim.isoformat()}"
    col_pdf, col_csv = st.columns(2)
    with col_pdf:
        st.download_button(
            "📄 Descarregar PDF das datas selecionadas",
            data=pdf_bytes,
            file_name=f"relatorio_portaria_{nome_intervalo}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col_csv:
        st.download_button(
            "📊 Descarregar CSV das datas selecionadas",
            data=csv_bytes,
            file_name=f"relatorio_portaria_{nome_intervalo}.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.caption("Podes descarregar os relatórios PDF e CSV acima. Os registos continuam guardados no sistema.")

# Não existe botão de apagar os movimentos nesta versão, para evitar perda acidental.
st.sidebar.write("---")
st.sidebar.info(
    "Os registos são guardados no ficheiro portaria_registos.sqlite3. "
    "Faça cópias de segurança desse ficheiro regularmente."
)
