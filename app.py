import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo
import html
import time

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

st.title("📝 Registo Automatizado de Vigilância")
st.subheader("Controlo Residencial com registos permanentes, limpeza e PDF")
st.caption("Os movimentos são guardados numa base de dados local e não desaparecem ao atualizar a página.")
st.write("---")


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
    momento_texto = agora.strftime("%d/%m/%Y %H:%M:%S %Z")
    periodo = periodo_operacional(agora)
    with ligar_bd() as conn:
        conn.execute(
            """
            INSERT INTO movimentos
            (data_hora, quarto, nome_aluno, movimento, periodo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (momento_texto, f"Quarto {quarto}", nome, movimento, periodo),
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
                       periodo AS 'Dia Operacional'
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
                       periodo AS 'Dia Operacional'
                FROM movimentos
                ORDER BY id ASC
                """
            ).fetchall()
    return pd.DataFrame([dict(r) for r in rows])


def ultimo_movimento_quarto(quarto):
    with ligar_bd() as conn:
        row = conn.execute(
            """
            SELECT movimento, data_hora
            FROM movimentos
            WHERE quarto = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (f"Quarto {quarto}",),
        ).fetchone()
    return dict(row) if row else None


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
    ("227A", "Gabrielle Cristina da Silva"), ("227B", "Joana Isabel Pereira Reis Rato"), ("228A", "Luana Filipa da Silva Cabral"),
    ("228B", "Jéssica Inês Alves Teixeira"), ("229A", "Maria Inês Figueiredo Bentes"), ("229B", "Mariana Alves Barrinha"),
    ("230A", "Helena Isabel Ramos da Costa"), ("230B", "Joana Margarida Paim Gregório"), ("231A", "Pedro Guilherme Baptista Silva"),
    ("231B", "Duarte Carreno Novais"),
]
alunos_db = pd.DataFrame(dados_brutos, columns=["Numero", "Nome"])
placeholder_pesquisa = "-- Clique para selecionar Quarto ou Nome --"
opcoes_pesquisa = [placeholder_pesquisa] + [
    f"{row['Numero']} | {row['Nome']}"
    for _, row in alunos_db.iterrows()
]


# ============================================================
# PDF VERDADEIRO
# ============================================================
def criar_pdf(df, titulo_relatorio, periodo):
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
            f"<b>Período operacional:</b> {html.escape(periodo)} "
            f"(01:00 até 00:59 do dia seguinte)",
            estilos["Normal"],
        ),
        Paragraph(
            f"<b>Data de emissão:</b> {agora_local().strftime('%d/%m/%Y %H:%M:%S %Z')}",
            estilos["Normal"],
        ),
        Spacer(1, 7 * mm),
    ]

    colunas = ["Data/Hora", "Quarto", "Nome do Aluno", "Movimento"]
    dados = [[Paragraph(c, estilo_cabecalho) for c in colunas]]

    if df.empty:
        dados.append([
            Paragraph("-", estilo_celula),
            Paragraph("-", estilo_celula),
            Paragraph("Sem movimentos registados neste período.", estilo_celula),
            Paragraph("-", estilo_celula),
        ])
    else:
        df_pdf = df[["Data/Hora", "Quarto", "Nome do Aluno", "Movimento"]].fillna("")
        for linha in df_pdf.astype(str).itertuples(index=False, name=None):
            dados.append([
                Paragraph(html.escape(valor), estilo_celula)
                for valor in linha
            ])

    largura_util = landscape(A4)[0] - 24 * mm
    larguras = [
        largura_util * 0.20,
        largura_util * 0.15,
        largura_util * 0.45,
        largura_util * 0.20,
    ]
    tabela = Table(dados, colWidths=larguras, repeatRows=1, hAlign="LEFT")
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
    doc.build(elementos)

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
# CONSULTA RÁPIDA PARA LIMPEZAS
# ============================================================
st.write("### 🧹 Consulta Rápida para Equipas de Limpeza")
quarto_limpeza = st.selectbox(
    "Selecione o quarto para saber se está livre para limpar:",
    options=opcoes_pesquisa,
    key="limpeza_check",
)

if quarto_limpeza != placeholder_pesquisa:
    q_limpo = quarto_limpeza.split(" | ", 1)[0]
    ultimo = ultimo_movimento_quarto(q_limpo)

    if ultimo:
        if ultimo["movimento"] == "SAÍDA":
            st.success(
                f"🟢 **PODE LIMPAR:** O último movimento do Quarto {q_limpo} "
                "foi uma SAÍDA."
            )
        else:
            st.error(
                f"🔴 **NÃO ENTRAR:** O último movimento do Quarto {q_limpo} "
                "foi uma ENTRADA."
            )
        st.caption(f"Último movimento: {ultimo['data_hora']}")
    else:
        st.info(f"⚪ O Quarto {q_limpo} ainda não tem movimentos registados.")

st.write("---")

# ============================================================
# REGISTO DE ENTRADAS E SAÍDAS
# ============================================================
col_esquerda, col_direita = st.columns(2, gap="large")

with col_esquerda:
    st.write("### 🔍 Pesquisa e Entrada (Portaria)")
    escolha = st.selectbox(
        "Pesquise pelo Quarto ou pelo Nome do Aluno para registar:",
        options=opcoes_pesquisa,
        key="portaria_reg",
    )
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        entrada = st.button(
            "📥 Registar ENTRADA",
            type="primary",
            use_container_width=True,
        )
    with col_btn2:
        saida = st.button(
            "📤 Registar SAÍDA",
            use_container_width=True,
        )

    if (entrada or saida) and escolha != placeholder_pesquisa:
        quarto_escolhido = escolha.split(" | ", 1)[0]
        aluno = alunos_db[alunos_db["Numero"] == quarto_escolhido]
        if not aluno.empty:
            nome_aluno = str(aluno.iloc[0]["Nome"])
            tipo = "ENTRADA" if entrada else "SAÍDA"
            adicionar_movimento(quarto_escolhido, nome_aluno, tipo)
            st.success(f"Registada {tipo} para {nome_aluno}.")
            st.rerun()
    elif (entrada or saida) and escolha == placeholder_pesquisa:
        st.warning("Selecione primeiro um quarto/aluno.")

with col_direita:
    st.write("### 🕒 Histórico de Movimentos")
    periodo_atual = periodo_operacional()
    df_atual = carregar_movimentos(periodo_atual)
    if not df_atual.empty:
        st.dataframe(
            df_atual[["Data/Hora", "Quarto", "Nome do Aluno", "Movimento"]].iloc[::-1],
            use_container_width=True,
            height=300,
        )
    else:
        st.info("Nenhum movimento registado no período operacional atual.")

# ============================================================
# RELATÓRIOS E EXPORTAÇÕES
# ============================================================
st.write("---")
st.write("### ⬇️ Exportar Relatórios")

periodos_df = carregar_movimentos()
periodos_disponiveis = sorted(
    periodos_df["Dia Operacional"].dropna().unique().tolist(),
    reverse=True,
) if not periodos_df.empty else []

if periodos_disponiveis:
    periodo_escolhido = st.selectbox(
        "Escolha o dia operacional para descarregar:",
        options=periodos_disponiveis,
        index=0,
    )
else:
    periodo_escolhido = periodo_operacional()
    st.info("Ainda não existem movimentos guardados. Pode descarregar um relatório vazio.")

df_export = carregar_movimentos(periodo_escolhido)
df_export_tabela = (
    df_export[["Data/Hora", "Quarto", "Nome do Aluno", "Movimento"]]
    if not df_export.empty
    else pd.DataFrame([{
        "Data/Hora": "-",
        "Quarto": "-",
        "Nome do Aluno": "-",
        "Movimento": "-",
    }])
)

pdf_bytes = criar_pdf(df_export_tabela, "RELATÓRIO DE PORTARIA E VIGILÂNCIA", periodo_escolhido)
csv_bytes = df_export_tabela.to_csv(index=False).encode("utf-8-sig")

col_pdf, col_csv = st.columns(2)
with col_pdf:
    st.download_button(
        "📄 Descarregar PDF do dia selecionado",
        data=pdf_bytes,
        file_name=f"relatorio_portaria_{periodo_escolhido}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with col_csv:
    st.download_button(
        "📊 Descarregar CSV do dia selecionado",
        data=csv_bytes,
        file_name=f"relatorio_portaria_{periodo_escolhido}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# Fechos arquivados
st.write("---")
st.write("### 🗂️ Relatórios automáticos arquivados")
st.caption(
    "O fecho é feito quando a aplicação está em execução e é executada depois das 01:00. "
    "Para garantir o fecho mesmo com a aplicação desligada, é necessário agendar uma tarefa "
    "no servidor/PC ou usar um serviço de agendamento."
)

with ligar_bd() as conn:
    fechados = conn.execute(
        """
        SELECT periodo, caminho_pdf, data_fecho
        FROM relatorios_fechados
        ORDER BY periodo DESC
        """
    ).fetchall()

if fechados:
    for item in fechados:
        caminho = Path(item["caminho_pdf"])
        col_info, col_download = st.columns([3, 1])
        with col_info:
            st.write(f"**Dia operacional:** {item['periodo']}")
            st.caption(f"Fechado em: {item['data_fecho']}")
        with col_download:
            if caminho.exists():
                st.download_button(
                    "📥 Descarregar",
                    data=caminho.read_bytes(),
                    file_name=caminho.name,
                    mime="application/pdf",
                    key=f"download_{item['periodo']}",
                    use_container_width=True,
                )
else:
    st.info("Ainda não existem relatórios automáticos arquivados.")

# Não existe botão de apagar os movimentos nesta versão, para evitar perda acidental.
st.sidebar.write("---")
st.sidebar.info(
    "Os registos são guardados no ficheiro portaria_registos.sqlite3. "
    "Faça cópias de segurança desse ficheiro e da pasta relatorios."
)
