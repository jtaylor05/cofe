from __future__ import annotations

import ast
import sys
import functools
import warnings
from typing import Optional, Tuple, Union

from cofe.transform.grammar_transform import GrammarWrapper
from cofe.transform.transformer import Transform
from cofe.config.configure import PackageConfigParser
from cofe.utils import import_module_from_file, get_python_grammar, parse_from_grammar, matches_transform

from pathlib import Path
from abc import ABC

PathLike = Union[str, Path]
AST = ast.AST
    
@functools.lru_cache(maxsize=None)
def get_transformer_src(file_path: PathLike = None) -> list[Transform]:
    config = PackageConfigParser(config_file=file_path)
    
    _modules = {}
            
    transformers: list[Transform] = []
    
    for cls, f in config.get_active().items():
        p = Path(f)
        module_name = p.name
        
        if module_name in _modules:
            class_var = getattr(_modules[module_name], cls)
            if matches_transform(class_var):
                transformers.append(class_var())
            continue
        
        module = import_module_from_file(module_name, p)
        
        _modules[module_name] = module
        class_var = getattr(module, cls)
        if matches_transform(class_var):
            transformers.append(class_var())
    
    transformers.sort(key=lambda t: t.get_sort())
    return transformers

def get_modified_grammar(config_file: PathLike = None) -> GrammarWrapper:
    grammar = GrammarWrapper(get_python_grammar())
    
    transformers = get_transformer_src(file_path=config_file)
    
    for t in transformers:
        t.apply_grammar(grammar)
        
    return grammar

def transform_code(
    source: str,
    config_file: PathLike = None,
    py_version: Optional[Tuple[int, int]] = None,
) -> str:
    transformers = get_transformer_src(file_path=config_file)
    
    grammar = get_modified_grammar(config_file)
    
    for t in transformers:
        source = t.preprocess(source)
    
    root = None
    try:
        root = parse_from_grammar(source, grammar, py_version=py_version)
    except Exception as e:
        raise e
    
    for t in transformers:
        t.apply_ast(root)
        
    transformed = ast.unparse(root)
    
    for t in transformers:
        transformed = t.postprocess(transformed)

    return transformed
        