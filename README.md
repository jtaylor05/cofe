# cofe

## Intro

cofe is a research-oriented tool meant to allow for a modular and counterfactual environment creation that is completely compatible with modern Python. This can be used to test LLMs and Agents in environments unfamiliar to them without the need to create one from scratch.

cofe is not meant to be used in a production setting, as the modular nature of the interpreter causes a slow-down on all code running. Instead, use cofe to explore and improve upon agentic coding in novel environments.

This package comes with the interpreter as well as the tools needed to create any environment you want starting from the Python grammar. The package is aimed at modifying both syntax modifications, as well as API changes.

## Installation

The cofe package is available on PyPI. It currently does not support uv so please install on pip with the following command:
```bash
pip install cofe
```
Currently cofe only supports **Python 3.13**. I aim to increase the number of available versions as more of Python's grammar is integrated into the tool.

## Quick Start

### Setup

In order to create your environment, you must first create your transformers. To create your transformers, checkout [Creating Transformers](#creating-transformers). After you have those, you must make the classes you just created visible to the tool. In order to do that, run:
```bash
cofe config -t ClassName=path/to/class ClassName2=path/to/other/class
```
This logs all of your new classes with the tool so it knows where to find them. 

However, the tool will not use them yet. After you added the available transformations, you can now piece them together in any format. To add configurations to the active list, do the following command:
```bash
cofe config -a ClassName ClassName2
```

### Use

With that you have created your counterfactual environment. In order to run code in this new environment, pass a file to the cofe interpreter like you would to Python. 
```bash
cofe file.y
```
The package will only modify files with the extension '.y' and treat everything else as normal python. If you want to change the extension, just run the following command:
```bash
cofe config -c extension=.new
```

### Saving

Finally, after you finish running all of your counterfactual code, you can save your configuration to a separate file so you can use it again later. Simply run:
```bash
cofe config -T place/to/save
```
Then if you want to reload that particular configuration, all you have to do is run:
```bash
cofe config -s place/to/save
```

### Test Mode

As this is meant to be a tool that is visible to active models, it additionally has a 'safe' mode meant to be activated so a model can not just run all the same commands above and undo your environment. After you run:
```bash
cofe config -c test=True
```
The only tool made available is the code running. In order to remove test mode, you must find your active config file in your 'cwd/.cenv/config.ini' and replace test=True with test=False.


## Creating Transformers

Here is a simple example of how to create a transformer:
```python
from cofe.configure import Transform
from cofe.grammar_transform import RenameStringLeaf

class NewTransform(Transform):

    def __init__(self):
        self.rename = RenameStringLeaf('if', 'when')

    def apply_grammar(self, grammar):
        return self.rename.apply(grammar)
    
    def apply_ast(self, root):
        #do something
        return root

    def get_sort(self):
        return 1

```

There are a few things here that are important.
1. The new transformer class must be a subclass of the 'Transform' class in cofe.configure.
2. In order to modify anything you must either implement apply_grammar() or apply_ast(). More details about how to modify those are provided in the section below.
3. If you wish to add a custom ordering, implement the get_sort() method and return whatever value you see fit. 0 is the basic value.

## Transformation Details

What follows below are the different types of transformations built-in with the tool, including AST transformers and pegen Grammar transformers. If you want more details about pegen, you can find their GitHub [here](https://github.com/we-like-parsers/pegen)

### AST Transformations

These transformers use the standard ast.NodeVisitor class in order to visit all ast Nodes in the tree. Transformations to the ast should focus on targeting API names or standard Python library functions (i.e. print(), range()).

Below are a few tools to help you more easily put together modifications. You must import them from cofe.ast_transform.

- StrictCallTransformer: Changes all instances of ast.Call with the value <self.old> to <self.new>. e.g. foo() -> bar(). Does not allow any instances of <self.new>.
- StrictFuncDefTransformer: Changes all instances of ast.FuncDef with the value <self.old> to <self.new>. e.g. def foo() -> def bar(). Does not allow any instances of <self.new>.
- StrictImportTransformer: Changes all instances of ast.Import with the value <self.old> to <self.new>. Additionally sets <asname=self.new>. e.g. import system -> import sys as system. Does not allow any instances of <self.new>.
- StrictImportFromTransformer: Changes all instances of the ast.ImportFrom with the value <self.old> to <self.new>. e.g. from path_system import Path -> from pathlib import Path. Does not allow any instances of <self.new>.
- AggregateFuncTransformer: Uses both _StrictCallTransformer_ and _StrictFuncDefTransformer_. Meant to be used to modify internally defined methods.
- AggregateImportTransformer: acts as the union between _StrictImportTransformer_ and _StrictImportFromTransformer_. Meant to be used to modify externally imported API (i.e. os, sys, requests, etc.).

Example use cases can be found in the cofe.configure file.

### Grammar Transformations

These transformers are meant to modify the python.gram file as defined by pegen's [python.gram](https://github.com/we-like-parsers/pegen/blob/main/data/python.gram). To get more information about the file and how to transform it, please take a look at their documentation and read through the grammar file to figure out what you want to change.

Below are a few tools to help you more easily put together grammar modifications. It utilises pegen's GrammarVisitor. Import them from cofe.grammar_transform.

- RenameStringLeaf: Renames all StringLeafs that have the value <self.old> to <self.new>. A StringLeaf is always a hard keyword (i.e. 'if', 'for', 'lambda').
- RenameNameLeaf: Renames all NameLeafs that have the value <self.old> to <self.new>. A NameLeaf is all references to other rules internal to the python.gram.
- RenameRule: Renames the rule with the name <self.old> to <self.new>. Additionally uses RenameNameLeaf(self.old, self.new) to rename all references to the rule.
- ReplaceRuleBody: Completely replace an old rule with a new rule. The new rule should include the name of the old rule in its definition. Should be used first as it does not merge well with Renaming.
- InjectAlt: Allows the injection of one Alt (a single 'or' branch of a rule) at the beginning or end of a rule set. Should be used before everything else but after ReplaceRuleBody.