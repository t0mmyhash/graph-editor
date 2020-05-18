from PyQt5.QtCore import *
from misc.register_vertices import *
from classes.vertex_base import *


class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("E", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setGeometry(60 / 2 - 22, 60 / 2 - 17, 40, 30)
        self.edit.setObjectName(self.node.content_label_objname)


@register_node(OP_NODE_OUTPUT)
class CalcNode_Output(CalcNode):
    icon = "icons/out.png"
    op_code = OP_NODE_OUTPUT
    op_title = "Конечная вершина"
    content_label_objname = "calc_node_output"

    def __init__(self, scene):
        super().__init__(scene, inputs=[0], outputs=[])

    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.grNode = CalcGraphicsNode(self)

    # def evalImplementation(self):
    #     input_node = self.getInput(0)
    #     if not input_node:
    #         self.grNode.setToolTip("Input is not connected")
    #         self.markInvalid()
    #         return
    #
    #     val = input_node.eval()
    #
    #     if val is None:
    #         self.grNode.setToolTip("Input is NaN")
    #         self.markInvalid()
    #         return
    #
    #     self.content.lbl.setText("%d" % val)
    #     self.markInvalid(False)
    #     self.markDirty(False)
    #     self.grNode.setToolTip("")
    #
    #     return val
