""" Module NumFSAUtils -- optional utility functions for the FSA

The FSA module uses these methods if the Numeric module is present"""

__author__  = "Oliver Steele", 'steele@osteele.com'

import Numeric

class TransitionSet:
    def __init__(self):
        self.capacity = capacity = 100
        self.sources = Numeric.zeros(capacity)
        self.sinks = Numeric.zeros(capacity)
        self.labels = Numeric.zeros(capacity)
        self.size = 0
        self.stateMap = {}
        self.reverseStateMap = []
        self.nextStateIndex = 0
        self.labelMap = {}
        self.reverseLabelMap = []
        self.nextLabelIndex = 0
    
    def stateIndex(self, state):
        index = self.stateMap.get(state)
        if index is None:
            index = self.nextStateIndex
            self.nextStateIndex = index + 1
            self.stateMap[state] = index
            self.reverseStateMap.append(state)
        return index
    
    def labelIndex(self, label):
        index = self.labelMap.get(label)
        if index is None:
            index = self.nextLabelIndex
            self.nextLabelIndex = index + 1
            self.labelMap[label] = index
            self.reverseLabelMap.append(label)
        return index
    
    def append(self, transition):
        source, sink, label = transition
        source, sink, label = self.stateIndex(source), self.stateIndex(sink), self.labelIndex(label)
        index = self.size
        if index >= self.capacity:
            capacity = self.capacity + 100
            self.sources = Numeric.resize(self.sources, [capacity])
            self.sinks = Numeric.resize(self.sinks, [capacity])
            self.labels = Numeric.resize(self.labels, [capacity])
            self.capacity = capacity
        self.sources[index] = source
        self.sinks[index] = sink
        self.labels[index] = label
        self.size = self.size + 1
    
    def __len__(self):
        return self.size
    
    def toList(self, useStateIndices=0):
        transitions = []
        for i in range(self.size):
            sourceIndex = self.sources[i]
            sinkIndex = self.sinks[i]
            if not useStateIndices:
                sourceIndex = self.reverseStateMap[sourceIndex]
                sinkIndex = self.reverseStateMap[sinkIndex]
            labelIndex = self.reverseLabelMap[self.labels[i]]
            transitions.append((sourceIndex, sinkIndex, labelIndex))
        return transitions


def stateCodeFromSet(set):
    code = 0
    for state in set:
        code = code + (1L << state)
    return code

def stateCodeToSet(code):
    set = []
    index, bitmask = 0, 1L
    while code:
        if code & bitmask:
            set.append(index)
            code = code & ~bitmask
        index, bitmask = index + 1, bitmask << 1
    return set


DETERMINITION_PROGRESS_TRIGGER = None   # Higher than this prints progress to stdout
DETERMINATION_CUTOFF = None # Higher than this returns (incorrectly, but useful for profiling)

def determinize(states0, alphabet, transitions0, initial0, finals0, epsilonClosure):
    from FSA import constructLabelMap
    progress = 0
    transitions = []
    stateCodes, index = [stateCodeFromSet(epsilonClosure(initial0))], 0
    transitions = TransitionSet()
    while index < len(stateCodes):
        if DETERMINATION_CUTOFF and index > DETERMINATION_CUTOFF:
            break
        stateCode, index = stateCodes[index], index + 1
        stateSet = stateCodeToSet(stateCode)
        if DETERMINITION_PROGRESS_TRIGGER and len(stateCodes) > DETERMINITION_PROGRESS_TRIGGER:
            progress = 1
            print 'NumFSAUtils:', index, 'of', len(stateCodes)
        localTransitions = filter(lambda (s0,s1,l), set=stateSet:l and s0 in set, transitions0)
        if localTransitions:
            localLabels = map(lambda(_,__,label):label, localTransitions)
            labelMap = constructLabelMap(localLabels, alphabet)
            labelTargets = {}
            for _, s1, l1 in localTransitions:
                for label, positives in labelMap:
                    if l1 in positives:
                        successorStates = labelTargets[label] = labelTargets.get(label) or []
                        for s2 in epsilonClosure(s1):
                            if s2 not in successorStates:
                                successorStates.append(s2)
            for label, successorStates in labelTargets.items():
                successorCode = stateCodeFromSet(successorStates)
                transitions.append((stateCode, successorCode, label))
                if successorCode not in stateCodes:
                    stateCodes.append(successorCode)
    finalStates = []
    for stateCode in stateCodes:
        if filter(lambda s,finalStates=finals0:s in finalStates, stateCodeToSet(stateCode)):
            finalStates.append(stateCode)
    f = transitions.stateIndex
    tuple = map(f, stateCodes), alphabet, transitions.toList(useStateIndices=1), f(stateCodes[0]), map(f, finalStates)
    if progress:
        print 'exiting'
    return tuple
