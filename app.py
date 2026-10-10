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
st.subheader("Controlo de Quartos com Exportação em PDF")

# Base de dados simulada de Alunos e Quartos
if 'alunos_db' not in st.session_state:
    st.session_state.alunos_db = pd.DataFrame([
        {"Numero": "101", "Nome": "Carlos Sousa", "Quarto": "Quarto 12"},
        {"Numero": "102", "Nome": "Sofia Martins", "Quarto": "Quarto 15"},
        {"Numero": "103", "Nome": "Ricardo Silva", "Quarto": "Quarto 22"},
        {"Numero": "104", "Nome": "Mariana Costa", "Quarto": "Quarto 08"},
    ])

if 'livro_registo' not in st.session_state:
    st.session_state.livro_registo = []

st.write("### 🔍 Scanner / Introdução de Dados")
num_introduzido = st.text_input("Introduza o Número do Aluno:", placeholder="Ex: 101", key="num_aluno")

col1, col2 = st.columns(2)
with col1:
    entrada = st.button("📥 Registar ENTRADA", type="primary", use_container_width=True)
with col2:
    saida = st.button("📤 Registar SAÍDA", use_container_width=True)

if (entrada or saida) and num_introduzido:
    aluno = st.session_state.alunos_db[st.session_state.alunos_db['Numero'] == num_introduzido]
    
    if not aluno.empty:
        nome_aluno = aluno.iloc['Nome']
        quarto_aluno = aluno.iloc['Quarto']
        hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipo_movimento = "ENTRADA" if entrada else "SAÍDA"
        
        st.session_state.livro_registo.append({
            "Data/Hora": hora_atual,
            "Número": num_introduzido,
            "Nome": nome_aluno,
            "Quarto": quarto_aluno,
            "Movimento": tipo_movimento
        })
        
        if entrada:
            st.success(f"✅ Registada ENTRADA de {nome_aluno} ({quarto_aluno})")
        else:
            st.warning(f"🚪 Registada SAÍDA de {nome_aluno} ({quarto_aluno})")
    else:
        st.error(f"⚠️ O número {num_introduzido} não foi encontrado.")

st.write("---")
st.write("### 📋 Livro de Registo Diário")

if st.session_state.livro_registo:
    df_registo = pd.DataFrame(st.session_state.livro_registo)
    st.dataframe(df_registo.iloc[::-1], use_container_width=True)
    
    def gerar_pdf(dados):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30, title="Relatorio_Vigilancia")
        elementos = []
        
        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle('TituloStyle', parent=estilos['Heading1'], fontSize=18, leading=22, alignment=1, spaceAfter=20)
        estilo_texto = ParagraphStyle('TextoStyle', parent=estilos['Normal'], fontSize=10, leading=12)
        estilo_cabecalho = ParagraphStyle('CabecalhoStyle', parent=estilos['Normal'], fontSize=11, leading=13, fontName="Helvetica-Bold", textColor=colors.whitesmoke)
        
        data_impressao = datetime.now().strftime("%d/%m/%Y %H:%M")
        elementos.append(Paragraph(f"<b>RELATÓRIO DE VIGILÂNCIA E ACESSOS</b><br/><font size=10>Gerado em: {data_impressao}</font>", estilo_titulo))
        elementos.append(Spacer(1, 15))
        
        dados_tabela = [[Paragraph("Data/Hora", estilo_cabecalho), Paragraph("Nº", estilo_cabecalho), Paragraph("Nome do Aluno", estilo_cabecalho), Paragraph("Quarto", estilo_cabecalho), Paragraph("Movimento", estilo_cabecalho)]]
        
        for r in dados:
            dados_tabela.append([
                Paragraph(r["Data/Hora"], estilo_texto),
                Paragraph(r["Número"], estilo_texto),
                Paragraph(r["Nome"], estilo_texto),
                Paragraph(r["Quarto"], estilo_texto),
                Paragraph(f"<b>{r['Movimento']}</b>", estilo_texto)
            ])
        
       tabela = Table(dados_tabela, colWidths=[110, 40, 180, 80, 80])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F3F4F6')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        
        elementos.append(tabela)
        doc.build(elementos)
        buffer.seek(0)
        return buffer

    col_arq1, col_arq2 = st.columns(2)
    with col_arq1:
        pdf_data = gerar_pdf(st.session_state.livro_registo)
        st.download_button(label="📄 Descarregar PDF", data=pdf_data, file_name="relatorio_acessos.pdf", mime="application/pdf", use_container_width=True)
    with col_arq2:
        csv = df_registo.to_csv(index=False).encode('utf-8')
        st.download_button(label="📊 Descarregar Excel/CSV", data=csv, file_name="registo_acessos.csv", mime="text/csv", use_container_width=True)
else:
    st.info("Nenhum movimento registado neste turno.")
