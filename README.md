# Análise de Dados da Saúde Pública de Santa Maria/RS (RAG 2024)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?style=for-the-badge&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-purple?style=for-the-badge&logo=pandas)

Análise e visualização de dados da saúde pública de Santa Maria/RS, com base no Relatório Anual de Gestão (RAG) de 2024. O projeto inclui dashboards interativos sobre casos de Dengue e repasses financeiros para a Enfermagem.

---
## ⚙️ Como Usar

Para executar este projeto localmente, siga os passos abaixo.

### Pré-requisitos

* [Python 3.10](https://www.python.org/downloads/) ou superior
* [Git](https://git-scm.com/)

### Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/leowaechter/analise-rag-sm.git](https://github.com/leowaechter/analise-rag-sm.git)
    cd analise-rag-sm
    ```

2.  **Crie e ative um ambiente virtual:**

    * **No Linux/macOS:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

    * **No Windows:**
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute os dashboards:**
    * Para o dashboard de Dengue:
        ```bash
        cd dengue_sm/
        streamlit run dashboard_dengue_sm.py
        ```
    * Para o dashboard de Repasses da Enfermagem:
        ```bash
        cd pgto_enfermagem/
        streamlit run dashboard_pgto_enf.py
        ```
---

## 📊 Fonte dos Dados

Os dados foram extraídos do [Relatório Anual de Gestão (RAG) de 2024](pdfs/relatorio-anual-de-gestao-2024-rag.pdf) da Secretaria de Saúde de Santa Maria/RS.

---
