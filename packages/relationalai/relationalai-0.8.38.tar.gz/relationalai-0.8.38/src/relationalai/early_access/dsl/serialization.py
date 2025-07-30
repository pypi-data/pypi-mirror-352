from io import StringIO

from relationalai.early_access.dsl.adapters.orm.adapter import ORMAdapter
from relationalai.early_access.dsl.adapters.orm.adapter_qb import ORMAdapterQB
from relationalai.early_access.dsl.adapters.owl.adapter import OwlAdapter
from relationalai.early_access.dsl.ontologies.python_printer import PythonPrinter
from relationalai.early_access.dsl.orm.printer import Printer

def orm_to_python(orm_file_path: str, output_file_path: str) -> None:
    model_to_python(ORMAdapter(orm_file_path).model, output_file_path)

def owl_to_python(owl_file_path: str, output_file_path: str) -> None:
    model_to_python(OwlAdapter(owl_file_path).model, output_file_path)

def model_to_python(model, output_file_path: str) -> None:
    with StringIO() as s:
        PythonPrinter(s).to_python_string(model)
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(s.getvalue())

def orm_to_python_string(orm_file_path: str) -> str:
    return model_to_python_string(ORMAdapter(orm_file_path).model)

def orm_to_qb_python_string(orm_file_path: str) -> str:
    return model_to_qb_python_string(ORMAdapterQB(orm_file_path).model)

def owl_to_python_string(owl_file_path: str) -> str:
    return model_to_python_string(OwlAdapter(owl_file_path).model)

def model_to_python_string(model) -> str:
    with StringIO() as s:
        PythonPrinter(s).to_python_string(model)
        return s.getvalue()

def model_to_qb_python_string(model) -> str:
    with StringIO() as s:
        Printer(s).to_string(model)
        return s.getvalue()