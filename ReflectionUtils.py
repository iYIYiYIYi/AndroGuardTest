#################################################
# 反射节点处理
# 一个完整的反射点由 { forName()/loadClass() | getMethod() | newInstance() | invoke() } 确定
# 反射点中包含 {
#            | class_name:str        :类名
#            | method_name:str       :方法名
#            | params:(types_arr)    :参数类型元组
#            }
################################################
REFLECTION_SET = {['forName', 'loadClass', 'getMethod', 'newInstance', 'invoke']}


# 处理字节码语句
class ExpressionNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right


# 处理方法
class MethodNode:
    def __init__(self, class_name: str, method_name: str, args: ()):
        self.expression_dict = {}
        self.class_name = class_name
        self.method_name = method_name
        self.args = args

    def __eq__(self, other):
        if not isinstance(other, MethodNode):
            return False
        if self.class_name == other.class_name and \
                self.method_name == other.method_name and \
                self.args == other.args:
            return True


# 反射节点
class ReflectionNode:
    def __init__(self, from_m: MethodNode, to_m: MethodNode):
        self.from_m = from_m
        self.to_m = to_m

    def __eq__(self, other):
        if not isinstance(other, ReflectionNode):
            return False
        if self.to_m == other.to_m and \
                self.from_m == other.from_m:
            return True
