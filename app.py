import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Portaria e Quartos", page_icon="📝", layout="wide")

st.title("📝 Registo Automatizado de Vigilância")
st.subheader("Controlo Residencial Completo")
st.write("---")

# Botão de emergência na barra lateral para limpar a cache
if st.sidebar.button("🧹 Reiniciar Base de Dados / Limpar Cache"):
    st.session_state.clear()
    st.rerun()

# BASE DE DADOS COMPACTADA OFICIAL E CONVERTIDA
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
        ("225B", "Maria Amália Poças"), ("226A", "Jacinta Borges"), ("226B", "Carlota Abreu Freitas"),
        ("227A", "Gabrielle Cristina da Silva"), ("227B", "Joana Isabel Pereira Reis Rato"), ("228A", "Luana Filipa da Silva Cabral"),
        ("228B", "Jéssica Inês Alves Teixeira"), ("229A", "Maria Inês Figueiredo Bentes"), ("229B", "Mariana Alves Barrinha"),
        ("230A", "Helena Isabel Ramos da Costa"), ("230B", "Joana Margarida Paim Gregório"), ("231A", "Pedro Guilherme Baptista Silva"),
        ("231B", "Duarte Carreno Novais")
    ]
    st.session_state.alunos_db = pd.DataFrame(dados_brutos, columns=['Numero', 'Nome'])

if 'livro_registo' not in st.session_state:
    st.session_state.livro_registo = []

# Lista para a pesquisa interativa
opcoes_pesquisa = ["-- Clique para digitar Quarto ou Nome --"]
for _, row in st.session_state.alunos_db.iterrows():
    opcoes_pesquisa.append(f"{row['Numero']} | {row['Nome']}")

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
        partes = escolha.split(" | ")
        quarto_escolhido = partes
        nome_escolhido = partes
        
        # Formata a data e hora como um texto simples e limpo (string)
        hora_atual = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        tipo_movimento = "ENTRADA" if entrada else "SAÍDA"
        
        st.session_state.livro_registo.append({
            "Data/Hora": hora_atual,
            "Quarto": f"Quarto {quarto_escolhido}",
            "Nome do Aluno": nome_escolhido,
            "Movimento": tipo_movimento
        })
        
        st.toast(f"✅ Registada {tipo_movimento} para {nome_escolhido}", icon="💾")
        st.session_state.contador_reset += 1
        st.rerun()

with col_direita:
    st.write("### 🕒 Histórico do Turno (Lado Direito)")
    if st.session_state.livro_registo:
        df_visualizacao = pd.DataFrame(st.session_state.livro_registo)
        
        # GARANTE QUE A TABELA TRATA A HORA COMO TEXTO PARA NÃO ADICIONAR O +00
        df_visualizacao["Data/Hora"] = df_visualizacao["Data/Hora"].astype(str)
        
        st.dataframe(df_visualizacao.iloc[::-1], use_container_width=True, height=250)
    else:
        st.info("Nenhum movimento registado neste turno.")

# --- BOTÃO DE EXPORTAÇÃO SEGURO E DIRETO ---
st.write("---")
st.write("### ⬇️ Exportar Relatório de Final de Dia")

df_export = pd.DataFrame(st.session_state.livro_registo if st.session_state.livro_registo else [{"Data/Hora": "-", "Quarto": "-", "Nome do Aluno": "-", "Movimento": "-"}])
df_export["Data/Hora"] = df_export["Data/Hora"].astype(str)
csv_dados = df_export.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📊 Descarregar Relatório Completo para Excel / Impressão", 
    data=csv_dados, 
    file_name=f"relatorio_portaria_{datetime.now().strftime('%Y%m%d')}.csv", 
    mime="text/csv", 
    use_container_width=True
)
