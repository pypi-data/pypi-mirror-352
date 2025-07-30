# 📚 Documentação LuxorASAP

> Guia do desenvolvedor para os subpacotes **datareader**, **ingest**, **btgapi** e **utils**.
>
> • Instalação rápida  • Visão arquitetural  • APIs detalhadas  • Exemplos de uso  • Extras opcional

---

## Índice

1. [Visão Geral](#visao-geral)
2. [Instalação](#instalacao)
3. [utils](#utils)
4. [datareader](#datareader)
5. [ingest](#ingest)
6. [btgapi](#btgapi)
7. [Roadmap & Contribuições](#roadmap)

---

## 1. Visão Geral

LuxorASAP é o *toolbox* unificado da Luxor para ingestão, consulta e automação de dados financeiros.

| Subpacote      | Função‑chave                                                          | Extras PyPI            |
| -------------- | --------------------------------------------------------------------- | ---------------------- |
| **utils**      | Utilidades puras (I/O ADLS, transformação de DataFrame, decorators)   | `storage`, `dataframe` |
| **datareader** | Consulta de preços/tabelas no data lake via `LuxorQuery`              | `datareader`           |
| **ingest**     | Carga de dados nova (parquet/zip/excel) em ADLS + loader legado       | `ingest`               |
| **btgapi**     | Wrapper autenticado para as APIs do BTG Pactual (relatórios & trades) | `btgapi`               |

---

## 2. Instalação

```bash
# core + leitura de dados
pip install luxorasap[datareader]

# tudo incluído (leitura, ingest, btg)
pip install luxorasap[datareader,ingest,btgapi]

# desenvolvimento
pip install -e ".[dev]"
```

Extras podem ser combinados à vontade (`luxorasap[storage]`, etc.).

Configuração obrigatória do **ADLS**:

```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=..."
```

---

## 3. utils

Camada de utilidades **sem dependências internas**.

### 3.1 storage.BlobParquetClient

```python
from luxorasap.utils.storage import BlobParquetClient
client = BlobParquetClient(container="luxorasap")

# write
client.write_df(df, "bronze/parquet/mytable.parquet")

# read (tuple -> DataFrame, success_flag)
df, ok = client.read_df("bronze/parquet/mytable.parquet")
```

### 3.2 dataframe

```python
from luxorasap.utils.dataframe import prep_for_save, persist_column_formatting, read_bytes

df2 = prep_for_save(df, index=True, index_name="ID", normalize=True)
```

### 3.3 decorators & misc

`with_retry`, `chunkify`, `timer`… ficam em *utils.helpers* (caso precise).

---

## 4. datareader

### 4.1 Visão rápida

```python
from luxorasap.datareader import LuxorQuery
lq = LuxorQuery()

# DataFrame completo
df = lq.get_table("assets")

# Série de preços diária
aapl = lq.get_prices("aapl us equity", start="2025-01-01", end="2025-03-31")

# Preço pontual
price = lq.get_price("aapl us equity", on="2025-03-31")
```

*Caching*: `@lru_cache(maxsize=32)` evita hits repetidos ao Blob.

### 4.2 Métodos-chave

| Método                                          | Descrição                     |
| ----------------------------------------------- | ----------------------------- |
| `table_exists(name)`                            | checa metadados no ADLS       |
| `get_table(name)`                               | DataFrame completo (cached)   |
| `get_prices(asset, start, end, column="Price")` | `pd.Series`                   |
| `get_price(asset, on)`                          | preço pontual (float ou None) |

---

## 5. ingest

### 5.1 ingest.cloud (novo)

```python
from luxorasap.ingest import save_table, incremental_load
from luxorasap.datareader import LuxorQuery

save_table("trades", df)

lq = LuxorQuery()
incremental_load(lq, "prices_daily", df_new, increment_column="Date")
```

### 5.2 ingest.legacy\_local

```python
from luxorasap.ingest import DataLoader   # Deprecado – ainda funcional
```

*Decoration*: ao importar `DataLoader` você verá `DeprecationWarning`.

---

## 6. btgapi

### 6.1 Autenticação

```python
from luxorasap.btgapi import get_access_token
TOKEN = get_access_token(test_env=True)
```

### 6.2 Relatórios – Portfolio & Investor Transactions

```python
from luxorasap.btgapi.reports import (
    request_portfolio, await_report_ticket_result, process_zip_to_dfs,
    request_investors_transactions_report,
)

ticket = request_portfolio(TOKEN, "LUXOR FUND - CLASS A",
                           start=dt.date(2025,1,1), end=dt.date(2025,1,31))
zip_bytes = await_report_ticket_result(TOKEN, ticket)
carteiras = process_zip_to_dfs(zip_bytes)
```

### 6.3 Trades offshore

```python
from luxorasap.btgapi.trades import (
    submit_offshore_equity_trades,
    await_transaction_ticket_result,
)

ticket = submit_offshore_equity_trades(TOKEN, trades=[{...}], test_env=True)
status_df = await_transaction_ticket_result(TOKEN, ticket, test_env=True)
```

### 6.4 Extras

* `BTGApiError` — exceção customizada para qualquer falha.

---

## 7. Roadmap & Contribuições

* **Remover** `ingest.legacy_local` quando não houver mais dependências.
* Suporte a partições Parquet (delta‑like) na gravação.
* Adicionar `pydantic` para validar contratos BTG.
* Pull requests bem‑vindos!  Rode `make lint && pytest -q` antes de enviar.

---

### Contatos

* Dados / Back‑Office – [backoffice@luxor.com.br](mailto:backoffice@luxor.com.br)
* Mantenedor principal – Sergio
