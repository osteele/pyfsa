"""
To do:
New features:
    - iteration reduction
Bug fixes:
    - A* ending up A?*
    - (a*b)*
Cleanup:
    - fix the case where there's no expression
    - alphabetize multiple branches (or sort by source order?)
Optimizations:
    - only walk the cycle when there's a suffix

"""

__author__  = "Oliver Steele <steele@cs.brandeis.edu>"

from compileRE import compileRE

#
# Converting FSAs to RE trees
#

def decompileFSA(fsa, dottedStates=[], wrap=None, sep=None, returnTree=0):
    queries = {}
    if dottedStates:
        for state in dottedStates:
            queries[state] = []
    tree = computeSubgraphTree(fsa.transitions, fsa.initialState, fsa.finalStates, dottedStates)
    if returnTree or tree is None:
        return tree
    if sep is None:
        sep = ''
        labels = fsa.alphabet or fsa.labels()
        if filter(lambda label:type(label) == type('a'), labels) == labels and filter( lambda label:len(label) > 1, labels):
            sep = ' '
    #print tree
    #tree = combineDisjunctionEnds(tree)
    #print tree
    return treeToString(tree, sep=sep, wrap=wrap)

def addListMappingItem(mapping, key, value):
    for tk, tv in mapping:
        if key == tk:
            tv.append(value)
            return
    mapping.append((key, [value]))

def combineDisjunctionEnds(tree):
    if tree in (EMPTY_TREE, DOT_TREE) or tree[0] == 'LEAF':
        return tree
    if tree[0] == DISJUNCTION:
        mapping = []
        disjuncts = map(combineDisjunctionEnds, tree[1])
        #print 'incoming:', disjuncts
        for disjunct in disjuncts:
            if type(disjunct) == TupleType and disjunct[0] == CONCATENATION:
                disjunct = disjunct[1]
            else:
                disjunct = [disjunct]
            addListMappingItem(mapping, disjunct[-1], makeConcatenationTree(disjunct[:-1]))
        if len(mapping) < len(disjuncts):
            disjuncts = []
            for key, paths in mapping:
                disjuncts.append(concatenateTrees(makeDisjunctionTree(paths), key))
            #print '->', disjuncts
        disjuncts.sort()
        return makeDisjunctionTree(disjuncts)
    elif tree[0] == CONCATENATION:
        return (tree[0], map(combineDisjunctionEnds, tree[1]))
    elif tree[0] in QUANTIFIERS:
        return (tree[0], combineDisjunctionEnds(tree[1]))
    else:
        raise 'unknown operator', tree[0]

def computeSubgraphTree(graph, start, finals, dottedStates, brokenNodes=[], isFirst=0, forbidden=[]):
    """Returns a list of disjuncts.  If there's only one possibility, the list is a singleton."""
    if start in brokenNodes and not isFirst:
        #print graph, start, finals, isFirst, brokenNodes, forbidden, ':', (start in finals and EMPTY_TREE) or None
        if start in finals:
            return EMPTY_TREE
        else:
            return None
    
    wasforbidden = forbidden
    wasBroken = brokenNodes
    
    if start not in brokenNodes:
        brokenNodes = brokenNodes + [start]
    
    preamble = None
    if not isFirst:
        preamble = computeSubgraphTree(graph, start, [start], dottedStates, brokenNodes, isFirst=1, forbidden=forbidden)
        if preamble:
            preamble = quantifyTree(preamble)
    
    disjuncts = []
    if start in finals and start not in forbidden:
        disjuncts.append(EMPTY_TREE)
    if preamble:
        forbidden = forbidden + [start]
    for s0, s1, label in graph:
        if s0 == start and s1 not in forbidden:
            branch = label and makeLeaf(label) or EMPTY_TREE
            tail = computeSubgraphTree(graph, s1, finals, dottedStates, brokenNodes, isFirst=0, forbidden=forbidden)
            if tail:
                disjuncts.append(concatenateTrees(branch, tail))
    body = disjuncts and makeDisjunctionTree(disjuncts) or None
    
    if body and start in dottedStates:
        body = concatenateTrees(DOT_TREE, body)
    
    #print graph, start, finals, isFirst, wasBroken, wasforbidden, ':', preamble, '+', body
    if preamble and body:
        body = concatenateTrees(preamble,body)
    #elif preamble and start in finals and not isFirst:
    #   body = preamble
    return body


#
# Tree construction
#

DISJUNCTION = '|'
LEAF = 'LEAF'
CONCATENATION = ':'
QUANTIFIERS = ('*', '?', '+')
EMPTY_TREE = 'e'
DOT_TREE = '.'

def makeNode(op, children):
    return (op, children)

def makeLeaf(value):
    return makeNode(LEAF, value)

def makeDisjunctionTree(disjuncts):
    assert disjuncts, 'no disjuncts'
    if len(disjuncts) == 1:
        return disjuncts[0]
    elif EMPTY_TREE in disjuncts:
        return quantifyTree(makeDisjunctionTree(filter(lambda expr:expr != EMPTY_TREE, disjuncts)), '?')
    else:
        return makeNode(DISJUNCTION, disjuncts)

def makeConcatenationTree(items):
    if len(items) == 0:
        return EMPTY_TREE
    elif len(items) == 1:
        return items[0]
    else:
        return makeNode(CONCATENATION, items)

def concatenateTrees(a, b):
    if a == EMPTY_TREE:
        left = []
    elif a[0] == CONCATENATION:
        left = a[1]
    else:
        left = [a]
    if b == EMPTY_TREE:
        right = []
    elif b[0] == CONCATENATION:
        right = b[1]
    else:
        right = [b]
    children = left + right
    if not children:
        return EMPTY_TREE
    elif len(children) == 1:
        return children[0]
    else:
        return makeNode(CONCATENATION, children)

def quantifyTree(node, quantifier='*'):
    if node == EMPTY_TREE:
        return node
    else:
        return makeNode(quantifier, node)


#
# Rendering trees to strings
#

def treeToString(node, caller=None, wrap=None, sep=None):
    import string
    def toString(node, caller=node[0], wrap=wrap, sep=sep):
        return treeToString(node, caller=caller, wrap=wrap, sep=sep)

    if node == EMPTY_TREE:
        return ''
    elif node == DOT_TREE:
        return '.'
    
    op, args = node[0], node[1]
    if op == LEAF:
        if args == FSA.ANY:
            return '.'
        else:
            s = str(args)
            if ('|' in s or '&' in s) and (s[0] != '(' or s[-1] != ')'):
                s = '(' + s + ')'
            return s
    elif op == CONCATENATION:
        s = string.join(map(toString, args), sep)
        if caller in QUANTIFIERS:
            s = '(' + s + ')'
        return s
    elif op == DISJUNCTION:
        bar = '|'
        #if wrap and len(s) > wrap:
        #   bar = '|\n  '
        s = string.join(map(lambda arg, f=toString:f(arg, wrap=None), args), bar)
        if caller == CONCATENATION or caller in QUANTIFIERS:
            s = '(' + s + ')'
        return s
    elif op in QUANTIFIERS:
        return toString(args) + op
    else:
        raise 'unknown operator:', op


#
# RE comparison
#

def simplify(str):
    return decompileFSA(compileRE(str).minimized())

def _testSimplify():
    cases = ['a',
             'a*',
             'a?',
             'ab',
             'a?b',
             'ab?',
             'a*b',
             'ab*',
             ('abc'),
             ('ab|c'),
             ('ab|ac', 'a[bc]'),
             ('ab|cb', '[ac]b'),
             ('ab|c?'),
             ('(ab)*'),
             ('(ab)*c'),
             ('(ab)*(cd)', '(ab)*cd),
             ('(ab)*(cd)*'),
             ('(ab)?cd'),
             ('ab(cd)?'),
             ('(ab)*c'),
             ('abc|acb|bac|bca|cab|cba', 'c(ab|ba)|a(cb|bc)|b(ac|ca)'),
             ('[ab]c|[bc]a|[ca]b'),
             ('(a*b)*'),
             ('(a|b)*', '[ab]*'),
             ]
    failures = 0
    for case in cases:
        if type(case) == TupleType:
            if len(case) == 1:
                case += case
        else:
            case = (case, case)
        input, expect = case
        receive = simplify(input)
        if expect != receive:
            print 'expected %s -> %s; received %s' % (input, expect, receive)
            failures += 1
    print "%s failure%s" % (failures or 'no', 's'[failures==1:])

def compareREs(*exprs):
    import string
    fsas = map(compileRE, exprs)
    def setName(set):
        set = map(lambda x:x.label, set)
        if len(set) == 1:
            return set[0]
        else:
            import string
            return string.join(set[:-1], ', ') + ' and ' + set[-1]
    print 'Comparing', setName(fsas)
    processed = []
    sets = []
    for fsa in fsas:
        if fsa in processed:
            continue
        set = [fsa]
        for other in fsas:
            if other != fsa and other not in processed and FSA.equivalent(fsa, other):
                set.append(other)
        sets.append(set)
        processed.extend(set)
    for set in sets:
        if len(set) > 1:
            print setName(set), 'are equivalent'
    if len(sets) > 1:
        for set in sets:
            others = filter(lambda a,b=set:a not in b, fsas)
            only = FSA.difference(set[0], reduce(FSA.union, others))
            if not only.isEmpty():
                es = (len(set) == 1 and 'es') or ''
                print 'Only', setName(set), 'match'+es, decompileFSA(only)

"""
compareREs('a*b', 'b*a', 'b|a*b')
compareREs('a*b', 'ab*')
compareREs('a*b', 'b|a*b')
compareREs('ab*', 'b|a*b')

print decompileFSA(compileRE('ab|ac'), [0])
print decompileFSA(compileRE('ab|ac', 0), [0])
print decompileFSA(compileRE('abc'), [1])
print decompileFSA(compileRE('abc'), [1, 2])
print decompileFSA(compileRE('abc'), [0, 1, 2])
print decompileFSA(compileRE('abc'), [0, 1, 2, 3])
print decompileFSA(FSA.compileRE('a bb* c', multichar=1))
print decompileFSA(FSA.compileRE('(a bb)* c', multichar=1))
print decompileFSA(FSA.complement(FSA.containment(FSA.singleton('a'), 3)))

# lift FSA operators to string operators:
print complement('ab*')
print difference('a*b', 'ab*')
"""

def _test(reset=0):
    import doctest, decompileFSA
    if reset:
        doctest.master = None # This keeps doctest from complaining after a reload.
    return doctest.testmod(decompileFSA)
