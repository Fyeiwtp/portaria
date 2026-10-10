import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Importação da biblioteca nativa corrigida para gerar PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Portaria e Quartos", page_icon="📝", layout="wide")

st.title("📝 Registo Automatizado de Vigilância")
st.subheader("Controlo Residencial com Estado de Limpezas e PDF")
st.write("---")

# Botão de emergência na barra lateral
if st.sidebar.button("🧹 Reiniciar Base de Dados / Limpar Cache"):
    st.session_state.clear()
    st.rerun()

# BASE DE DADOS OFICIAL DE ALUNOS E QUARTOS
if 'alunos_db' not in st.session_state:
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
        {"Numero": "225B", "Nome": "Maria Amália Poças"}, {"Numero": "226A", "Nome": "Jacinta Borges"}, {"Numero": "226B", "Nome": "Carlota Abreu Freitas"},
        {"Numero": "227A", "Nome": "Gabrielle Cristina da Silva"}, {"Numero": "227B", "Nome": "Joana Isabel Pereira Reis Rato"}, {"Numero": "228A", "Nome": "Luana Filipa da Silva Cabral"},
        {"Numero": "228B", "Nome": "Jéssica Inês Alves Teixeira"}, {"Numero": "229A", "Nome": "Maria Inês Figueiredo Bentes"}, {"Numero": "229B", "Nome": "Mariana Alves Barrinha"},
        {"Numero": "230A", "Nome": "Helena Isabel Ramos da Costa"}, {"Numero": "230B", "Nome": "Joana Margarida Paim Gregório"}, {"Numero": "231A", "Nome": "Pedro Guilherme Baptista Silva"},
        {"Numero": "231B", "Nome": "Duarte Carreno Novais"}
    ]
    st.session_state.alunos_db = pd.DataFrame(dados_brutos, columns=['Numero', 'Nome'])

if 'livro_registo' not in st.session_state:
    st.session_state.livro_registo = []

# Criar lista para a pesquisa interativa
opcoes_pesquisa = ["-- Clique para digitar Quarto ou Nome --"]
for _, row in st.session_state.alunos_db.iterrows():
    opcoes_pesquisa.append(f"{row['Numero']} | {row['Nome']}")

# --- SECÇÃO DE CONSULTA RÁPIDA DE LIMPEZAS ---
st.write("### 🧹 Consulta Rápida para Equipas de Limpeza")
quarto_limpeza = st.selectbox("Selecione o quarto para saber se está livre para limpar:", options=opcoes_pesquisa, key="limpeza_check")

if quarto_limpeza != "-- Clique para digitar Quarto ou Nome --":
    q_limpo = quarto_limpeza.split(" | ")[0]
    historico_quarto = [r for r in st.session_state.livro_registo if r["Quarto"] == f"Quarto {q_limpo}"]
    
    if historico_quarto:
        ultimo_movimento = historico_quarto[-1]["Movimento"]
        if ultimo_movimento == "SAÍDA":
            st.success(f"🟢 **PODE LIMPAR:** O aluno do Quarto {q_limpo} encontra-se **FORA DO QUARTO**.")
        else:
            st.error(f"🔴 **NÃO ENTRAR:** O aluno do Quarto {q_limpo} encontra-se atualmente **DENTRO DO QUARTO**.")
    else:
        st.info(f"⚪ O Quarto {q_limpo} ainda não registou movimentos hoje.")

st.write("---")

# --- SECÇÃO DE REGISTO EM DUAS COLUNAS FIXAS ---
col_esquerda, col_direita = st.columns(2, gap="large")

with col_esquerda:
    st.write("### 🔍 Pesquisa e Entrada (Portaria)")
    
    if "contador_reset" not in st.session_state:
        st.session_state.contador_reset = 0
        
    escolha = st.selectbox(
        "Pesquise pelo Quarto ou pelo Nome do Aluno para registar:", 
        options=opcoes_pesquisa, 
        key=f"portaria_reg_{st.session_state.contador_reset}"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        entrada = st.button("📥 Registar ENTRADA", type="primary", use_container_width=True)
    with col_btn2:
        saida = st.button("📤 Registar SAÍDA", use_container_width=True)

    if (entrada or saida) and escolha != "-- Clique para digitar Quarto ou Nome --":
        quarto_escolhido = escolha.split(" | ")[0]
        aluno = st.session_state.alunos_db[st.session_state.alunos_db['Numero'] == quarto_escolhido]
        
        if not aluno.empty:
            nome_aluno = aluno.iloc[0]['Nome']
            num_quarto = aluno.iloc[0]['Numero']
            hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            tipo_movimento = "ENTRADA" if entrada else "SAÍDA"
            
            st.session_state.livro_registo.append({
                "Data/Hora": hora_atual,
                "Quarto": f"Quarto {num_quarto}",
                "Nome do Aluno": nome_aluno,
                "Movimento": tipo_movimento
            })
            
            st.toast(f"✅ Registada {tipo_movimento} para {nome_aluno}", icon="💾")
            st.session_state.contador_reset += 1
            st.rerun()

with col_direita:
    st.write("### 🕒 Histórico do Turno (Lado Direito)")
    if st.session_state.livro_registo:
        df_visualizacao = pd.DataFrame(st.session_state.livro_registo)
        st.dataframe(df_visualizacao.iloc[::-1], use_container_width=True, height=250)
    else:
        st.info("Nenhum movimento registado neste turno.")

# --- BOTÕES DE EXPORTAÇÃO DIRETOS EM PDF ---
st.write("---")
st.write("### ⬇️ Exportar Relatório de Final de Dia")

def gerar_pdf_oficial(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elementos = []
    
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('T', parent=estilos['Heading1'], fontSize=16, alignment=1, spaceAfter=20)
    estilo_texto = ParagraphStyle('X', parent=estilos['Normal'], fontSize=10)
    estilo_cab = ParagraphStyle('C', parent=estilos['Normal'], fontSize=11, fontName="Helvetica-Bold", textColor=colors.whitesmoke)
    
    elementos.append(Paragraph(f"<b>RELATÓRIO DE VIGILÂNCIA E PORTARIA</b><br/><font size=10>Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>", estilo_titulo))
    elementos.append(Spacer(1, 15))
    
    dados_tab = [[Paragraph("Data/Hora", estilo_cab), Paragraph("Quarto", estilo_cab), Paragraph("Nome do Aluno", estilo_cab), Paragraph("Movimento", estilo_cab)]]
    
    lista_movimentos = dados if dados else [{"Data/Hora": "Sem movimentos", "Quarto": "-", "Nome do Aluno": "-", "Movimento": "-"}]
    for r in lista_movimentos:
        dados_tab.append([
            Paragraph(r.get("Data/Hora", "-"), estilo_texto),
            Paragraph(r.get("Quarto", "-"), estilo_texto),
            Paragraph(r.get("Nome do Aluno", "-"), estilo_texto),
            Paragraph(f"<b>{r.get('Movimento', '-')}</b>", estilo_texto)
        ])
    
    # Formatação das colunas fixa protegida contra quebras
    tabela = Table(dados_tab, colWidths=[120, 80, 220, 80])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F3F4F6')]),
