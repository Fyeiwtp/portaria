import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Importações para gerar o PDF formatado
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Registo de Portaria e Quartos", page_icon="📝", layout="centered")

st.title("📝 Registo Automatizado de Vigilância")
st.subheader("Controlo de Quartos com Pesquisa Instantânea e PDF")
st.write("---")

# LISTA OFICIAL DE ALUNOS E QUARTOS
if 'alunos_db' not in st.session_state:
    st.session_state.alunos_db = pd.DataFrame([
        {"Numero": "1.9A", "Nome": "Safira Coelho Curado", "Quarto": "Quarto 1.9A"},
        {"Numero": "1.9B", "Nome": "Yolanta Yermakova", "Quarto": "Quarto 1.9B"},
        {"Numero": "110A", "Nome": "Iara Victoria Amorim Senra", "Quarto": "Quarto 110A"},
        {"Numero": "110B", "Nome": "Bárbara da Rocha Soares", "Quarto": "Quarto 110B"},
        {"Numero": "111A", "Nome": "Abel Cabral Costa", "Quarto": "Quarto 111A"},
        {"Numero": "111B", "Nome": "Paulo Henrique Pacheco de Sousa Duarte", "Quarto": "Quarto 111B"},
        {"Numero": "112A", "Nome": "Sizikelly Soares da Gama", "Quarto": "Quarto 112A"},
        {"Numero": "112B", "Nome": "Beatriz Mendonça da Silva", "Quarto": "Quarto 112B"},
        {"Numero": "113A", "Nome": "Afonso Luís Medeiros Freitas", "Quarto": "Quarto 113A"},
        {"Numero": "113B", "Nome": "Carolina Nunes Correia", "Quarto": "Quarto 113B"},
        {"Numero": "114A", "Nome": "Joana Natal Pinto de Magalhães", "Quarto": "Quarto 114A"},
        {"Numero": "114B", "Nome": "Luana Vitória Rodrigues Rachão Lopes", "Quarto": "Quarto 114B"},
        {"Numero": "115A", "Nome": "Júlia Beatriz Rodrigues de Freitas Pereira", "Quarto": "Quarto 115A"},
        {"Numero": "115B", "Nome": "Inês Sofia Untea Machado", "Quarto": "Quarto 115B"},
        {"Numero": "116A", "Nome": "Henrique Barbosa Pereira", "Quarto": "Quarto 116A"},
        {"Numero": "116B", "Nome": "Ricardo Barbosa Pereira", "Quarto": "Quarto 116B"},
        {"Numero": "117A", "Nome": "José Carlos Oliveira da Silva Rocha", "Quarto": "Quarto 117A"},
        {"Numero": "117B", "Nome": "Pedro Calvinho", "Quarto": "Quarto 117B"},
        {"Numero": "118A", "Nome": "Alícia Dias Marcos", "Quarto": "Quarto 118A"},
        {"Numero": "118B", "Nome": "Ema Alves da Silva Neves de Barros", "Quarto": "Quarto 118B"},
        {"Numero": "119A", "Nome": "Bruno Nunes Pereira", "Quarto": "Quarto 119A"},
        {"Numero": "119B", "Nome": "Luís Gabriel Lemos da Silva", "Quarto": "Quarto 119B"},
        {"Numero": "120A", "Nome": "Lanna Lajarin de Oliveira Costa", "Quarto": "Quarto 120A"},
        {"Numero": "120B", "Nome": "Maria Miguel Dias Mandim Lino", "Quarto": "Quarto 120B"},
        {"Numero": "121A", "Nome": "Ana Margarida Silva Ferreira", "Quarto": "Quarto 121A"},
        {"Numero": "121B", "Nome": "Núria Silva Teixeira", "Quarto": "Quarto 121B"},
        {"Numero": "122A", "Nome": "Rodrigo Sousa Mendonça", "Quarto": "Quarto 122A"},
        {"Numero": "122B", "Nome": "Duarte Nuno Dias Marques", "Quarto": "Quarto 122B"},
        {"Numero": "123A", "Nome": "Rodrigo Miguel Pacheco Talaia", "Quarto": "Quarto 123A"},
        {"Numero": "123B", "Nome": "André Brito Palma", "Quarto": "Quarto 123B"},
        {"Numero": "124A", "Nome": "Bruno Jorge Câmara Silva", "Quarto": "Quarto 124A"},
        {"Numero": "124B", "Nome": "Tiago Belchior Soares de Albergaria", "Quarto": "Quarto 124B"},
        {"Numero": "125A", "Nome": "Paulo Jorge Medeiros Alexandre", "Quarto": "Quarto 125A"},
        {"Numero": "125B", "Nome": "Mateus Oliveira", "Quarto": "Quarto 125B"},
        {"Numero": "126A", "Nome": "Pedro Soares Casado", "Quarto": "Quarto 126A"},
        {"Numero": "126B", "Nome": "Dinis Manuel Martins Santos", "Quarto": "Quarto 126B"},
        {"Numero": "127A", "Nome": "Inês Luzia Leal Fagundes", "Quarto": "Quarto 127A"},
        {"Numero": "127B", "Nome": "Ana Luísa Leite Matos", "Quarto": "Quarto 127B"},
        {"Numero": "128A", "Nome": "Vitória Skrzypietz", "Quarto": "Quarto 128A"},
        {"Numero": "128B", "Nome": "Suzana Sousa Dos Santos", "Quarto": "Quarto 128B"},
        {"Numero": "129A", "Nome": "Mafalda Ferreira Martins", "Quarto": "Quarto 129A"},
        {"Numero": "129B", "Nome": "Carolina Relva Mendonça", "Quarto": "Quarto 129B"},
        {"Numero": "130A", "Nome": "Dinis Karpov", "Quarto": "Quarto 130A"},
        {"Numero": "130B", "Nome": "João António Silveira Ramalho", "Quarto": "Quarto 130B"},
        {"Numero": "210A", "Nome": "Alice Francisca Ladeiras Caldeira", "Quarto": "Quarto 210A"},
        {"Numero": "210B", "Nome": "Camila Afonso Brás Matos Pereira", "Quarto": "Quarto 210B"},
        {"Numero": "211A", "Nome": "Tomás Miranda", "Quarto": "Quarto 211A"},
        {"Numero": "211B", "Nome": "Luis Carlos Rego Pacheco", "Quarto": "Quarto 211B"},
        {"Numero": "212A", "Nome": "Mafalda Machado Cabral", "Quarto": "Quarto 212A"},
        {"Numero": "212B", "Nome": "Soraia Filipa Andrade", "Quarto": "Quarto 212B"},
        {"Numero": "213A", "Nome": "Gabriela Nogueira Ferreira", "Quarto": "Quarto 213A"},
        {"Numero": "213B", "Nome": "Mariana Gonçalves", "Quarto": "Quarto 213B"},
        {"Numero": "214A", "Nome": "Bianca Antonio", "Quarto": "Quarto 214A"},
        {"Numero": "214B", "Nome": "Sara Sofia Vieira Cró", "Quarto": "Quarto 214B"},
        {"Numero": "215A", "Nome": "Jorge Miguel Pacheco Botelho", "Quarto": "Quarto 215A"},
        {"Numero": "215B", "Nome": "Jahyr Isney Morales Correia", "Quarto": "Quarto 215B"},
        {"Numero": "216A", "Nome": "Anastasia Belilovets", "Quarto": "Quarto 216A"},
        {"Numero": "216B", "Nome": "Gabriela Filipa Rodrigues Santos", "Quarto": "Quarto 216B"},
        {"Numero": "217A", "Nome": "Rodrigo Freitas Spínola", "Quarto": "Quarto 217A"},
        {"Numero": "217B", "Nome": "Guilherme Bento da Cruz Marques", "Quarto": "Quarto 217B"},
        {"Numero": "218A", "Nome": "Anastácia Dikovych", "Quarto": "Quarto 218A"},
        {"Numero": "218B", "Nome": "Leonor José Abreu Sousa", "Quarto": "Quarto 218B"},
        {"Numero": "219A", "Nome": "Leandro Medeiros Amaral", "Quarto": "Quarto 219A"},
        {"Numero": "219B", "Nome": "Rafael Cabral da Silva", "Quarto": "Quarto 219B"},
        {"Numero": "220A", "Nome": "Margarida Pereira", "Quarto": "Quarto 220A"},
        {"Numero": "220B", "Nome": "Carlota Oliveira Baptista Reis", "Quarto": "Quarto 220B"},
        {"Numero": "221A", "Nome": "Daniela Alexandra Marques Carreira", "Quarto": "Quarto 221A"},
        {"Numero": "221B", "Nome": "Matilde Bairos Fumo", "Quarto": "Quarto 221B"},
        {"Numero": "222A", "Nome": "Maria Elvira Basílio Canada", "Quarto": "Quarto 222A"},
        {"Numero": "222B", "Nome": "João Gonçalo Nascimento Abreu", "Quarto": "Quarto 222B"},
        {"Numero": "223A", "Nome": "Bruno Miguel Pereira Medeiros", "Quarto": "Quarto 223A"},
        {"Numero": "223B", "Nome": "Raquel Viveiros Sousa", "Quarto": "Quarto 223B"},
        {"Numero": "224A", "Nome": "Ana Cristina Marques da Silva", "Quarto": "Quarto 224A"},
        {"Numero": "224B", "Nome": "Carolina Alexandra Pereira Fernandes", "Quarto": "Quarto 224B"},
        {"Numero": "225A", "Nome": "Érica Brites Freitas", "Quarto": "Quarto 225A"},
        {"Numero": "225B", "Nome": "Maria Amália Poças", "Quarto": "Quarto 225B"},
        {"Numero": "226A", "Nome": "Jacinta Borges", "Quarto": "Quarto 226A"},
        {"Numero": "226B", "Nome": "Carlota Abreu Freitas", "Quarto": "Quarto 226B"},
        {"Numero": "227A", "Nome": "Gabrielle Cristina da Silva", "Quarto": "Quarto 227A"},
        {"Numero": "227B", "Nome": "Joana Isabel Pereira Reis Rato", "Quarto": "Quarto 227B"},
        {"Numero": "228A", "Nome": "Luana Filipa da Silva Cabral", "Quarto": "Quarto 228A"},
        {"Numero": "228B", "Nome": "Jéssica Inês Alves Teixeira", "Quarto": "Quarto 228B"},
        {"Numero": "229A", "Nome": "Maria Inês Figueiredo Bentes", "Quarto": "Quarto 229A"},
        {"Numero": "230A", "Nome": "Helena Isabel Ramos da Costa", "Quarto": "Quarto 230A"},
        {"Numero": "231A", "Nome": "Pedro Guilherme Baptista Silva", "Quarto": "Quarto 231A"},
        {"Numero": "231B", "Nome": "Duarte Carreno Novais", "Quarto": "Quarto 231B"},
    ])

if 'livro_registo' not in st.session_state:
    st.session_state.livro_registo = []

# Criar opções legíveis para a pesquisa: "Quarto X - Nome do Aluno"
opcoes_alunos = ["-- Selecione ou digite o número do quarto --"] + [
    f"Quarto {row['Numero']} - {row['Nome']}" for _, row in st.session_state.alunos_db.iterrows()
]

st.write("### 🔍 Pesquisa Instantânea de Aluno")
escolha = st.selectbox("Comece a digitar o número do quarto para pesquisar:", options=opcoes_alunos)

# Processa apenas se o vigilante tiver escolhido um aluno válido
if escolha != "-- Selecione ou digite o número do quarto --":
    # Extrair o número do quarto a partir do texto selecionado
    quarto_selecionado = escolha.split(" - ")[0].replace("Quarto ", "")
    aluno_selecionado = st.session_state.alunos_db[st.session_state.alunos_db['Numero'] == quarto_selecionado].iloc[0]
    
    nome_aluno = aluno_selecionado['Nome']
    quarto_aluno = aluno_selecionado['Quarto']
    
    # Mostrar feedback visual instantâneo do aluno selecionado
    st.info(f"👤 **Aluno Selecionado:** {nome_aluno} | 🛏️ **{quarto_aluno}**")
    
    col1, col2 = st.columns(2)
    with col1:
        entrada = st.button("📥 Registar ENTRADA", type="primary", use_container_width=True)
    with col2:
        saida = st.button("📤 Registar SAÍDA", use_container_width=True)
        
    if entrada or saida:
        hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipo_movimento = "ENTRADA" if entrada else "SAÍDA"
        
        st.session_state.livro_registo.append({
