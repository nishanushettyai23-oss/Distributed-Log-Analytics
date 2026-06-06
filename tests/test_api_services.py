from api.services.export_service import ExportService
from api.services.query_service import QueryService


class QueryConfig:
    MAX_QUERY_ROWS = 100


def test_query_service_accepts_select():
    service = QueryService(repository=None, config=QueryConfig())
    assert service.validate("SELECT component FROM logs") == "SELECT component FROM logs"


def test_query_service_accepts_cte():
    service = QueryService(repository=None, config=QueryConfig())
    assert service.validate("WITH logs AS (SELECT 1 AS value) SELECT * FROM logs").startswith("WITH")


def test_query_service_blocks_mutation():
    service = QueryService(repository=None, config=QueryConfig())
    try:
        service.validate("DELETE FROM logs")
        assert False, "DELETE must be blocked"
    except ValueError as error:
        assert "SELECT" in str(error)


def test_query_service_blocks_multiple_statements():
    service = QueryService(repository=None, config=QueryConfig())
    try:
        service.validate("SELECT 1; SELECT 2")
        assert False, "Multiple statements must be blocked"
    except ValueError as error:
        assert "one SELECT" in str(error)


def test_exports_are_generated():
    rows = [{"component": "DataNode", "logs": 42}]
    assert b"component" in ExportService.csv_bytes(rows)
    assert ExportService.xlsx_bytes(rows).startswith(b"PK")
    assert ExportService.pdf_bytes("Report", [("Logs", 42)]).startswith(b"%PDF")
