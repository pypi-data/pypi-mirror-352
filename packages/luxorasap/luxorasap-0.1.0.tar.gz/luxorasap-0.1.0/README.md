# LuxorASAP

**LuxorASAP** é o pacote-guarda-chuva que concentra as ferramentas internas de dados da Luxor Group:  
consulta estruturada ao data lake, cargas padronizadas para ADLS, wrappers de API, utilitários e muito mais.

[![PyPI](https://img.shields.io/pypi/v/luxorasap.svg)](https://pypi.org/project/luxorasap/)
![Python](https://img.shields.io/pypi/pyversions/luxorasap)

---

## Instalação

```bash
# pacote base
pip install luxorasap

# com o submódulo datareader
pip install "luxorasap[datareader]"
```
## Uso rápido
```python
from luxorasap.datareader import LuxorQuery

lq = LuxorQuery(blob_directory="enriched/parquet")
prices = lq.get_prices("aapl us equity", "2024-01-01", "2024-12-31")
print(prices.head())
```
## Submódulos
| Módulo                 | Descrição rápida                         | Extras                                |
| ---------------------- | ---------------------------------------- | ------------------------------------- |
| `luxorasap.datareader` | Leitura de tabelas e séries no data lake | `pip install "luxorasap[datareader]"` |
| `luxorasap.ingest`     | Funções de carga padronizada para ADLS   | `"luxorasap[ingest]"`                 |
| `luxorasap.btgapi`     | Wrapper REST para dados BTG              | `"luxorasap[btgapi]"`                 |

© Luxor Group – uso interno. Todos os direitos reservados.
