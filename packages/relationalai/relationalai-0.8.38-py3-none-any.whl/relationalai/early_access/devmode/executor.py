from __future__ import annotations

import duckdb
from pandas import DataFrame
from typing import Any, Union

from relationalai.early_access.metamodel import ir, executor as e
from . import Compiler

class Executor(e.Executor):

    def execute(self, model: ir.Model, task:ir.Task) -> Union[DataFrame, Any]:
        return self._execute(Compiler().compile(model))

    def execute_without_denormalization(self, model: ir.Model) -> Union[DataFrame, Any]:
        return self._execute(Compiler(skip_denormalization=True).compile(model))

    def _execute(self, sql: str) -> Union[DataFrame, Any]:
        """ Execute the SQL query directly. """
        connection = duckdb.connect()
        try:
            result = connection.query(sql).to_df()
            return result
        finally:
            connection.close()
