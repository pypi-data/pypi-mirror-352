import datetime as dt, io, json, zipfile
import pandas as pd
import pytest

from luxorasap.btgapi.reports import (
    request_portfolio,
    await_report_ticket_result,
    process_zip_to_dfs,
)

_TICKET_URL = "https://funds.btgpactual.com/reports/Ticket"
_POST_URL   = "https://funds.btgpactual.com/reports/Portfolio"

def test_request_portfolio_returns_ticket(requests_mock):
    requests_mock.post(_POST_URL, json={"ticket": "ABC"})
    tk = request_portfolio("tok", "FUND", dt.date(2025,1,1), dt.date(2025,1,31))
    assert tk == "ABC"

def test_await_ticket_inline_zip(requests_mock, monkeypatch):
    # 1ª chamada: ainda processando   2ª: devolve ZIP binário
    # Explicando o que requests_mock faz:
    # 
    requests_mock.get(_TICKET_URL, [
        {"json": {"result": "Processando"}},
        {"content": b"ZIP!"},
    ])
    monkeypatch.setattr("time.sleep", lambda *_: None)
    out = await_report_ticket_result("tok", "ABC", attempts=2, interval=0)
    assert out == b"ZIP!"

def test_await_ticket_via_urldownload(requests_mock, monkeypatch):
    dl_url = "https://download/file.zip"
    # 1ª chamada ao ticket devolve JSON com UrlDownload
    requests_mock.get(_TICKET_URL, json={"result": json.dumps({"UrlDownload": dl_url})})
    requests_mock.get(dl_url, content=b"ZIP2", headers={"Content-Type": "application/zip"})
    monkeypatch.setattr("time.sleep", lambda *_: None)
    out = await_report_ticket_result("tok", "XYZ", attempts=1)
    assert out == b"ZIP2"


def test_process_zip_to_dfs():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        df = pd.DataFrame({"x": [1]})
        zf.writestr("data.csv", df.to_csv(index=False))
    dfs = process_zip_to_dfs(buf.getvalue())
    assert dfs["data.csv"].iloc[0, 0] == 1
    
    
def test_process_zip_latin1_csv():
    import io, zipfile, pandas as pd
    from luxorasap.btgapi.reports import process_zip_to_dfs

    df_src = pd.DataFrame({"nome": ["ação", "æøå"]})
    csv_latin1 = df_src.to_csv(index=False, encoding="latin1")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("dados.csv", csv_latin1)

    dfs = process_zip_to_dfs(buf.getvalue())
    assert dfs["dados.csv"].equals(df_src)