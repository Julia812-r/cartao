import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# ----------------- Configurações Iniciais -----------------
st.set_page_config(
    page_title="Controle de Empréstimo de Cartão GoodCard",
    layout="wide"
)

# CSS personalizado
st.markdown("""
    <style>
    .titulo-renault {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: #FFD700;
        margin-top: -40px;
    }
    section[data-testid="stSidebar"] {
        background-color: black;
        color: white;
    }
    .css-1cpxqw2, .css-qbe2hs, .css-1v0mbdj, .css-1xarl3l {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="titulo-renault">RENAULT</div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Controle de Empréstimo - GoodCard</h1>", unsafe_allow_html=True)

# ----------------- Logo na Sidebar -----------------
logo_url = "https://storage.googleapis.com/ire-74774-ope/files%2Fmigration%2Ftb_releases-5238-604.jpg"

st.sidebar.markdown(
    f"""
    <div style="text-align: center; padding: 10px 0;">
        <img src="{logo_url}" style="width: 100%; max-width: 300px; border-radius: 10px;" />
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- Funções Auxiliares -----------------
CSV_FILE = "emprestimos_goodcard.csv"

def carregar_dados():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=[
            "Nome Solicitante", "Email Solicitante", "IPN Solicitante", "Departamento",
            "Centro de Custo", "Telefone Solicitante", "Nome Supervisor", "Email Supervisor",
            "Motivo", "Previsão Devolução", "Identificação Veículo", "Concorda Regras", "Data Registro"
        ])

def salvar_dados(df):
    df.to_csv(CSV_FILE, index=False)

def adicionar_registro(novo_dado):
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    salvar_dados(df)

# ----------------- Menu Lateral -----------------
menu_opcao = st.sidebar.selectbox("Navegação", ["Formulário de Solicitação", "Registros de Empréstimos"])

# ----------------- Página: Formulário -----------------
if menu_opcao == "Formulário de Solicitação":
    st.subheader("Regras para Empréstimo e Utilização de Cartão GoodCard")

    with st.expander("Clique para ler as regras de utilização do Cartão GoodCard"):
        regras = """
A pesquisa levará aproximadamente 7 minutos para ser concluída.

### REGRAS PARA EMPRÉSTIMO E UTILIZAÇÃO DE CARTÕES COMBUSTÍVEL:
1. Para empréstimo de Cartões Combustível é necessária a aprovação do Gestor do solicitante e do Chefe do atelier DE-TV (via Flow);
2. Todo o uso particular é rigorosamente PROIBIDO;
3. O uso do Cartão Combustível deverá ser restrito aos postos homologados;
4. O uso do cartão deve ser atrelado a uma Placa vinculada a um veículo e a um período de tempo;
5. Para cartões que não possuam vínculo com Placas Verdes os gastos com combustível deverão ser comprovados através de cupons fiscais emitidos pelos postos;
6. Em caso de extravio ou roubo do cartão de abastecimento providenciar imediatamente um Boletim de Ocorrência e avisar o responsável pelos Cartões Combustível na DE-TV;
7. O período de empréstimo não deverá exceder 30 dias para empréstimos não vinculados a Placas Verdes;
8. A utilização correta do cartão é de inteira responsabilidade do solicitante, todos os gastos desvinculados a projetos Renault serão devidamente repassados ao solicitante.
9. A Devolução do Cartão Combustível deverá ocorrer imediatamente após a finalização do período de empréstimo.
10. Use com responsabilidade - Temos o controle e monitoramento dos resultados de abastecimentos.
        """
        st.markdown(regras)

    st.subheader("Formulário de Solicitação de Empréstimo")

    with st.form("form_goodcard"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo do Solicitante", placeholder="João da Silva")
            email = st.text_input("Email do Solicitante", placeholder="joao.silva@renault.com")
            ipn = st.text_input("IPN do Solicitante", placeholder="PM51532")
            departamento = st.text_input("Departamento", placeholder="DE-TR")
            centro_custo = st.text_input("Centro de Custo", placeholder="GI31000")
            telefone = st.text_input("Telefone de Contato", placeholder="41988774433")
        with col2:
            nome_sup = st.text_input("Nome Completo do Supervisor", placeholder="Mario de Andrade")
            email_sup = st.text_input("Email do Supervisor", placeholder="mario.andrade@renault.com")
            previsao = st.date_input("Previsão de Devolução", format="DD/MM/YYYY")
            identificacao = st.text_input("Identificação do Veículo", placeholder="SV6122 ou Chassi")

        motivo = st.text_area("Local e motivo da utilização", placeholder="Circuitos LPC para ensaio de durabilidade do projeto XXX")
        concorda = st.checkbox("Declaro que li e estou de acordo com as Regras para Empréstimo e Utilização de Cartão Combustível.")

        submit = st.form_submit_button("Enviar Solicitação")

        if submit:
            if not all([nome, email, ipn, departamento, centro_custo, telefone, nome_sup, email_sup, motivo, identificacao]):
                st.warning("Preencha todos os campos obrigatórios.")
            elif not concorda:
                st.warning("Você deve confirmar a leitura das regras.")
            else:
                dados = {
                    "Nome Solicitante": nome,
                    "Email Solicitante": email,
                    "IPN Solicitante": ipn,
                    "Departamento": departamento,
                    "Centro de Custo": centro_custo,
                    "Telefone Solicitante": telefone,
                    "Nome Supervisor": nome_sup,
                    "Email Supervisor": email_sup,
                    "Motivo": motivo,
                    "Previsão Devolução": previsao.strftime("%d/%m/%Y"),
                    "Identificação Veículo": identificacao,
                    "Concorda Regras": "SIM",
                    "Data Registro": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                adicionar_registro(dados)
                st.success("Solicitação registrada com sucesso.")

# ----------------- Página: Registros -----------------
elif menu_opcao == "Registros de Empréstimos":
    st.subheader("Registros de Empréstimos - Cartão GoodCard")
    df = carregar_dados()

    # Filtros
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            nome_filtro = st.text_input("Filtrar por Nome do Solicitante")
        with col2:
            veiculo_filtro = st.text_input("Filtrar por Identificação do Veículo")

        if nome_filtro:
            df = df[df["Nome Solicitante"].astype(str).str.contains(nome_filtro, case=False, na=False)]
        if veiculo_filtro:
            df = df[df["Identificação Veículo"].fillna("").astype(str).str.contains(veiculo_filtro, case=False, na=False)]

    st.markdown("### Tabela de Empréstimos")
    df_editado = st.data_editor(df, num_rows="dynamic", key="editor_goodcard")

    if not df_editado.equals(df):
        salvar_dados(df_editado)
        st.success("Alterações salvas com sucesso.")
