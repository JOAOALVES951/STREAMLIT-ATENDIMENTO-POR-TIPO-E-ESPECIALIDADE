Dashboard de Atendimentos por Tipo e Especialidade

Aplicação desenvolvida em **Streamlit (Python)** para análise de atendimentos hospitalares, com foco em **performance**, **confiabilidade dos indicadores** e **facilidade de uso para o usuário final**.

O dashboard permite analisar grandes volumes de dados (testado com **+400 mil registros**) de forma interativa, com filtros dinâmicos, KPIs, tabelas e gráficos.



Objetivo do Projeto

Disponibilizar uma ferramenta de análise que permita:

- Visualizar o **volume de atendimentos únicos**
- Analisar atendimentos por **especialidade**, **tipo**, **classificação** e **convênio**
- Comparar **SUS x Não SUS**
- Acompanhar a **evolução temporal** dos atendimentos
- Garantir **consistência dos números**, mesmo com dados duplicados por linha



Regras de Negócio Implementadas

- **Atendimento único:**  
  Todos os cálculos utilizam `CD_ATENDIMENTO` como identificador único  
  > Linha ≠ Atendimento

- **Data válida:**  
  Apenas a coluna `DT_ATENDIMENTO` é utilizada para análises temporais  
  (outras colunas de data são ignoradas)

- **Classificação SUS:**  
  Convênios classificados como **SUS**:
  - `SUS-SIA`
  - `SUS-AIH`
  - `SESA PROCEDIMENTOS S/SIGTAP`  
  Todos os demais são classificados como **Não SUS**

- **Datas no formato brasileiro:**  
  `DD/MM/YYYY`

- **Normalização de texto:**  
  Acentos e variações de escrita são tratados na lógica,  
  mantendo o texto original no visual.


Estrutura Esperada do CSV

O arquivo CSV deve conter as seguintes colunas:

| Coluna | Descrição |
|------|---------|
| `CD_ATENDIMENTO` | Código único do atendimento |
| `DT_ATENDIMENTO` | Data do atendimento (DD/MM/YYYY) |
| `DS_ESPECIALID` | Especialidade |
| `NM_CONVENIO` | Convênio |
| `TP_ATENDIMENTO` | Classificação (A, U, I) |
| `TIPO` | Tipo do atendimento |

> Outras colunas podem existir no arquivo, mas não são utilizadas.

Funcionalidades do Dashboard

Filtros
- Período (data inicial e final)
- Convênio (SUS / Não SUS)
- Classificação (Ambulatorial, Urgência, Internação)
- Especialidade
- Tipo

> O filtro de período aceita **1 data ou intervalo**, sem gerar erro para o usuário.


KPIs
- Total de Atendimentos
- Média Diária
- Média Mensal
- Atendimentos SUS
- Atendimentos Não SUS
- % de Urgência



Tabela
- Top 7 especialidades com maior volume de atendimentos
- Percentual sobre o total filtrado


Gráficos
- Atendimentos por Especialidade (barra)
- Distribuição por Classificação (rosca)
- SUS x Não SUS (rosca)
- Evolução Temporal:
  - **Mensal** quando não há filtro de data
  - **Diária** quando há filtro de período



Tecnologias Utilizadas

- **Python**
- **Streamlit**
- **Pandas**
- **Plotly**




