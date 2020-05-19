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
    icon = "icons/add.png"
    op_code = OP_NODE_ADD
    op_title = "Вершина"
    content_label = "+"
    content_label_objname = "calc_node_bg"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.eval()

    def initInnerClasses(self):
        self.content = NodeStandContent(self)
        self.grNode = CalcGraphicsNode(self)
        #self.content.edit.textChanged.connect(self.onInputChanged)



    def evalOperation(self, input1, input2):
        return input1 + input2


# way how to register by function call
# register_node_now(OP_NODE_ADD, CalcNode_Add)
