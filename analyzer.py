from classes.vertices.input import CalcNode_Input
from classes.vertices.operations import CalcNode_Add
from classes.vertices.output import CalcNode_Output
from itertools import permutations
from _collections import OrderedDict

CORE_W = 0
CORE_D = 0

class Analyzer():
    visited_nodes = set()

    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def dfs(self, node):
        self.visited_nodes.clear()
        self.doDfs(node)

    def doDfs(self, node):
        self.visited_nodes.add(node)
        assert(len(node.outputs) == 1 or len(node.outputs) == 0)
        # print("node", str(node.content.edit.text()), "outputs", len(node.outputs))
        if len(node.outputs) == 1:
            for edge in node.outputs[0].edges:
                toNode = edge.end_socket.node
                if toNode not in self.visited_nodes:
                    self.doDfs(toNode)

    def dfsCycle(self, node):
        self.colors = {}
        self.cycles = {}
        self.cycles_edges = {}
        self.parents = {}
        self.doDfsCycle(node)

    # def getCycle(self, start, end):
    #     cycle = []
    #     node = end
    #
    #     print(f"start {start.content.edit.text()}, end {end.content.edit.text()}")
    #     for child in self.parents:
    #         parents = self.parents[child]
    #         print(f"child {child.content.edit.text()} <- ", end="")
    #         print(",".join([parent.content.edit.text() for parent in parents]))
    #     while node != start:
    #         print(f"curr node {node.content.edit.text()}")
    #         cycle.append(node)
    #         node = self.parents[node].pop()
    #     cycle.append(node)
    #     self.parents[node].pop()
    #     cycle.reverse()
    #     return cycle
    #
    # def doDfsCycle(self, node):
    #     print("goto", node.content.edit.text())
    #     assert (len(node.outputs) == 1 or len(node.outputs) == 0)
    #     self.colors[node.id] = 1
    #     if len(node.outputs) == 1:
    #         for edge in node.outputs[0].edges:
    #             toNode = edge.end_socket.node
    #             self.parents.setdefault(toNode, list()).append(node)
    #             if self.colors.setdefault(toNode.id, 0) == 0:
    #                 self.doDfsCycle(toNode)
    #             elif self.colors[toNode.id] == 1:
    #                 cycle = self.getCycle(toNode, node)
    #                 self.cycles.setdefault(toNode, list()).append(cycle)
    #             print(f"return to {node.content.edit.text()}")
    #     self.colors[node.id] = 0

    def getCycle(self, start, path, edgePath):
        cycle = [start]
        cycleEdge = []
        idx = len(cycleEdge) - 1
        # print(f"start {start.content.edit.text()}, end {end.content.edit.text()}")
        # print(",".join([node.content.edit.text() for node in path]))
        for node in path[::-1]:
            cycle.append(node)
            cycleEdge.append(edgePath[idx])
            idx -= 1
            if node == start:
                break

        assert(idx == -1)

        cycle.reverse()
        cycleEdge.reverse()
        return cycle, cycleEdge

    def doDfsCycle(self, node, path=list(), edgePath=list()):
        print("goto", node.content.edit.text(), "path", ",".join([node.content.edit.text() for node in path]))
        assert (len(node.outputs) == 1 or len(node.outputs) == 0)
        self.colors[node.id] = 1
        pathCopy = path.copy()
        pathCopy.append(node)
        print("pathCopy", ",".join([node.content.edit.text() for node in pathCopy]))
        if len(node.outputs) == 1:
            for edge in node.outputs[0].edges:
                toNode = edge.end_socket.node
                edgePathCopy = edgePath.copy()
                edgePathCopy.append(edge)
                self.parents.setdefault(toNode, list()).append(node)
                if self.colors.setdefault(toNode.id, 0) == 0:
                    self.doDfsCycle(toNode, pathCopy, edgePathCopy)
                elif self.colors[toNode.id] == 1:
                    cycle, cycleEdges = self.getCycle(toNode, pathCopy, edgePathCopy)
                    self.cycles.setdefault(toNode, list()).append(cycle)
                    self.cycles_edges.setdefault(toNode, list()).append(cycle)
                print(f"return to {node.content.edit.text()}", "path", ",".join([node.content.edit.text() for node in path]))
        self.colors[node.id] = 0


    def checkCorrectness(self):
        start_nodes = [node for node in self.nodes if isinstance(node, CalcNode_Input)]
        if len(start_nodes) != 1:
            return False, f"Начальных вершин {len(start_nodes)}"

        self.dfs(start_nodes[0])
        if len(self.visited_nodes) != len(self.nodes):
            return False, f"Граф несвязный"

        # if there is not way to output vertex from vertex then graph is incorrect
        for node in self.nodes:
            if not isinstance(node, CalcNode_Output) and not isinstance(node, CalcNode_Input):
                self.dfs(node)
                outputReachability = False
                for visited_node in self.visited_nodes:
                    if isinstance(visited_node, CalcNode_Output):
                        outputReachability = True
                        break
                if not outputReachability:
                    return False, f"Из вершины {str(node.content.edit.text())} нет пути до конца"

        return True, None

    def is_correct_brackets(brackets_trace):
        brackets = brackets_trace
        while '()' in brackets:
            brackets = brackets.replace('()', '')
        return not brackets

    def proceedCycles(self, cycles, ):
        cycleCollectedStrings = (list(), list())

        a = set()

        for idx, cycle in enumerate(cycles):
            # if len(cycle) == 2:
            #     assert(cycle[0] == cycle[1])
            #     node = cycle[0]
            #     for edge in node.outputs[0].edges:
            #         if node == edge.end_socket.node and edge not in a:
            #             cycleCollectedStrings[0].append(edge.edge_bracket)
            #             cycleCollectedStrings[1].append(edge.edge_label)
            #             a.add(edge)
            #     continue

            for edge in edgePath:
                self.visited_nodes.add(edge.end_socket.node)
                cycleCollectedStrings[0].append(currentEdge.edge_bracket)
                cycleCollectedStrings[1].append(currentEdge.edge_label)

            # for nodeFrom, nodeTo in zip(cycle[:-1], cycle[1:]):
            #     # print(f"from-to1 {nodeFrom.content.edit.text()}-{nodeTo.content.edit.text()}")
            #     currentEdge = None
            #     for edge in nodeFrom.outputs[0].edges:
            #         # print(f"edge in cycle {edge.end_socket.node.content.edit.text()}, label {edge.edge_label}, bool {nodeTo == edge.end_socket.node}")
            #         if nodeTo == edge.end_socket.node:
            #             currentEdge = edge
            #     assert currentEdge is not None
            #
            #     self.visited_nodes.add(nodeTo)
            #     cycleCollectedStrings[0].append(currentEdge.edge_bracket)
            #     cycleCollectedStrings[1].append(currentEdge.edge_label)
            #     # print(f"from-to2 {nodeFrom.content.edit.text()}-{nodeTo.content.edit.text()} label {currentEdge.edge_label}")


            # TODO: maybe bug
            for remainingCycle in cycles[idx + 1:]:
                for node in remainingCycle:
                    self.visited_nodes.discard(node)

        for cycle in cycles:
            for node in cycle:
                self.visited_nodes.discard(node)

        return cycleCollectedStrings


    def dfsSubset(self, node):
        # print(f"goto {node.content.edit.text()}")
        self.visited_nodes.add(node)
        assert (len(node.outputs) == 1 or len(node.outputs) == 0)
        # print("node", str(node.content.edit.text()), "outputs", len(node.outputs))
        if len(node.outputs) == 0:  # output node
            print("Got this:", self.collectedStrings)
        else:
            if node in self.cycles:
                # print(self.cycleNumbersMap)
                # for cycle in self.cycles[node]:
                #     print(f"Цикл от {node.content.edit.text()} содержит вершины: " + ' -> '.join(
                #         [node.content.edit.text() for node in cycle]))
                # print("subset: ", self.subset)

                processableCycles = list()
                for idx, cycle in self.cycleNumbersMap[node]:
                    if idx in self.subset:
                        processableCycles.append(cycle)

                for permutation in permutations(processableCycles, len(processableCycles)):
                    # print("I'm in permutation cycle, wtf")
                    # print(f"Processable cycles permutation {len(permutation)}:")
                    # for cycle in permutation:
                    #     print(f"Цикл из перестановки от {node.content.edit.text()} содержит вершины: " + ' -> '.join(
                    #         [node.content.edit.text() for node in cycle]))

                    cycleCollectedStrings = self.proceedCycles(permutation)
                    self.collectedStrings = (
                        self.collectedStrings[0] + cycleCollectedStrings[0],
                        self.collectedStrings[1] + cycleCollectedStrings[1]
                    )
                    self.visited_nodes.add(node)

                    # print("go to deep dfs cnt", cnt)
                    for edge in node.outputs[0].edges:
                        toNode = edge.end_socket.node
                        # print(f" if from {node.content.edit.text()} try {toNode.content.edit.text()}")
                        # print("visted:", ", ".join([node.content.edit.text() for node in self.visited_nodes]))
                        self.collectedStrings[0].append(edge.edge_bracket)
                        self.collectedStrings[1].append(edge.edge_label)
                        if toNode not in self.visited_nodes:
                            self.dfsSubset(toNode)
                            # print(f"return to {node.content.edit.text()}")
                        for item in self.collectedStrings:
                            item.pop()
                    # print("return from deep dfs cnt", cnt)
                    self.collectedStrings = (
                        self.collectedStrings[0][: len(self.collectedStrings[0]) - len(cycleCollectedStrings[0])],
                        self.collectedStrings[1][: len(self.collectedStrings[1]) - len(cycleCollectedStrings[1])]
                    )
            else:
                for edge in node.outputs[0].edges:
                    toNode = edge.end_socket.node
                    # print(f" else from {node.content.edit.text()} try {toNode.content.edit.text()}")
                    # print("visted:", ", ".join([node.content.edit.text() for node in self.visited_nodes]))
                    self.collectedStrings[0].append(edge.edge_bracket)
                    self.collectedStrings[1].append(edge.edge_label)
                    if toNode not in self.visited_nodes:
                        self.dfsSubset(toNode)
                    for item in self.collectedStrings:
                        item.pop()

        self.visited_nodes.remove(node)

    def processSubset(self):
        self.visited_nodes.clear()
        self.collectedStrings = (list(), list())
        self.dfsSubset(self.start_node)

    def generateSubset(self, k):
        if k == self.cyclesNumber:
            self.processSubset()
        else:
            self.generateSubset(k + 1)
            self.subset.add(k)
            self.generateSubset(k + 1)
            self.subset.remove(k)

    def buildCore(self):
        self.cyclesNumber = 0
        self.subset = set()
        self.cycleNumbersMap = {}

        cyclesNumber = 0
        for node in self.cycles:
            self.cyclesNumber += len(self.cycles[node])

            self.cycleNumbersMap[node] = list()
            for idx, cycle in enumerate(self.cycles[node]):
                self.cycleNumbersMap[node].append((cyclesNumber, cycle))
                cyclesNumber += 1

        print("cycles number =", self.cyclesNumber)

        self.generateSubset(0)

    def checkCycles(self, node = 0, wd = 0):
        fin_str = ''
        for node in self.nodes:
            if isinstance(node, CalcNode_Input):
                self.start_node = node
        self.dfsCycle(self.start_node)
        for node in self.cycles:
            for cycle in self.cycles[node]:
                str = f"Цикл от {node.content.edit.text()} содержит вершины: " + ' -> '.join([node.content.edit.text() for node in cycle])
                print(str)
                fin_str += str + ';\n'
        return fin_str[:-2]+'.'
        #self.buildCore()

    def sentence(self, node, brackets_trace, labels_trace, wd = 0):
        #print('shalava', self.core_visited_nodes)
        self.core_visited_nodes.add(node)
        assert(len(node.inputs) == 1 or len(node.inputs) == 0)
        # print("node", str(node.content.edit.text()), "outputs", len(node.outputs))
        if len(node.inputs) == 1:
            for edge in node.inputs[0].edges:
                toNode = edge.start_socket.node
                #print(toNode)
                brackets_trace += edge.edge_bracket
                print(brackets_trace)
                labels_trace += edge.edge_label
                print(labels_trace)
                if toNode not in self.core_visited_nodes:
                    self.sentence(toNode, brackets_trace, labels_trace)

    def sentencesCore(self, wd = 0):
        self.core_visited_nodes = set()
        self.end_nodes = set()
        label_trace_core = []
        bracket_trace_core = []
        labels = brackets = ''
        for node in self.nodes:
            if isinstance(node, CalcNode_Input):
                self.dfs(node)
                for visited_node in self.visited_nodes:
                    if isinstance(visited_node, CalcNode_Output):
                        self.end_nodes.add(visited_node)
                for visited_node in self.visited_nodes:
                    if isinstance(visited_node, CalcNode_Output) and (visited_node in self.end_nodes):
                        self.sentence(visited_node, brackets, labels)
                        print('labels path:', labels[::-1])
                        print('brackets path:', brackets[::-1])
                        self.end_nodes.remove(visited_node)
        return True, labels[::-1], brackets[::-1]

    def DeterminedGraph(self):
        pass


