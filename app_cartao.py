import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
from urllib.request import urlopen
import firebase_admin
from firebase_admin import credentials, firestore

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

# ----------------- Firebase -----------------
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()
COLLECTION_NAME = "emprestimos_goodcard"

# ----------------- Funções Auxiliares -----------------
def carregar_dados():
    docs = db.collection(COLLECTION_NAME).stream()
    data = [doc.to_dict() for doc in docs]
    if data:
        df = pd.DataFrame(data)
        # Mantém o ID do Firestore
        for i, doc in enumerate(db.collection(COLLECTION_NAME).stream()):
            df.at[i, "Firestore_ID"] = doc.id
        return df
    else:
        return pd.DataFrame(columns=[
            "Nome Solicitante", "Email Solicitante", "IPN Solicitante", "Departamento",
            "Centro de Custo", "Telefone Solicitante", "Nome Supervisor", "Email Supervisor",
            "Motivo", "Previsão Devolução", "Identificação Veículo", "Concorda Regras", "Data Registro",
            "Cartão", "Data Devolução Real", "Firestore_ID"
        ])

def salvar_dados(df):
    for _, row in df.iterrows():
        row_dict = row.to_dict()

        # Converte datas
        for col in ["Previsão Devolução", "Data Devolução Real", "Data Registro"]:
            if pd.isnull(row_dict.get(col)):
                row_dict[col] = None
            elif isinstance(row_dict[col], pd.Timestamp):
                row_dict[col] = row_dict[col].to_pydatetime()

        # Pega o ID do Firestore (se existir)
        doc_id = row_dict.get("Firestore_ID")
        
        # Se doc_id for inválido ou vazio, cria novo documento
        if not doc_id or pd.isna(doc_id):
            doc_ref = db.collection(COLLECTION_NAME).add(row_dict)
            df.at[_, "Firestore_ID"] = doc_ref[1].id
        else:
            db.collection(COLLECTION_NAME).document(str(doc_id)).set(row_dict)


def adicionar_registro(novo_dado):
    for col in ["Previsão Devolução", "Data Devolução Real", "Data Registro"]:
        if col in novo_dado and isinstance(novo_dado[col], pd.Timestamp):
            novo_dado[col] = novo_dado[col].to_pydatetime()
    doc_ref = db.collection(COLLECTION_NAME).add(novo_dado)
    novo_dado["Firestore_ID"] = doc_ref[1].id

# ----------------- Título -----------------
st.markdown('<div class="titulo-renault">RENAULT</div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Controle de Empréstimo - GoodCard</h1>", unsafe_allow_html=True)

# ----------------- Logo na Sidebar -----------------
try:
    logo_url = "https://storage.googleapis.com/ire-74774-ope/files%2Fmigration%2Ftb_releases-5238-604.jpg"
    logo = Image.open(urlopen(logo_url))
    st.sidebar.image(logo, use_container_width=True)
except Exception as e:
    st.sidebar.write("Erro ao carregar a logo:", e)

# ----------------- Menu Lateral -----------------
menu_opcao = st.sidebar.selectbox("Navegação", ["Formulário de Solicitação", "Registros de Empréstimos"])

# ----------------- Página: Formulário -----------------
if menu_opcao == "Formulário de Solicitação":
    st.subheader("Regras para Empréstimo e Utilização de Cartão GoodCard")
    with st.expander("Clique para ler as regras de utilização do Cartão GoodCard"):
        st.markdown("""
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
        """)

    st.subheader("Formulário de Solicitação de Empréstimo")
    with st.form("form_goodcard"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo do Solicitante")
            email = st.text_input("Email do Solicitante")
            ipn = st.text_input("IPN do Solicitante")
            departamento = st.text_input("Departamento")
            centro_custo = st.text_input("Centro de Custo")
            telefone = st.text_input("Telefone de Contato")
        with col2:
            nome_sup = st.text_input("Nome Completo do Supervisor")
            email_sup = st.text_input("Email do Supervisor")
            previsao = st.date_input("Previsão de Devolução")
            identificacao = st.text_input("Identificação do Veículo")
        motivo = st.text_area("Local e motivo da utilização")
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
                    "Previsão Devolução": previsao,
                    "Identificação Veículo": identificacao,
                    "Concorda Regras": "SIM",
                    "Data Registro": datetime.now(),
                    "Cartão": "",
                    "Data Devolução Real": None
                }
                adicionar_registro(dados)
                st.success("Solicitação registrada com sucesso.")

# ----------------- Página: Registros -----------------
elif menu_opcao == "Registros de Empréstimos":
    st.subheader("Área Protegida - Registros de Empréstimos")
    senha_correta = "renault2025"
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        senha_entrada = st.text_input("🔐 Digite a senha para acessar os registros:", type="password")
        if senha_entrada == senha_correta:
            st.session_state["autenticado"] = True
            st.success("Acesso autorizado com sucesso.")
        elif senha_entrada:
            st.error("Senha incorreta. Tente novamente.")
        else:
            st.info("Digite a senha para visualizar os registros.")

    if st.session_state["autenticado"]:
        df = carregar_dados()
        df["Previsão Devolução"] = pd.to_datetime(df["Previsão Devolução"], errors='coerce')
        df["Data Devolução Real"] = pd.to_datetime(df["Data Devolução Real"], errors='coerce')

        def calcular_status(row):
            hoje = datetime.now().date()
            if pd.notnull(row["Data Devolução Real"]):
                return "Devolvido"
            elif pd.notnull(row["Previsão Devolução"]) and hoje > row["Previsão Devolução"].date():
                return "Atrasado"
            else:
                return "Em aberto"

        df["Status"] = df.apply(calcular_status, axis=1)

        col1, col2, col3 = st.columns(3)
        nome_filtro = col1.text_input("Filtrar por Nome do Solicitante")
        veiculo_filtro = col2.text_input("Filtrar por Identificação do Veículo")
        status_filtro = col3.multiselect("Filtrar por Status", options=df["Status"].unique().tolist(), default=df["Status"].unique().tolist())

        if nome_filtro:
            df = df[df["Nome Solicitante"].astype(str).str.contains(nome_filtro, case=False, na=False)]
        if veiculo_filtro:
            df = df[df["Identificação Veículo"].fillna("").astype(str).str.contains(veiculo_filtro, case=False, na=False)]
        if status_filtro:
            df = df[df["Status"].isin(status_filtro)]

        df_exibicao = df.copy()
        df_exibicao["Previsão Devolução"] = df_exibicao["Previsão Devolução"].dt.strftime("%d/%m/%Y").fillna("")
        df_exibicao["Data Devolução Real"] = df_exibicao["Data Devolução Real"].dt.strftime("%d/%m/%Y").fillna("")

        ordem_colunas = [
            "Status", "Previsão Devolução", "Data Devolução Real",
            "Nome Solicitante", "Email Solicitante", "Departamento", "IPN Solicitante", "Centro de Custo",
            "Telefone Solicitante", "Nome Supervisor", "Email Supervisor", "Motivo",
            "Identificação Veículo", "Cartão", "Data Registro", "Firestore_ID"
        ]
        for col in ordem_colunas:
            if col not in df_exibicao.columns:
                df_exibicao[col] = ""

        df_exibicao = df_exibicao[ordem_colunas]

        df_editavel = st.data_editor(
            df_exibicao,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_emprestimos",
            disabled=["Status"],
        )

        if not df_editavel.equals(df_exibicao):
            df_editavel["Previsão Devolução"] = pd.to_datetime(df_editavel["Previsão Devolução"], errors='coerce')
            df_editavel["Data Devolução Real"] = pd.to_datetime(df_editavel["Data Devolução Real"], errors='coerce')
            salvar_dados(df_editavel)

