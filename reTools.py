__author__  = "Oliver Steele <steele@cs.brandeis.edu>"

#
# Simplification
#

def simplify(str):
    # replace() is workaround for bug in simplify
    return decompileFSA(compileRE(str).minimized()).replace('?*','*')

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
             ('(ab)*(cd)', '(ab)*cd)'),
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


#
# Comparison
#

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

# todo: lift FSA operators to string operators:
print complement('ab*')
print difference('a*b', 'ab*')
"""

#
# Tracing
#

"""
To do:
Bug fixes:
    - in tracing, ab*\&a*b at final state only prints the period at the end
    - trace doesn't work with nondeterminized automata

Functions for web page:
1) Show how far we got (the last state)
2) Give a list of n steps

Later:
3) Simplify, add algebra
"""

def collectSourcePositions(fsa, states):
    positions = []
    for state in states:
        for transition in fsa.transitionsFrom(state):
            for position in fsa.getArcMetadataFor(transition, []):
                if position not in positions:
                    positions.append(position)
    return positions

def fsaLabelWithCursor(fsa, states):
    """Return the FSA's label, with a cursor ('.') inserted at
    each position in states."""
    s = ''
    positions = collectSourcePositions(fsa, states)
    for index in range(len(fsa.label)):
        if index + 1 in positions:
            s = s + '.'
        s = s + fsa.label[index]
    if filter(lambda s, finals=fsa.finalStates: s in finals, states):
        s = s +  '.'
    return s

from compileRE import compileRE

def traceREStates(re, str, trace=1):
    fsa = compileRE(re, recordSourcePositions=1)
    states = fsa.epsilonClosure(fsa.initialState)
    for i in range(len(str)):
        newStates = fsa.nextStateSet(states, str[i])
        if newStates:
            if trace:
                print fsaLabelWithCursor(fsa, newStates), 'matches', str[:i+1] + '.' + str[i+1:]
            states = newStates
        else:
            c = CharacterSet([])
            for s0 in states:
                for _, _, label in fsa.transitionsFrom(s0):
                    if label:
                        c = c.union(label)
            print fsaLabelWithCursor(fsa, states), 'stops matching at', str[:i] + '.' + str[i:], '; expected', c
            break

def updatePositions(fsa, states, input, positions):
    successors = []
    #print 'counting from', states, 'over', label, 'in', fsa.label
    for state in states:
        for transition in fsa.transitionsFrom(state):
            _, sink, label = transition
            if fsa.labelMatches(label, input) and sink not in successors:
                successors.extend(fsa.epsilonClosure(sink))
                #todo: share with collectSourcePositions
                data = fsa.getArcMetadataFor(transition, [])
                for position in data:
                    if position not in positions:
                        positions.append(position)
    return successors

def reMatchStatePairs(re, str):
    """Return a list of (re, str), where re is a the regular
    expression with <SPAN>s inserted over all the matched characters,
    and str is the string with <SPAN>s likewise inserted."""
    #print re, '~=', str
    pairs = []
    fsa = compileRE(re, recordSourcePositions=1)
    states = fsa.epsilonClosure(fsa.initialState)
    positions = [] #todo: everything that starts here?
    for i in range(len(str)):
        if i < len(str):
            #print states, '->', newStates, '(', str[i], ')'
            #todo: factor the following block with fsa.nextStateSet
            newPositions = []
            newStates = updatePositions(fsa, states, str[i], newPositions)
            #assert newStates == fsa.nextStateSet(states, str[i])
        if not newStates:
            # we ran out of matches
            # todo: show in red where the match stopped, as in the textual version
            expected = None
            for state in states:
                for t in fsa.transitionsFrom(state):
                    label = t[2]
                    if expected:
                        expected = expected + label
                    else:
                        expected = label
            return pairs, 'expected %s' % expected
        srcLabel = fsa.label
        # todo: could color newly matched states in a different color
        #todo: quote the html stuff
        rem = ''
        #print srcLabel, allStates, positions
        def htmlQuote(str):
            return ''.join([{'<': '&lt;', '>': '&gt;', '&': '&amp;'}.get(c, c) for c in str])
        for j in range(len(srcLabel)):
            c = htmlQuote(srcLabel[j])
            if j+1 in newPositions:
                rem += '<SPAN CLASS="rematchnew">%s</SPAN>' % c
                #positions.append(j)
            elif j+1 in positions:
                rem += '<SPAN CLASS="rematch">%s</SPAN>' % c
            else:
                rem += c
        s0, s1, s2 = htmlQuote(str[:i+1]), '', htmlQuote(str[i+1:])
        strm = '<SPAN CLASS="strmatch">%s</SPAN><SPAN CLASS="strmatchnew">%s</SPAN>%s' % (s0, s1, s2)
        comment = "states: %s -> %s; positions: %s -> %s; index = %d" % (states,newStates,positions,newPositions,i)
        pairs.append((rem, strm, comment))
        states = newStates
        positions += newPositions
    return pairs, [s for s in states if s in fsa.finalStates]

_CASES = [('abc', 'abc'),
          ('abc', 'ab'),
          ('ab', 'abc'),
          ('ab|ac', 'ab'),
          ('(a*b)*', 'aaabaabab'),
          ('abc', 'ac')]

# attributes at http://www.echoecho.com/csslinks.htm
STYLE = """<STYLE TYPE="text/css" MEDIA="screen" TITLE="Special paragraph colour">
<!--
SPAN.rematch {text-decoration: underline;}
SPAN.rematchnew {color: green; style: bold; text-face: bold; font-style: bold; background: red}
SPAN.strmatch {text-decoration: underline; background: yellow}
SPAN.strmatchnew {text-decoration: underline;}
-->
</STYLE>"""

def makeHtml():
    import os
    f = open('match.html', 'w')
    #f = open(os.path.join(os.path.split(__file__)[0], 'foo.html'), 'w')
    print >> f, '<HTML><HEAD>'
    print >> f, STYLE
    print >> f, '</HEAD><BODY>'
    for re, str in _CASES:
        pairs, success = reMatchStatePairs(re, str)
        op = success and '=~' or '!~'
        print >> f, '<H1>%r %s /%s/</H1>' % (str, op, re)
        print >> f, '<TABLE>'
        for r, s, note in pairs:
            print >> f, '<TR><TD>%s' % r
            print >> f, '<TD>=~'
            print >> f, '<TD>%s' % s
            print >> f, '<TD>%s' % note
        if not success:
            print >> f, '<TR><TD COLSPAN=2>Failure'
        print >> f, '</TABLE>'
    print >> f, '</BODY></HTML>'

#print reMatchStatePairs('abc', 'abc')

makeHtml()

def _test(reset=0):
    import doctest, reTools
    if reset:
        doctest.master = None # This keeps doctest from complaining after a reload.
    return doctest.testmod(reTools)
