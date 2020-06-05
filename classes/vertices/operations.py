from PyQt5.QtCore import *
from misc.register_vertices import *
from classes.vertex_base import *
from misc.utils import dumpException

class NodeStandContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("A", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setGeometry(60 / 2 - 22, 60 / 2 - 17, 40, 30)
        self.edit.setObjectName(self.node.content_label_objname)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res

@register_node(OP_NODE_ADD)
class CalcNode_Add(CalcNode):
    icon = "icons/left.png"
    op_code = OP_NODE_ADD
    op_title = "Вершина (left in)"
    content_label = "A"
    content_label_objname = "calc_node_bg"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()

    def initInnerClasses(self):
        self.content = NodeStandContent(self)
        self.grNode = CalcGraphicsNode(self)
        #self.content.edit.textChanged.connect(self.onInputChanged)

    def evalOperation(self, input1, input2):
        return input1 + input2


@register_node(OP_NODE_ADD_RIGHT_IN)
class CalcNode_Add_Right_In(CalcNode):
    icon = "icons/right.png"
    op_code = OP_NODE_ADD_RIGHT_IN
    op_title = "Вершина (right in)"
    content_label = "C"
    content_label_objname = "calc_node_right_input"

    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()

    def initInnerClasses(self):
        self.content = NodeStandContent(self)
        self.grNode = CalcGraphicsNode(self)
        #self.content.edit.textChanged.connect(self.onInputChanged)

    def evalOperation(self, input1, input2):
        return input1 + input2
