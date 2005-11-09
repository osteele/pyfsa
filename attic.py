def traceREStates(fsa, s, trace=1):
    #if decompileFSA(fsa, sep='') != expr:
    #   print expr, 'is equivalent to', decompileFSA(fsa, sep='')
    states = fsa.epsilonClosure(fsa.initialState)
    for i in range(len(s)):
        newStates = fsa.nextStateSet(states, s[i])
        if newStates:
            if trace:
                print sdbre(fsa, newStates), 'matches', s[:i+1] + '.' + s[i+1:]
            states = newStates
        else:
            c = CharacterSet([])
            for s0 in states:
                for _, _, label in fsa.transitionsFrom(s0):
                    if label:
                        c = c.union(label)
            print sdbre(fsa, states), 'stops matching at', s[:i] + '.' + s[i:], '; expected', c
            break

