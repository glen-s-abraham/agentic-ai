# query_runner_tool.py
from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import os, json

class QueryRunnerToolInput(BaseModel):
    """Input schema for QueryRunnerTool."""
    query: str = Field(..., description="Single SQL statement to execute.")
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional bound parameters, e.g. {'id': 42}"
    )

class QueryRunnerTool(BaseTool):
    name: str = "Query runner"
    description: str = "Executes a SQL query on the configured PostgreSQL database."
    args_schema: Type[BaseModel] = QueryRunnerToolInput

    def __init__(self, db_uri: Optional[str] = None):
        """
        db_uri: SQLAlchemy URI. If omitted, reads from env DB_URI or PG* vars.
        Examples:
          postgresql+psycopg://user:pass@localhost:5432/mydb
        """
        super().__init__()
        self._engine: Engine = self._make_engine(db_uri)

    # ---- Tool entrypoint ----
    def _run(self, query: str, params: Optional[Dict[str, Any]] = None) -> str:
        try:
            with self._engine.begin() as conn:
                result = conn.execute(text(query), params or {})
                if result.returns_rows:
                    rows: List[Dict[str, Any]] = [dict(r._mapping) for r in result]
                    return json.dumps({"rows": rows}, default=str)
                else:
                    return json.dumps({"rows_affected": result.rowcount})
        except SQLAlchemyError as e:
            # surface DB/driver errors nicely to the agent
            return f"DB Error: {str(e.__cause__ or e)}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"

    # ---- Internals ----
    def _make_engine(self, db_uri: Optional[str]) -> Engine:
        uri = db_uri or os.getenv("DB_URI") or self._uri_from_pg_env()
        if not uri:
            raise RuntimeError(
                "No DB URI provided. Set DB_URI or PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE."
            )
        # psycopg3 driver recommended: pip install "psycopg[binary]"
        return create_engine(uri, pool_pre_ping=True, future=True)

    def _uri_from_pg_env(self) -> Optional[str]:
        host = os.getenv("PGHOST")
        if not host:
            return None
        user = os.getenv("PGUSER", "postgres")
        pwd  = os.getenv("PGPASSWORD", "")
        port = os.getenv("PGPORT", "5432")
        db   = os.getenv("PGDATABASE", "postgres")
        return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"
