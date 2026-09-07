import textwrap

from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple, Type

from pegen.grammar import (
    Alt,
    Gather,
    Grammar,
    GrammarVisitor,
    Leaf,
    NameLeaf,
    NamedItem,
    Rhs,
    Rule,
    StringLeaf,
)
from pegen.grammar_parser import GeneratedParser as GrammarParser
from pegen.utils import parse_string

type NameTable = Dict[Tuple[Type, str], List[Leaf]]
type LeafKey = Tuple[Type, str]

class _LeafCollector(GrammarVisitor):
    """Walks a Rule and records every NameLeaf/StringLeaf occurrence."""
 
    def __init__(self) -> None:
        self.visited: Set[Any] = set()
        self.table: NameTable = {}
        self.count = 0
 
    def check_visited(self, node: Any) -> bool:
        if node in self.visited:
            return True
        self.visited.add(node)
        return False
 
    def _gather(self, node: Leaf) -> None:
        key: LeafKey = (type(node), node.value)
        self.table.setdefault(key, []).append(node)
 
    def visit_NameLeaf(self, node: NameLeaf) -> None:
        self._gather(node)
 
    def visit_StringLeaf(self, node: StringLeaf) -> None:
        self._gather(node)
 
    def visit_Gather(self, node: Gather) -> None:
        self.visit(node.separator)
        self.visit(node.node)
    
    def generic_visit(self, node, *args, **kwargs):
        """Called if no explicit visitor function exists for a node."""
        for value in node:
            if isinstance(value, list):
                for item in value:
                    if self.check_visited(item):
                        continue
                    self.visit(item, *args, **kwargs)
            else:
                if self.check_visited(value):
                    continue
                self.visit(value, *args, **kwargs)

def gather_names(grammar: Grammar) -> NameTable:
    visitor = _LeafCollector()
    visitor.visit(grammar)
    return visitor.table

class GrammarWrapper(Grammar):
    
    def __init__(self, grammar: Grammar):
        self.grammar: Grammar = grammar
        self.names: NameTable = gather_names(grammar)
    
    @property
    def rules(self):
        return self.grammar.rules
    
    @property
    def metas(self):
        return self.grammar.metas
    
    def regather_names(self):
        self.names = gather_names(self.grammar)
        
    def set_node_name(self, leaf: Leaf, new_value: str):
        self.set_type_name(type(leaf), leaf.value, new_value)
    
    def set_type_name(self, type: Type, value: str, new_value:str):
        key, new_key = (type, value), (type, new_value)
        if key not in self.names:
            raise ValueError(f"Leaves of type {type} and value {value} not in nametable.")
        if new_key in self.names:
            raise ValueError(f"Leaves of type {type} and value {new_value} already in nametable.")
        
        for node in self.names[key]:
            node.value = new_value
        
        self.names[new_key] = self.names.pop(key)
    
    def __str__(self) -> str:
        return self.grammar.__str__()

    def __repr__(self) -> str:
        return self.grammar.__repr__()

    def __iter__(self):
        yield from self.grammar
        
def _parse_fragment(rule_source: str) -> Rule:
    """
    Parse a single standalone rule (e.g. "sum: expr '+' expr { ... }\\n")
    through pegen's own GrammarParser and return the resulting Rule.
 
    Useful for building replacement Rhs/Alt objects without hand-constructing
    Alt/NamedItem/Leaf trees yourself.
    """
    src = textwrap.dedent(rule_source).strip() + "\n"
    grammar = parse_string(src, GrammarParser)
    if len(grammar.rules) != 1:
        raise ValueError(f"expected exactly one rule in fragment, got {list(grammar.rules)}")
    return next(iter(grammar.rules.values()))

@dataclass
class GrammarTransform:
    """Base class. Subclasses implement apply(wrapper)."""
 
    def apply(self, wrapper: GrammarWrapper) -> None:
        raise NotImplementedError
 
@dataclass
class RenameLeaf(GrammarTransform):
    """Rename every occurrence of a NameLeaf or StringLeaf value.
 
    Examples
    --------
    RenameLeaf(StringLeaf, "'lambda'", "'fn'")   # rename a hard keyword
    RenameLeaf(NameLeaf, "expression", "expr")   # rename a rule reference
    """
 
    leaf_type: Type
    old: str
    new: str
 
    def apply(self, wrapper: GrammarWrapper) -> None:
        wrapper.set_type_name(self.leaf_type, self.old, self.new)
 
@dataclass
class RenameStringLeaf(GrammarTransform):
    """Rename every occurrence of a StringLeaf value
    """
 
    old: str
    new: str
 
    def apply(self, wrapper: GrammarWrapper) -> None:
        wrapper.set_type_name(StringLeaf, self.old, self.new)
        
@dataclass
class RenameNameLeaf(GrammarTransform):
    """Rename every occurrence of a NameLeaf value
    """
 
    old: str
    new: str
 
    def apply(self, wrapper: GrammarWrapper) -> None:
        wrapper.set_type_name(NameLeaf, self.old, self.new)
 
 
@dataclass
class RenameRule(GrammarTransform):
    """Rename a rule definition and every reference to it."""
 
    old: str
    new: str
 
    def apply(self, wrapper: GrammarWrapper) -> None:
        grammar = wrapper.grammar
        if self.old not in grammar.rules:
            raise KeyError(f"no such rule: {self.old!r}")
        rule = grammar.rules.pop(self.old)
        rule.name = self.new
        grammar.rules[self.new] = rule
        # Every reference elsewhere in the grammar is a NameLeaf(self.old)
        wrapper.set_type_name(NameLeaf, self.old, self.new)
 
 
@dataclass
class ReplaceRuleBody(GrammarTransform):
    """Replace a rule's entire Rhs by parsing a fresh rule fragment."""
 
    rule_name: str
    new_source: str  # e.g. "sum: expr '+' expr { BinOp(expr, Add(), expr) }"
 
    def apply(self, wrapper: GrammarWrapper) -> None:
        grammar = wrapper.grammar
        if self.rule_name not in grammar.rules:
            raise KeyError(f"no such rule: {self.rule_name!r}")
        fragment = _parse_fragment(self.new_source)
        if fragment.name != self.rule_name:
            raise ValueError(
                f"fragment defines {fragment.name!r}, expected {self.rule_name!r}"
            )
        grammar.rules[self.rule_name].rhs = fragment.rhs
        
        wrapper.regather_names()  # new rule may have new leaves, so rebuild the nametable
 
 
@dataclass
class InjectAlt(GrammarTransform):
    """Add a new alternative to an existing rule without touching the rest."""
 
    rule_name: str
    alt_source: str  # e.g. "expr '@' expr { MatMult(expr, expr) }"
    prepend: bool = False  # PEG tries alts in order -- prepend for higher priority
 
    def apply(self, wrapper: GrammarWrapper) -> None:
        grammar = wrapper.grammar
        rule = grammar.rules[self.rule_name]
        # Wrap the single alt in a throwaway rule so the parser gives us
        # back a real Alt object via its Rhs.
        wrapper_source = f"_tmp: {self.alt_source}\n"
        fragment = _parse_fragment(wrapper_source)
        new_alts: List[Alt] = fragment.rhs.alts
        if self.prepend:
            rule.rhs.alts = new_alts + rule.rhs.alts
        else:
            rule.rhs.alts = rule.rhs.alts + new_alts
        wrapper.regather_names()  # new alt may have new leaves, so rebuild the nametable
 
if __name__ == "__main__":
    from pegen.utils import generate_parser
 
    src = """
    start: sum NEWLINE ENDMARKER { sum }
    sum: sum '+' term { sum + term } | term { term }
    term: NUMBER { int(number.string) }
    """
    grammar = parse_string(src, GrammarParser)
    wrapper = GrammarWrapper(grammar)
 
    # rename the '+' operator to '@'
    transform = RenameLeaf(StringLeaf, "'+'", "'@'")
    transform.apply(wrapper)
 
    print(wrapper)  # sum: sum '@' term { ... } | term { ... }
 
    parser_class = generate_parser(wrapper, parser_name="GeneratedParser")
    result = parse_string("1@2@3", parser_class)
    print(result)  # 6