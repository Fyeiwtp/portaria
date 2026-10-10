import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Importações para gerar o PDF formatado de forma segura
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Portaria e Quartos", page_icon="📝", layout="wide")

st.title("📝 Registo Automatizado de Vigilância")
st.subheader("Controlo Residencial com Estado de Limpezas e PDF")
st.write("---")

# BASE DE DADOS OFICIAL COMPLETA E CORRIGIDA SEM ERROS DE TEXTO
if 'alunos_db' not in st.session_state:
    st.session_state.alunos_db = pd.DataFrame([
        {"Numero": "1.9A", "Nome": "Safira Coelho Curado"},
        {"Numero": "1.9B", "Nome": "Yolanta Yermakova"},
        {"Numero": "110A", "Nome": "Iara Victoria Amorim Senra"},
        {"Numero": "110B", "Nome": "Bárbara da Rocha Soares"},
        {"Numero": "111A", "Nome": "Abel Cabral Costa"},
        {"Numero": "111B", "Nome": "Paulo Henrique Pacheco de Sousa Duarte"},
        {"Numero": "112A", "Nome": "Sizikelly Soares da Gama"},
        {"Numero": "112B", "Nome": "Beatriz Mendonça da Silva"},
        {"Numero": "113A", "Nome": "Afonso Luís Medeiros Freitas"},
        {"Numero": "113B", "Nome": "Carolina Nunes Correia"},
        {"Numero": "114A", "Nome": "Joana Natal Pinto de Magalhães"},
        {"Numero": "114B", "Nome": "Luana Vitória Rodrigues Rachão Lopes"},
        {"Numero": "115A", "Nome": "Júlia Beatriz Rodrigues de Freitas Pereira"},
        {"Numero": "115B", "Nome": "Inês Sofia Untea Machado"},
        {"Numero": "116A", "Nome": "Henrique Barbosa Pereira"},
        {"Numero": "116B", "Nome": "Ricardo Barbosa Pereira"},
        {"Numero": "117A", "Nome": "José Carlos Oliveira da Silva Rocha"},
        {"Numero": "117B", "Nome": "Pedro Calvinho"},
        {"Numero": "118A", "Nome": "Alícia Dias Marcos"},
        {"Numero": "118B", "Nome": "Ema Alves da Silva Neves de Barros"},
        {"Numero": "119A", "Nome": "Bruno Nunes Pereira"},
        {"Numero": "119B", "Nome": "Luís Gabriel Lemos da Silva"},
        {"Numero": "120A", "Nome": "Lanna Lajarin de Oliveira Costa"},
        {"Numero": "120B", "Nome": "Maria Miguel Dias Mandim Lino"},
        {"Numero": "121A", "Nome": "Ana Margarida Silva Ferreira"},
        {"Numero": "121B", "Nome": "Núria Silva Teixeira"},
        {"Numero": "122A", "Nome": "Rodrigo Sousa Mendonça"},
        {"Numero": "122B", "Nome": "Duarte Nuno Dias Marques"},
        {"Numero": "123A", "Nome": "Rodrigo Miguel Pacheco Talaia"},
        {"Numero": "123B", "Nome": "André Brito Palma"},
        {"Numero": "124A", "Nome": "Bruno Jorge Câmara Silva"},
        {"Numero": "124B", "Nome": "Tiago Belchior Soares de Albergaria"},
        {"Numero": "125A", "Nome": "Paulo Jorge Medeiros Alexandre"},
        {"Numero": "125B", "Nome": "Mateus Oliveira"},
        {"Numero": "126A", "Nome": "Pedro Soares Casado"},
        {"Numero": "126B", "Nome": "Dinis Manuel Martins Santos"},
        {"Numero": "127A", "Nome": "Inês Luzia Leal Fagundes"},
        {"Numero": "127B", "Nome": "Ana Luísa Leite Matos"},
        {"Numero": "128A", "Nome": "Vitória Skrzypietz"},
        {"Numero": "128B", "Nome": "Suzana Sousa Dos Santos"},
        {"Numero": "129A", "Nome": "Mafalda Ferreira Martins"},
        {"Numero": "129B", "Nome": "Carolina Relva Mendonça"},
        {"Numero": "130A", "Nome": "Dinis Karpov"},
        {"Numero": "130B", "Nome": "João António Silveira Ramalho"},
        {"Numero": "210A", "Nome": "Alice Francisca Ladeiras Caldeira"},
        {"Numero": "210B", "Nome": "Camila Afonso Brás Matos Pereira"},
        {"Numero": "211A", "Nome": "Tomás Miranda"},
        {"Numero": "211B", "Nome": "Luis Carlos Rego Pacheco"},
        {"Numero": "212A", "Nome": "Mafalda Machado Cabral"},
        {"Numero": "212B", "Nome": "Soraia Filipa Andrade"},
        {"Numero": "213A", "Nome": "Gabriela Nogueira Ferreira"},
        {"Numero": "213B", "Nome": "Mariana Gonçalves"},
        {"Numero": "214A", "Nome": "Bianca Antonio"},
        {"Numero": "214B", "Nome": "Sara Sofia Vieira Cró"},
        {"Numero": "215A", "Nome": "Jorge Miguel Pacheco Botelho"},
        {"Numero": "215B", "Nome": "Jahyr Isney Morales Correia"},
        {"Numero": "216A", "Nome": "Anastasia Belilovets"},
        {"Numero": "216B", "Nome": "Gabriela Filipa Rodrigues Santos"},
        {"Numero": "217A", "Nome": "Rodrigo Freitas Spínola"},
        {"Numero": "217B", "Nome": "Guilherme Bento da Cruz Marques"},
        {"Numero": "218A", "Nome": "Anastácia Dikovych"},
        {"Numero": "218B", "Nome": "Leonor José Abreu Sousa"},
        {"Numero": "219A", "Nome": "Leandro Medeiros Amaral"},
        {"Numero": "219B", "Nome": "Rafael Cabral da Silva"},
        {"Numero": "220A", "Nome": "Margarida Pereira"},
        {"Numero": "220B", "Nome": "Carlota Oliveira Baptista Reis"},
        {"Numero": "221A", "Nome": "Daniela Alexandra Marques Carreira"},
        {"Numero": "221B", "Nome": "Matilde Bairos Fumo"},
        {"Numero": "222A", "Nome": "Maria Elvira Basílio Canada"},
        {"Numero": "222B", "Nome": "João Gonçalo Nascimento Abreu"},
        {"Numero": "223A", "Nome": "Bruno Miguel Pereira Medeiros"},
        {"Numero": "223B", "Nome": "Raquel Viveiros Sousa"},
        {"Numero": "224A", "Nome": "Ana Cristina Marques da Silva"},
        {"Numero": "224B", "Nome": "Carolina Alexandra Pereira Fernandes"},
        {"Numero": "225A", "Nome": "Érica Brites Freitas"},
        {"Numero": "225B", "Nome": "Maria Amália Poças"},
        {"Numero": "226A", "Nome": "Jacinta Borges"},
        {"Numero": "226B", "Nome": "Carlota Abreu Freitas"},
        {"Numero": "227A", "Nome": "Gabrielle Cristina da Silva"},
        {"Numero": "227B", "Nome": "Joana Isabel Pereira Reis Rato"},
        {"Numero": "228A", "Nome": "Luana Filipa da Silva Cabral"},
        {"Numero": "228B", "Nome": "Jéssica Inês Alves Teixeira"},
        {"Numero": "229A", "Nome": "Maria Inês Figueiredo Bentes"},
        {"Numero": "229B", "Nome": "Mariana Alves Barrinha"},
        {"Numero": "230A", "Nome": "Helena Isabel Ramos da Costa"},
        {"Numero": "230B", "Nome": "Joana Margarida Paim Gregório"},
        {"Numero": "231A", "Nome": "Pedro Guilherme Baptista Silva"},
        {"Numero": "231B", "Nome": "Duarte Carreno Novais"}
    ])

if 'livro_registo' not in st.session_state:
    st.session_state.livro_registo = []

# Criar lista organizada para o menu de pesquisa interativa
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
            st.success(f"🟢 **PODE LIMPAR:** O aluno do Quarto {q_limpo} encontra-se **FORA DO QUARTO** (Saída às {historico_quarto[-1]['Data/Hora']}).")
        else:
            st.error(f"🔴 **NÃO ENTRAR:** O aluno do Quarto {q_limpo} encontra-se atualmente **DENTRO DO QUARTO**.")
    else:
        st.info(f"⚪ O Quarto {q_limpo} ainda não registou movimentos hoje. Confirme na portaria.")

st.write("---")

# --- SECÇÃO DE REGISTO EM DUAS COLUNAS FIXAS ---
col_esquerda, col_direita = st.columns(2, gap="large")

with col_esquerda:
    st.write("### 🔍 Pesquisa e Entrada (Portaria)")
    escolha = st.selectbox("Pesquise pelo Quarto ou pelo Nome do Aluno para registar:", options=opcoes_pesquisa, key="portaria_reg")
    
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
            st.success(f"✅ Registada {tipo_movimento} para {nome_aluno} ({num_quarto})")
            st.rerun()

with col_direita:
    st.write("### 🕒 Histórico do Turno (Lado Direito)")
    if st.session_state.livro_registo:
        df_visualizacao = pd.DataFrame(st.session_state.livro_registo)
        st.dataframe(df_visualizacao.iloc[::-1], use_container_width=True, height=250)
    else:
        st.info("Nenhum movimento registado neste turno.")

# --- BOTÃO DO PDF OFICIAL ATIVADO E FIXO ---
st.write("---")
st.write("### ⬇️ Exportar Relatório de Final de Dia")

def gerar_pdf(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elementos = []
    estilos = getSampleStyleSheet()
    
