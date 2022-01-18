from androguard.core.bytecodes.dvm import EncodedMethod
from networkx import DiGraph

from ReflectionUtils import ReflectionNode


def transferDad2DiGraph(dad) -> DiGraph:
    graph = DiGraph()
    for e in dad.edges:
        for n in dad.edges[e]:
            graph.add_edge(e, n)

    for e in dad.catch_edges:
        for n in dad.catch_edges[e]:
            graph.add_edge(e, n)

    return graph


def find_by_classname(classname, name, Graph, dx) -> EncodedMethod:
    for n in Graph.nodes:
        if isinstance(n, EncodedMethod):
            if n.get_class_name() == classname and n.get_name() == name:
                return n

    # 如果n没找到
    l = dx.find_methods(classname=classname, methodname=name)
    for m in l:
        return m.get_method()


def find_by_ReflectionNode(reflection_node: ReflectionNode, Graph, dx) -> EncodedMethod:
    return find_by_classname(transfer_classname(reflection_node.to_m.class_name), reflection_node.to_m.method_name,
                             Graph, dx)


def transfer_classname(classname: str):
    t = 'L' + classname.replace('.', '/', -1)
    return t


def traverse_subtree(node,graph, reflection):
    # 层序遍历
    visit_queue = [node]
    reflection_set = set()

    current_method = node
    while len(visit_queue) > 0:
        successors = list(graph.successors(node))
        current_method = visit_queue.pop(0)

        # 添加邻接点，并去除反射函数
        for n in successors:
            if n in reflection:
                continue
            visit_queue.push(n)



