import matplotlib.pyplot as plt
import networkx as nx
import re
from androguard.core.analysis.analysis import ExternalMethod, MethodAnalysis
from androguard.core.bytecodes.dvm import EncodedMethod
from androguard.decompiler.dad.basic_blocks import BasicBlock
from androguard.decompiler.dad.dast import JSONWriter
from androguard.decompiler.dad.decompile import DvMethod
from androguard.decompiler.dad.instruction import InvokeStaticInstruction, AssignExpression, Constant, \
    InvokeInstruction, InvokeDirectInstruction
from androguard.misc import AnalyzeAPK
import androguard.decompiler.dad.graph as G

from ReflectionUtils import ReflectionNode

# a, d, dx = AnalyzeAPK("D:\\Codes\\Android\\ReflectionTest\\app\\build\\outputs\\apk\\debug\\app-debug.apk")
# MCG = dx.get_call_graph(classname="Lcom/buct/dp/reflectiontest/ReflectionNodes/*")
from utils import transferDad2DiGraph, find_by_ReflectionNode

a, d, dx = AnalyzeAPK("D:\\Codes\\Python\\AndroGuardTest\\apps\\SharedPreferences1.apk")
MCG = dx.get_call_graph(classname="Ledu/mit/shared_preferences/*")

PCG = MCG


def draw_MCG(internal, external, reflection):
    pos = nx.spiral_layout(MCG)
    plt.figure(dpi=400, frameon=False)
    nx.draw_networkx_nodes(MCG, pos=pos, node_color='r', nodelist=internal, node_shape='o')
    nx.draw_networkx_nodes(MCG, pos=pos, node_color='b', nodelist=external, node_shape='o')
    nx.draw_networkx_nodes(MCG, pos=pos, node_color='g', nodelist=reflection, node_shape='o')
    nx.draw_networkx_edges(MCG, pos, edge_color='k')
    nx.draw_networkx_labels(MCG, pos=pos,
                            labels={x: "{} {}".format(x.get_class_name().split('/')[-1], x.get_name()) for x in
                                    MCG.nodes},
                            font_size=4)
    plt.draw()
    plt.show()


def draw_PCG(internal, external, cfg_nodes, catch_edges):
    labels = {}
    for x in PCG.nodes:
        if isinstance(x, BasicBlock):
            labels[x] = "CFG:{} {}".format(x.__class__.__name__, x.name)
        else:
            labels[x] = "{} {}".format(x.get_class_name().split('/')[-1], x.get_name())

    plt.figure(dpi=600, frameon=False)
    pcg_pos = nx.spring_layout(PCG)
    nx.draw_networkx_nodes(PCG, pos=pcg_pos, node_color='r', nodelist=internal, node_shape='o')
    # nx.draw_networkx_nodes(PCG, pos=pcg_pos, node_color='b', nodelist=external, node_shape='o')
    nx.draw_networkx_nodes(PCG, pos=pcg_pos, node_color='c', nodelist=cfg_nodes, node_shape='o')
    nx.draw_networkx_edges(PCG, pcg_pos, edge_color='k')
    nx.draw_networkx_edges(PCG, pcg_pos, edgelist=catch_edges, edge_color='orange', style="dashed")
    nx.draw_networkx_labels(PCG, pos=pcg_pos, labels=labels, font_size=4)
    # nx.write_gexf(PCG, 'C:\\Users\\12990\\Desktop\\deploma-project\\Images\\PCG.gexf')
    plt.draw()
    plt.show()


# 组合MCG和CFG
def addCFG(ref_m, cfg_entry, mcg, cfg):
    nodes = cfg.nodes
    edges = cfg.edges
    for n in nodes:
        mcg.add_node(n)

    for e in edges:
        mcg.add_edge(e[0], e[1])

    mcg.add_edge(ref_m, cfg_entry)


def getReflectionNode(node, reflection_nodes: list, reflection):
    if not isinstance(node, EncodedMethod):
        return
    if visit_Dict[node]:
        return

    visit_Dict[node] = True
    neighbors = list(MCG.neighbors(node))
    for n in neighbors:
        if n in reflection:
            # 子节点是反射方法
            if len(reflection_nodes) == 0:
                reflection_nodes.append(ReflectionNode())

            vmap = {}
            exception_list = []
            dx_method = dx.get_method(node)
            blc = dx_method.get_basic_blocks()
            CFG = G.construct(blc.get_basic_block_pos(0), vmap, exception_list)
            cfg_start = CFG.entry
            CFG = transferDad2DiGraph(CFG)

            var_map = {}
            continue_loop = True
            node_queue = [cfg_start]
            # 防止有环的存在
            node_visit = {}
            for n in CFG.nodes:
                cfg_nodes.append(n)
                node_visit[n] = False
            while continue_loop:
                cfg_node_neighbors = CFG.neighbors(node_queue[0])
                for cfg_node in cfg_node_neighbors:
                    if not node_visit[cfg_node]:
                        node_queue.append(cfg_node)

                tmp_node = node_queue.pop(0)
                node_visit[tmp_node] = True
                for nn in tmp_node.ins:
                    if isinstance(nn,AssignExpression):
                        print("Hello ~")
                # for nn in tmp_node.ins:
                #     if isinstance(nn, AssignExpression):
                #         if isinstance(nn.rhs, Constant):
                #             var_map[nn.lhs] = nn.rhs.cst
                #         if isinstance(nn.rhs, InvokeStaticInstruction) or isinstance(nn.rhs, InvokeInstruction) \
                #                 or isinstance(nn.rhs, InvokeDirectInstruction):
                #             if nn.rhs.name == 'forName' or nn.rhs.name == 'loadClass':
                #                 if reflection_nodes[-1].class_name != var_map[nn.rhs.args[0]] \
                #                         and reflection_nodes[-1].class_name is not None:
                #                     new_node = ReflectionNode()
                #                     new_node.class_name = var_map[nn.rhs.args[0]]
                #                     reflection_nodes.append(new_node)
                #                 else:
                #                     reflection_nodes[-1].class_name = var_map[nn.rhs.args[0]]
                #             elif nn.rhs.name == 'getMethod':
                #                 reflection_nodes[-1].method_name = var_map[nn.rhs.args[0]]
                #                 # 获取参数个数以及类型
                #             elif nn.rhs.name == 'invoke':
                #                 # 连接块儿与函数
                #                 if reflection_nodes[-1].judgeQualified():
                #                     if len(reflection_nodes) >= 2 and reflection_nodes[-1] == reflection_nodes[-2]:
                #                         break
                #
                #                     em = find_by_ReflectionNode(reflection_nodes[-1], MCG, dx)
                #                     MCG.add_edge(tmp_node, em)
                #                     addCFG(node, cfg_start, MCG, CFG)  # 将CFG与MCG组合

                if len(node_queue) == 0:
                    continue_loop = False
            break
        else:
            getReflectionNode(n, reflection_nodes, reflection)


visit_Dict = {}
catch_edges = []  # 异常捕捉边
cfg_nodes = []


# 图片后处理，清理节点
def post_process(node_list:list,another_list:list, pcg):

    for n in node_list:
        pcg.remove_node(n)


    # 清理一下度为0的节点
    for nodes in list(pcg.degree):
        if nodes[1] == 0:
            pcg.remove_node(nodes[0])
            if nodes[0] in another_list:
                another_list.remove(nodes[0])


def genPCG():
    internal = []
    external = []
    reflection = []

    for n in MCG.nodes:
        visit_Dict[n] = False

        if (isinstance(n, ExternalMethod)) and (
                n.get_name() == "getMethod" or n.get_name() == "forName" or n.get_name() == "loadClass" \
                or n.get_name() == "invoke" or n.get_name() == "newInstance"):
            reflection.append(n)
        elif isinstance(n, ExternalMethod):
            external.append(n)
        else:
            internal.append(n)

    draw_MCG(internal, external, reflection)

    reflection_nodes = []

    for n in list(MCG.in_degree):
        # 入度为0
        if n[1] == 0:
            # getReflectionNode(n[0], reflection_nodes, reflection)
            # 针对该节点执行遍历

            pass

    PCG = MCG
    post_process(external+reflection,internal, PCG)
    draw_PCG(internal, external, cfg_nodes, catch_edges)

# 路径提取
def searchPath():
    print("nothing")


if __name__ == '__main__':
    genPCG()
    searchPath()
