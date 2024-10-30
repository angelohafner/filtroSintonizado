
# Simulação de Filtro Sintonizado

Este projeto é uma aplicação desenvolvida em Python com a biblioteca Streamlit para simulação de um filtro sintonizado em sistemas elétricos.

## Funcionalidades

- **Parâmetros Personalizáveis**: Download e upload de um arquivo de parâmetros (`parameters.txt`) que permite editar valores como frequência, resistência, indutância, capacitância, e outros parâmetros do filtro.
- **Cálculo e Formatação de Resultados**: Realiza cálculos de impedância, corrente, e tensão para cada componente (resistor, indutor e capacitor) do filtro.
- **Detalhes de Capacitores e Indutor**: Calcula as propriedades nominais das células do capacitor e a corrente de curto-circuito do indutor.
- **Exportação de Resultados**: Salva os resultados calculados em três formatos: JSON, TXT e XLSX, permitindo o download dos arquivos.

## Como Usar

1. **Download do Arquivo de Parâmetros**: Clique no botão para baixar o arquivo `parameters.txt` com os valores padrão.
2. **Edição e Upload dos Parâmetros**: Após editar os valores no arquivo `parameters.txt`, faça o upload do arquivo editado.
3. **Cálculo e Visualização de Resultados**: A aplicação exibirá os resultados formatados e os disponibilizará para download em JSON, TXT e XLSX.

## Requisitos

- **Python 3.7+**
- Bibliotecas:
    - `streamlit`
    - `openpyxl`
    - `numpy`
    - `pandas`
    - `json`
    - `io`
    - `matplotlib`

Instale as dependências executando:

```bash
pip install streamlit openpyxl numpy pandas matplotlib
```

## Como Executar

Execute o aplicativo Streamlit com o seguinte comando:

```bash
streamlit run app.py
```

**Nota**: Substitua `app.py` pelo nome do arquivo onde o código foi salvo.

## Estrutura do Projeto

- **app.py**: Código principal do aplicativo.
- **parameters.txt**: Arquivo de parâmetros padrão para configuração.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo de licença para mais detalhes.
