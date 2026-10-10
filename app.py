import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Portaria e Quartos", page_icon="📝", layout="wide")

st.title("📝 Registo Automatizado de Vigilância")
st.subheader("Controlo Residencial com Exportação em PDF")
st.write("---")

# GERADOR AUTOMÁTICO DA BASE DE DADOS DE QUARTOS (Sem risco de cortes de texto)
if 'livro_registo' not in st.session_state:
    st.session_state.livro_registo = []

# Criar a estrutura em duas colunas fixas: Esquerda (Registo) e Direita (Histórico)
col_esquerda, col_direita = st.columns(2, gap="large")

with col_esquerda:
    st.write("### 🔑 Entrada de Dados")
    num_quarto = st.text_input("Introduza o Número do Quarto (Ex: 110A, 215B, 1.9A):", placeholder="Ex: 110A").strip().upper()
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        entrada = st.button("📥 Registar ENTRADA", type="primary", use_container_width=True)
    with col_btn2:
        saida = st.button("📤 Registar SAÍDA", use_container_width=True)

    if (entrada or saida) and num_quarto:
        hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipo_movimento = "ENTRADA" if entrada else "SAÍDA"
        
        # Guarda diretamente o quarto introduzido e a hora certa
        st.session_state.livro_registo.append({
            "Data/Hora": hora_atual,
            "Quarto": f"Quarto {num_quarto}",
            "Movimento": tipo_movimento
        })
        
        if entrada:
            st.success(f"✅ Registada ENTRADA para o Quarto {num_quarto} às {hora_atual}")
        else:
            st.warning(f"🚪 Registada SAÍDA para o Quarto {num_quarto} às {hora_atual}")

with col_direita:
    st.write("### 🕒 Histórico do Turno (Lado Direito)")
    if st.session_state.livro_registo:
        df_visualizacao = pd.DataFrame(st.session_state.livro_registo)
        st.dataframe(df_visualizacao.iloc[::-1], use_container_width=True, height=250)
    else:
        st.info("Nenhum movimento registado. O histórico aparecerá aqui à direita.")

# Área inferior fixa para descarregar o relatório em PDF no final do turno
st.write("---")
st.write("### ⬇️ Exportar Relatório de Final de Dia")

def gerar_pdf(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elementos = []
    estilos = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle('T', parent=estilos['Heading1'], fontSize=16, alignment=1, spaceAfter=20)
    estilo_texto = ParagraphStyle('X', parent=estilos['Normal'], fontSize=10)
    estilo_cab = ParagraphStyle('C', parent=estilos['Normal'], fontSize=11, fontName="Helvetica-Bold", textColor=colors.whitesmoke)
    
    elementos.append(Paragraph(f"<b>RELATÓRIO DE VIGILÂNCIA E PORTARIA</b><br/><font size=10>Data: {datetime.now().strftime('%d/%m/%Y')}</font>", estilo_titulo))
    elementos.append(Spacer(1, 15))
    
    dados_tab = [[Paragraph("Data/Hora", estilo_cab), Paragraph("Quarto", estilo_cab), Paragraph("Movimento", estilo_cab)]]
    
    lista_movimentos = dados if dados else [{"Data/Hora": "Sem movimentos", "Quarto": "-", "Movimento": "-"}]
    for r in lista_movimentos:
        dados_tab.append([Paragraph(r["Data/Hora"], estilo_texto), Paragraph(r["Quarto"], estilo_texto), Paragraph(f"<b>{r['Movimento']}</b>", estilo_texto)])
    
    tabela = Table(dados_tab, colWidths=[150, 150, 150])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F3F4F6')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elementos.append(tabela)
    doc.build(elementos)
    buffer.seek(0)
    return buffer

col_btn_pdf, col_btn_excel = st.columns(2)
with col_btn_pdf:
    pdf_bytes = gerar_pdf(st.session_state.livro_registo)
    st.download_button(label="📄 Descarregar Relatório em PDF", data=pdf_bytes, file_name="relatorio_turno.pdf", mime="application/pdf", use_container_width=True)
with col_btn_excel:
    df_excel = pd.DataFrame(st.session_state.livro_registo if st.session_state.livro_registo else [{"Data/Hora": "-", "Quarto": "-", "Movimento": "-"}])
    st.download_button(label="📊 Descarregar Folha Excel (CSV)", data=df_excel.to_csv(index=False).encode('utf-8'), file_name="relatorio_turno.csv", mime="text/csv", use_container_width=True)
