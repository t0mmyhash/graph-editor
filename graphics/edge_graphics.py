import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


EDGE_CP_ROUNDNESS = 100     #: Bezier controll point distance on the line
arrowSize = 13
Pi = 3.14
ishAngle = Pi/6

class QDMGraphicsEdge(QGraphicsPathItem):
    """Base class for Graphics Edge"""
    def __init__(self, edge:'Edge', parent:QWidget=None):
        """
        :param edge: reference to :class:`~nodeeditor.node_edge.Edge`
        :type edge: :class:`~nodeeditor.node_edge.Edge`
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance attributes:

            - **edge** - reference to :class:`~nodeeditor.node_edge.Edge`
            - **posSource** - ``[x, y]`` source position in the `Scene`
            - **posDestination** - ``[x, y]`` destination position in the `Scene`
        """
        super().__init__(parent)

        self.edge = edge

        # init our flags
        self._last_selected_state = False
        self.hovered = False

        # init our variables
        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self.text_pos_x = 0
        self.text_pos_y = 0


        self.initAssets()
        self.initUI()

    def initUI(self):
        """Set up this ``QGraphicsPathItem``"""
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color = self._default_color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        self._color_hovered = QColor("#FF37A6FF")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(2.5)
        self._pen_selected.setWidthF(5.0)
        self._pen_dragging.setWidthF(2.5)
        self._pen_hovered.setWidthF(6.0)
        self._arrowBrush = QBrush(self._default_color)


    def changeColor(self, color):
        """Change color of the edge from string hex value '#00ff00'"""
        # print("^Called change color to:", color.red(), color.green(), color.blue(), "on edge:", self.edge)
        self._color = QColor(color) if type(color) == str else color
        self._pen = QPen(self._color)
        self._pen.setWidthF(3.0)

    def setColorFromSockets(self) -> bool:
        """Change color according to connected sockets. Returns ``True`` if color can be determined"""
        socket_type_start = self.edge.start_socket.socket_type
        socket_type_end = self.edge.end_socket.socket_type
        if socket_type_start != socket_type_end: return False
        self.changeColor(self.edge.start_socket.grSocket.getSocketColor(socket_type_start))

    def onSelected(self):
        """Our event handling when the edge was selected"""
        self.edge.scene.grScene.itemSelected.emit()

    def doSelect(self, new_state:bool=True):
        """Safe version of selecting the `Graphics Node`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state: self.onSelected()

    def mouseReleaseEvent(self, event):
        """Overriden Qt's method to handle selecting and deselecting this `Graphics Edge`"""
        super().mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.edge.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def setSource(self, x:float, y:float):
        """ Set source point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        """
        self.posSource = [x, y]

    def setDestination(self, x:float, y:float):
        """ Set destination point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        """
        self.posDestination = [x, y]

    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        """Returns ``QPainterPath`` representation of this `Edge`

        :return: path representation
        :rtype: ``QPainterPath``
        """
        return self.calcPath()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Qt's overriden method to paint this Graphics Edge. Path calculated in :func:`~nodeeditor.node_graphics_edge.QDMGraphicsEdge.calcPath` method"""
        self.setPath(self.calcPath())

        painter.setBrush(Qt.NoBrush)
        angle = (Pi * 2)  # - ishAngle TODO : angles

        arrowP1 = QPointF(
            QPointF(self.posDestination[0], self.posDestination[1]) - QPointF(math.sin(angle + Pi / 3) * arrowSize,
                                                                              math.cos(angle + Pi / 3) * arrowSize) * (
                                                                              -1 if self.posDestination[0] <= self.posSource[0] else 1))
        arrowP2 = QPointF(
            QPointF(self.posDestination[0], self.posDestination[1]) - QPointF(math.sin(angle + Pi - Pi / 3) * arrowSize,
                                                                              math.cos(angle + Pi - Pi / 3) * arrowSize) * (
                                                                              -1 if self.posDestination[0] <= self.posSource[0] else 1))
        # painter.setBrush(self._arrowBrush)
        if self.hovered and self.edge.end_socket is not None:
            painter.setPen(self._pen_hovered)
            painter.drawPath(self.path())
            painter.drawLine(QPointF(self.posDestination[0], self.posDestination[1]), arrowP1)
            painter.drawLine(QPointF(self.posDestination[0], self.posDestination[1]), arrowP2)

        if self.edge.end_socket is not None:
            rect_label = QRectF(self.text_pos_x -5,
                                self.text_pos_y + 20 * (1 if (self.edge.edge_curve) % 2 else -2) - 10 * (
                                    1 if (self.edge.edge_curve) % 2 else 0) + 13 * (self.edge.edge_curve // 2) * (
                                    1 if (self.edge.edge_curve) % 2 else -1)
                                , 10, 15)

            rect_bracket = QRectF(self.text_pos_x -5,
                                  self.text_pos_y + 20 * (2 if (self.edge.edge_curve) % 2 else -1) - 10 * (
                                      1 if (self.edge.edge_curve) % 2 else 0) + 13 * (self.edge.edge_curve // 2) * (
                                      1 if (self.edge.edge_curve) % 2 else -1)
                                , 10, 15)
            if self.edge.end_socket.node != self.edge.start_socket.node:
                rect_label = QRectF(self.text_pos_x + 3, self.text_pos_y - 15, 10, 15)
                rect_bracket = QRectF(self.text_pos_x - 13, self.text_pos_y + 5, 10, 15)

            painter.drawText(rect_label, Qt.AlignCenter, self.edge.edge_label)
            painter.drawText(rect_bracket, Qt.AlignCenter, self.edge.edge_bracket)

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)

        painter.drawPath(self.path())
        painter.drawLine(QPointF(self.posDestination[0], self.posDestination[1]), arrowP1)
        painter.drawLine(QPointF(self.posDestination[0], self.posDestination[1]), arrowP2)

    def intersectsWith(self, p1:QPointF, p2:QPointF) -> bool:
        """Does this Graphics Edge intersect with line between point A and point B ?

        :param p1: point A
        :type p1: ``QPointF``
        :param p2: point B
        :type p2: ``QPointF``
        :return: ``True`` if this `Graphics Edge` intersects
        :rtype: ``bool``
        """
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)

    def calcPath(self) -> QPainterPath:
        """Will handle drawing QPainterPath from Point A to B

        :returns: ``QPainterPath`` of the edge connecting `source` and `destination`
        :rtype: ``QPainterPath``
        """
        raise NotImplemented("This method has to be overriden in a child class")


class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    """Direct line connection Graphics Edge"""
    def calcPath(self) -> QPainterPath:
        """Calculate the Direct line connection

        :returns: ``QPainterPath`` of the direct line
        :rtype: ``QPainterPath``
        """
        s = self.posSource
        d = self.posDestination
        if (s[0] >= 0) and (d[0] >= 0):
            self.text_pos_x = ((d[0] - s[0]) if (d[0] >= s[0]) else (s[0] - d[0])) / 2 + (
                s[0] if (d[0] >= s[0]) else d[0])
        elif (s[0] < 0) and (d[0] >= 0) or (s[0] >= 0) and (d[0] < 0):
            self.text_pos_x = (d[0] + s[0]) / 2
        else:
            self.text_pos_x = ((s[0] - d[0]) if (d[0] >= s[0]) else (d[0] - s[0])) / 2 + (
                d[0] if (d[0] >= s[0]) else s[0])
        # self.text_pos_x = ((d[0] - s[0] * (-1 if s[0] < 0 else 1)) if (d[0] >= s[0]) else (s[0] - d[0] * (-1 if d[0] < 0 else 1))) / 2
        # print(s[0], '.....', self.text_pos_x, '.......', d[0])
        # self.text_pos_y = ((self.posDestination[1] - self.posSource[1]) if (d[1] >= s[1]) else (self.posSource[1] - self.posDestination[1])) / 2

        if (s[1] >= 0) and (d[1] >= 0):
            self.text_pos_y = ((d[1] - s[1]) if (d[1] >= s[1]) else (s[1] - d[1])) / 2 + (
                d[1] if (s[1] >= d[1]) else s[1])
        elif (s[1] < 0) and (d[1] >= 0) or (s[1] >= 0) and (d[1] < 0):
            self.text_pos_y = (d[1] + s[1]) / 2
        else:
            self.text_pos_y = ((s[1] - d[1]) if (d[1] >= s[1]) else (d[1] - s[1])) / 2 + (
                d[1] if (d[1] >= s[1]) else s[1])

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path


class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    """Cubic line connection Graphics Edge"""
    def calcPath(self) -> QPainterPath:
        """Calculate the cubic Bezier line connection with 2 control points

        :returns: ``QPainterPath`` of the cubic Bezier line
        :rtype: ``QPainterPath``
        """
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.edge.start_socket is not None:
            ssin = self.edge.start_socket.is_input
            ssout = self.edge.start_socket.is_output


            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = (
                    (s[1] - d[1]) / math.fabs(
                        (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS
                cpy_s = (
                    (d[1] - s[1]) / math.fabs(
                        (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
                    )
                ) * EDGE_CP_ROUNDNESS

            if  (self.edge.end_socket is not None):
                if (self.edge.start_socket.node == self.edge.end_socket.node):
                    self.edge.start_socket.node.edges_in_self.add(self.edge.id)
                    cpx_s = (40 + 50*(self.edge.edge_curve // 2)) * (1 if (s[0] > d[0]) else -1)
                    cpy_s = (100 + 50*(self.edge.edge_curve // 2)) * (-1 if self.edge.edge_curve % 2 else 1)
                    cpy_d  = (100 + 50*(self.edge.edge_curve // 2)) * (-1 if self.edge.edge_curve % 2 else 1)
                    cpx_d = (-40 - 50*(self.edge.edge_curve // 2)) * (1 if (s[0] > d[0]) else -1)
                    ss_x = self.edge.start_socket.node.grNode.pos().x()
                    ss_y = self.edge.start_socket.node.grNode.pos().y()
                    ee_x = self.edge.end_socket.node.grNode.pos().x()
                    ee_y = self.edge.end_socket.node.grNode.pos().x()
                    self.text_pos_x = ss_x + self.edge.start_socket.node.grNode.width / 2
                    self.text_pos_y = s[1] + cpy_d
                else:
                    if (s[0] >= 0) and (d[0] >= 0):
                        self.text_pos_x = ((d[0] - s[0]) if (d[0] >= s[0]) else (s[0] - d[0])) / 2 + (s[0] if (d[0] >= s[0]) else d[0])
                    elif (s[0] < 0) and (d[0] >= 0) or (s[0] >= 0) and (d[0] < 0):
                        self.text_pos_x = (d[0] + s[0]) / 2
                    else:
                        self.text_pos_x = ((s[0] - d[0]) if (d[0] >= s[0]) else (d[0] - s[0])) / 2 + (d[0] if (d[0] >= s[0]) else s[0])
                    #self.text_pos_x = ((d[0] - s[0] * (-1 if s[0] < 0 else 1)) if (d[0] >= s[0]) else (s[0] - d[0] * (-1 if d[0] < 0 else 1))) / 2
                    #print(s[0], '.....', self.text_pos_x, '.......', d[0])
                    #self.text_pos_y = ((self.posDestination[1] - self.posSource[1]) if (d[1] >= s[1]) else (self.posSource[1] - self.posDestination[1])) / 2

                    if (s[1] >= 0) and (d[1] >= 0):
                        self.text_pos_y = ((d[1] - s[1]) if (d[1] >= s[1]) else (s[1] - d[1])) / 2 + (d[1] if (s[1] >= d[1]) else s[1])
                    elif (s[1] < 0) and (d[1] >= 0) or (s[1] >= 0) and (d[1] < 0):
                        self.text_pos_y = (d[1] + s[1]) / 2
                    else:
                        self.text_pos_y = ((s[1] - d[1]) if (d[1] >= s[1]) else (d[1] - s[1])) / 2 + (d[1] if (d[1] >= s[1]) else s[1])

                    #print(s[1], '.....', self.text_pos_y, '.......', d[1])

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))

        path.cubicTo( s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.posDestination[0], self.posDestination[1])

        return path
