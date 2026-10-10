import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

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

st.set_page_config(
    page_title="Portaria e Quartos",
    page_icon="📝",
    layout="wide",
)

st.title("📝 Registo Automatizado de Vigilância")
st.subheader("Controlo Residencial com Estado de Limpezas e PDF")
st.write("---")

# Botão de emergência na barra lateral
if st.sidebar.button("🧹 Reiniciar Base de Dados / Limpar Cache"):
    st.session_state.clear()
    st.rerun()

# BASE DE DADOS DOS ALUNOS
if "alunos_db" not in st.session_state:
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
    st.session_state.alunos_db = pd.DataFrame(
        dados_brutos, columns=["Numero", "Nome"]
    )

if "livro_registo" not in st.session_state:
    st.session_state.livro_registo = []

# Lista de pesquisa
placeholder_pesquisa = "-- Clique para selecionar Quarto ou Nome --"
opcoes_pesquisa = [placeholder_pesquisa]
for _, row in st.session_state.alunos_db.iterrows():
    opcoes_pesquisa.append(f"{row['Numero']} | {row['Nome']}")

# --- CONSULTA RÁPIDA DE LIMPEZAS ---
st.write("### 🧹 Consulta Rápida para Equipas de Limpeza")
quarto_limpeza = st.selectbox(
    "Selecione o quarto para saber se está livre para limpar:",
    options=opcoes_pesquisa,
    key="limpeza_check",
)

if quarto_limpeza != placeholder_pesquisa:
    q_limpo = quarto_limpeza.split(" | ", 1)[0]
    historico_quarto = [
        r for r in st.session_state.livro_registo
        if r["Quarto"] == f"Quarto {q_limpo}"
    ]

    if historico_quarto:
        ultimo_movimento = historico_quarto[-1]["Movimento"]
        if ultimo_movimento == "SAÍDA":
            st.success(
                f"🟢 **PODE LIMPAR:** O aluno do Quarto {q_limpo} "
                "encontra-se **FORA DO QUARTO**."
            )
        else:
            st.error(
                f"🔴 **NÃO ENTRAR:** O aluno do Quarto {q_limpo} "
                "encontra-se atualmente **DENTRO DO QUARTO**."
            )
    else:
        st.info(f"⚪ O Quarto {q_limpo} ainda não registou movimentos nesta sessão.")

st.write("---")

# --- REGISTO EM DUAS COLUNAS ---
col_esquerda, col_direita = st.columns(2, gap="large")

with col_esquerda:
    st.write("### 🔍 Pesquisa e Entrada (Portaria)")

    if "contador_reset" not in st.session_state:
        st.session_state.contador_reset = 0

    escolha = st.selectbox(
        "Pesquise pelo Quarto ou pelo Nome do Aluno para registar:",
        options=opcoes_pesquisa,
        key=f"portaria_reg_{st.session_state.contador_reset}",
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
        aluno = st.session_state.alunos_db[
            st.session_state.alunos_db["Numero"] == quarto_escolhido
        ]

        if not aluno.empty:
            nome_aluno = aluno.iloc[0]["Nome"]
            num_quarto = aluno.iloc[0]["Numero"]
            hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            tipo_movimento = "ENTRADA" if entrada else "SAÍDA"

            st.session_state.livro_registo.append({
                "Data/Hora": hora_atual,
                "Quarto": f"Quarto {num_quarto}",
                "Nome do Aluno": nome_aluno,
                "Movimento": tipo_movimento,
            })

            st.toast(
                f"✅ Registada {tipo_movimento} para {nome_aluno}",
                icon="💾",
            )
            st.session_state.contador_reset += 1
            st.rerun()

with col_direita:
    st.write("### 🕒 Histórico do Turno")
    if st.session_state.livro_registo:
        df_visualizacao = pd.DataFrame(st.session_state.livro_registo)
        st.dataframe(
            df_visualizacao.iloc[::-1],
            use_container_width=True,
            height=250,
        )
    else:
        st.info("Nenhum movimento registado nesta sessão.")

# --- EXPORTAÇÃO DE PDF VERDADEIRO E CSV ---
st.write("---")
st.write("### ⬇️ Exportar Relatório de Final de Dia")

df_export = pd.DataFrame(
    st.session_state.livro_registo
    if st.session_state.livro_registo
    else [{
        "Data/Hora": "-",
        "Quarto": "-",
        "Nome do Aluno": "-",
        "Movimento": "-",
    }]
)

def criar_pdf(df: pd.DataFrame) -> bytes:
    """Gera um PDF verdadeiro em memória e devolve os seus bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Relatório de Portaria e Vigilância",
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
        spaceAfter=12,
    )
    estilo_celula = ParagraphStyle(
        "CelulaTabela",
        parent=estilos["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        wordWrap="CJK",
    )
    estilo_cabecalho = ParagraphStyle(
        "CabecalhoTabela",
        parent=estilo_celula,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    elementos = [
        Paragraph("RELATÓRIO DE PORTARIA E VIGILÂNCIA", estilo_titulo),
        Paragraph(
            f"<b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            estilos["Normal"],
        ),
        Spacer(1, 10 * mm),
    ]

    colunas = list(df.columns)
    dados_tabela = [[Paragraph(str(c), estilo_cabecalho) for c in colunas]]

    for linha in df.fillna("").astype(str).itertuples(index=False, name=None):
        dados_tabela.append([
            Paragraph(str(valor).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), estilo_celula)
            for valor in linha
        ])

    largura_util = landscape(A4)[0] - 30 * mm
    larguras = [
        largura_util * 0.18,
        largura_util * 0.15,
        largura_util * 0.47,
        largura_util * 0.20,
    ]

    tabela = Table(
        dados_tabela,
        colWidths=larguras,
        repeatRows=1,
        hAlign="LEFT",
    )
    comandos = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    for indice in range(1, len(dados_tabela)):
        cor_linha = "#F3F4F6" if indice % 2 == 0 else "#FFFFFF"
        comandos.append((
            "BACKGROUND", (0, indice), (-1, indice),
            colors.HexColor(cor_linha),
        ))

    tabela.setStyle(TableStyle(comandos))
    elementos.append(tabela)
    doc.build(elementos)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


pdf_bytes = criar_pdf(df_export)
csv_bytes = df_export.to_csv(index=False).encode("utf-8-sig")

col_btn_pdf, col_btn_excel = st.columns(2)
with col_btn_pdf:
    st.download_button(
        label="📄 Descarregar Relatório em PDF",
        data=pdf_bytes,
        file_name="relatorio_turno.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
with col_btn_excel:
    st.download_button(
        label="📊 Descarregar Folha Excel (CSV)",
        data=csv_bytes,
        file_name="relatorio_turno.csv",
        mime="text/csv",
        use_container_width=True,
    )
