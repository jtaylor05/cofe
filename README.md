# cofe
A modular counterfactual python-compatible environment.

## AST Transformations

For all Python AST transformations, I focused on name based changes rather than structural changes, as the code must still be valid python in order to run from this point. What follows is a list of all transformation classes and their intended use. A strict transformer essentially means it does not allow the <self.new> value to exist in the AST tree.

- StrictCallTransformer: Changes all instances of ast.Call with the value <self.old> to <self.new>. e.g. foo() -> bar()
- StrictFuncDefTransformer: Changes all instances of ast.FuncDef with the value <self.old> to <self.new>. e.g. def foo() -> def bar()
- StrictImportTransformer: Changes all instances of ast.Import with the value <self.old> to <self.new>. Additionally sets <asname=self.new>. e.g. import system -> import sys as system
- StrictImportFromTransformer: Changes all instances of the ast.ImportFrom with the value <self.old> to <self.new>. e.g. from path_system import Path -> from pathlib import Path.
- AggregateFuncTransformer: acts as the union between _StrictCallTransformer_ and _StrictFuncDefTransformer_. Meant to be used to modify internally defined methods.
- AggregateImportTransformer: acts as the union between _StrictImportTransformer_ and _StrictImportFromTransformer_. Meant to be used to modify externally imported API (i.e. os, sys, requests, etc.).

Example use cases can be found in the test files.

## Grammar Transformations

For all Grammar transformations, I focused on changing the syntactic structure of Python, including keywords, format and other base rules of the language. What follows are a list of the relevant classes in the file.

- GrammarWrapper: A helper class and an extension of pegen.grammar.Grammar. Gathers all instances of classes that share the same value, using the assumption that they are meant to be pointing at the same value. Allows for easily modifying instances of these values.
- RenameLeaf: Renames either all StringLeaf's (pegen grammar literal) or NameLeaf's (pegen grammar reference) that have the value <self.old> to <self.new>
- RenameRule: Renames the rule with the name <self.old> to <self.new>. Additionally uses RenameLeaf(NameLeaf, self.old, self.new) to rename all references to the rule.
- ReplaceRuleBoady: A more user controlled class allowing for complete control over how a rule works. Should be used first as it does not merge well with Renaming.
- InjectAlt: Another high-control class allowing the injection of an entirely new Alt branch for one rule. Should be used second.