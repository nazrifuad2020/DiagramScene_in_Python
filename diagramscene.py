import os
import sys
from PyQt5.QtCore import QMimeData, QRect, QSize, pyqtSignal, QLineF, Qt, QPointF, QRectF, QSizeF, pyqtSlot  
from PyQt5.QtGui import QBrush, QColor, QDrag, QFont, QIcon, QIntValidator, QKeySequence, QPen, QPainterPath, QPainter, QPixmap, QPolygonF, QTransform
from PyQt5.QtWidgets import (QAbstractButton, QAction, QApplication, QButtonGroup, QComboBox, QFontComboBox, QGraphicsItem, QGraphicsTextItem, 
                            QGraphicsLineItem, QGraphicsPolygonItem, QGraphicsScene, 
                            QGraphicsView, QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QMenu, QMessageBox, QSizePolicy, QToolBox, QToolButton, QVBoxLayout, QWidget)

from enum import Enum

import math

DIR_NAME = os.path.dirname(__file__)
InsertTextButton = 10

COLORKEY = {'black': Qt.black, 'white': Qt.white, 'red': Qt.red, 'blue': Qt.blue, 'yellow': Qt.yellow}

class DiagramItem(QGraphicsPolygonItem):
    Type = QGraphicsItem.UserType + 15

    class DiagramType(Enum):
        Step = 0
        Conditional = 1 
        StartEnd = 2 
        Io = 3
    
    def __init__(self, diagramType, contextMenu, parent=None):
        super().__init__(parent=parent)

        path = QPainterPath()

        self.myPolygon = QPolygonF()
        self.arrows = []

        self.myName = ''

        self.widget = None

        self.myDiagramType = diagramType

        self.myContextMenu = contextMenu

        if self.myDiagramType == self.DiagramType.StartEnd:
            path.moveTo(200, 50)
            path.arcTo(150, 0, 50, 50, 0, 90)
            path.arcTo(50, 0, 50, 50, 90, 90)
            path.arcTo(50, 50, 50, 50, 180, 90)
            path.arcTo(150, 50, 50, 50, 270, 90)
            path.lineTo(200, 25)
            self.myPolygon = path.toFillPolygon()
        elif self.myDiagramType == self.DiagramType.Conditional:
            self.myPolygon << QPointF(-100, 0) << QPointF(0, 100) << QPointF(100, 0) << QPointF(0, -100) << QPointF(-100, 0)
        elif self.myDiagramType == self.DiagramType.Step:
            self.myPolygon << QPointF(-100, -100) << QPointF(100, -100) << QPointF(100, 100) << QPointF(-100, 100) << QPointF(-100, -100)
        else:
            self.myPolygon << QPointF(-120, -80) << QPointF(-70, 80) << QPointF(120, 80) << QPointF(70, -80) << QPointF(-120, -80)

        self.setPolygon(self.myPolygon)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def setMyName(self, myName):
        self.myName = myName

    def getMyName(self):
        return self.myName

    def diagramType(self):
        return self.myDiagramType

    def polygon(self):
        return self.myPolygon

    def type(self):
        return self.Type

    def setTextItemOwnership(self, textItem):
        self.textItem = textItem

    def getTextItem(self):
        return self.textItem

    def removeArrow(self, arrow):
        for arr in self.arrows:
            if arr == arrow:
                self.arrows.remove(arr)

    def removeArrows(self):
        # need a copy here since removeArrow() will
        # modify the arrows container
        arrowsCopy = self.arrows.copy()
        for arr in arrowsCopy:
            arr.startItem().removeArrow(arr)
            arr.endItem().removeArrow(arr)
            self.scene().removeItem(arr)

    def addArrow(self, arrow):
        self.arrows.append(arrow)

    def image(self):
        pixmap = QPixmap(250, 250)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.myPolygon)
        painter.end()

        return pixmap

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        self.myContextMenu.exec_(event.screenPos())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arr in self.arrows:
                arr.updatePosition()

        return value

    def mouseDoubleClickEvent(self, mouseEvent):
        if self.myDiagramType == DiagramItem.DiagramType.Conditional:
            if self.widget is None:
                self.widget = QWidget()
                label = QLabel(self.myName + ' is double-clicked')
                font = QFont()
                font.setPointSize(20)
                label.setFont(font)
                layout = QVBoxLayout()
                layout.addWidget(label)
                self.widget.setWindowTitle('Conditional')
                self.widget.setLayout(layout)
            self.widget.show()
        elif self.myDiagramType == DiagramItem.DiagramType.Io:
            if self.widget is None:
                self.widget = QWidget()
                label = QLabel(self.myName + ' is double-clicked')
                font = QFont()
                font.setPointSize(20)
                label.setFont(font)
                layout = QVBoxLayout()
                layout.addWidget(label)
                self.widget.setWindowTitle('Io')
                self.widget.setLayout(layout)
            self.widget.show()
        else:
            if self.widget is None:
                self.widget = QWidget()
                label = QLabel(self.myName + ' is double-clicked')
                font = QFont()
                font.setPointSize(20)
                label.setFont(font)
                layout = QVBoxLayout()
                layout.addWidget(label)
                self.widget.setWindowTitle('Step')
                self.widget.setLayout(layout)
            self.widget.show()

        super().mouseDoubleClickEvent(mouseEvent)

    
class Arrow(QGraphicsLineItem):
    Type = QGraphicsItem.UserType + 4
    
    def __init__(self, startItem, endItem, parent=None):
        super().__init__(parent=parent)

        self.myStartItem = startItem
        self.myEndItem = endItem
        
        self.arrowHead = QPolygonF()
        self.myColor = QColor(Qt.black)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setPen(QPen(self.myColor, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    def type(self):
        return self.Type

    def setColor(self, color):
        self.myColor = color

    def startItem(self):
        return self.myStartItem

    def endItem(self):
        return self.myEndItem

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0

        return QRectF(
                    self.line().p1(), 
                    QSizeF(self.line().p2().x() - self.line().p1().x(),
                    self.line().p2().y() - self.line().p1().y())
                    ).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super().shape() #QGraphicsLineItem.shape(self)
        path.addPolygon(self.arrowHead)
        
        return path

    def updatePosition(self):
        line = QLineF(
            self.mapFromItem(self.myStartItem, 0, 0), 
            self.mapFromItem(self.myEndItem, 0, 0)            
        )
        self.setLine(line)

    def paint(self, painter, option, widget):
        if self.myStartItem.collidesWithItem(self.myEndItem):
            return
        
        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 20
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        centerLine = QLineF(self.myStartItem.pos(), self.myEndItem.pos())
        endPolygon = self.myEndItem.polygon()
        p1 = endPolygon.first() + self.myEndItem.pos()
        intersectPoint = QPointF()
        for i in range(1, endPolygon.count()):
            p2 = endPolygon.at(i) + self.myEndItem.pos()
            polyLine = QLineF(p1, p2)
            intersectionType = polyLine.intersect(centerLine, intersectPoint)
            if intersectionType == QLineF.BoundedIntersection:
                break
            p1 = p2

        self.setLine(QLineF(intersectPoint, self.myStartItem.pos()))

        angle = math.atan2(-self.line().dy(), self.line().dx())

        arrowP1 = self.line().p1() + + QPointF(math.sin(angle + math.pi/3)*arrowSize, 
                                                math.cos(angle + math.pi/3) * arrowSize)

        arrowP2 = self.line().p1() + QPointF(math.sin(angle + math.pi - math.pi/3)*arrowSize,
                                                math.cos(angle + math.pi - math.pi/3)*arrowSize)
        
        self.arrowHead.clear()
        self.arrowHead << self.line().p1() << arrowP1 << arrowP2

        painter.drawLine(self.line())
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QPen(self.myColor, 1, Qt.DashLine))
            myLine = self.line()
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0,-8.0)
            painter.drawLine(myLine)

class DiagramTextItem(QGraphicsTextItem):
    Type = QGraphicsItem.UserType + 3

    lostFocus = pyqtSignal(QGraphicsTextItem)
    selectedChange = pyqtSignal(QGraphicsItem)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.itemOwner = None

    def type(self):
        return self.Type

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self.selectedChange.emit(self)
        return value

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.lostFocus.emit(self)
        super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
        super().mouseDoubleClickEvent(event)

    def setItemOwner(self, item):
        self.itemOwner = item

    def getOwner(self):
        return self.itemOwner

class DiagramScene(QGraphicsScene):
    class Mode(Enum):
        InsertItem = 0
        InsertLine = 1
        InsertText = 2
        MoveItem = 3
        DragScene = 4

    itemInserted = pyqtSignal(DiagramItem, QPointF)
    textInserted = pyqtSignal(QGraphicsTextItem)
    itemSelected = pyqtSignal(QGraphicsItem)

    def __init__(self, itemMenu, parent=None):
        super().__init__(parent=parent)

        self.myItemMenu = itemMenu
        self.myMode = DiagramScene.Mode.MoveItem
        self.myItemType = DiagramItem.DiagramType.Step
        self.line = None
        self.textItem = None
        self.myItemColor = Qt.white
        self.myTextColor = Qt.black
        self.myLineColor = Qt.black
        self.myFont = QFont()

        self.typeCount = {DiagramItem.DiagramType.Step: 0, DiagramItem.DiagramType.Conditional: 0, DiagramItem.DiagramType.Io: 0}

    def font(self):
        return self.myFont

    def textColor(self):
        return self.myTextColor

    def itemColor(self):
        return self.myItemColor

    def lineColor(self):
        return self.myLineColor

    def isItemChange(self, type):
        items = self.selectedItems()
        for item in items:
            if item.type() == type:
                return True
        return False

    def setLineColor(self, color):
        self.myLineColor = Qt.GlobalColor(color)
        if self.isItemChange(Arrow.Type):
            item = self.selectedItems()[0]
            item.setColor(self.myLineColor)
            self.update()

    def setTextColor(self, color):
        self.myTextColor = Qt.GlobalColor(color)
        if self.isItemChange(DiagramTextItem.Type):
            item = self.selectedItems()[0]
            item.setDefaultTextColor(self.myTextColor)

    def setItemColor(self, color):
        self.myItemColor = Qt.GlobalColor(color)
        if self.isItemChange(DiagramItem.Type):
            item = self.selectedItems()[0]
            item.setBrush(self.myItemColor)

    def setFont(self, font):
        self.myFont = font

        if self.isItemChange(DiagramTextItem.Type):
            item = self.selectedItems()[0]
            #At this point the selection can change so the first selected item might not be a DiagramTextItem
            if item is not None and isinstance(item, DiagramTextItem):
                item.setFont(self.myFont)

    def setMode(self, mode):
        self.myMode = mode

    def setItemType(self, type):
        self.myItemType = type

    def editorLostFocus(self, item):
        cursor = item.textCursor()
        cursor.clearSelection()
        item.setTextCursor(cursor)

        if item.getOwner() is None:
            if len(item.toPlainText()) == 0:
                self.removeItem(item)
        else:
            ownerItem = item.getOwner()
            if len(item.toPlainText()) == 0:
                item.setPlainText(ownerItem.getMyName())
            else:
                ownerItem.setMyName(item.toPlainText())

    def insertItem(self, posF, text=''):
        if self.myMode == DiagramScene.Mode.InsertItem:
            item = DiagramItem(self.myItemType, self.myItemMenu)
            item.setBrush(self.myItemColor)
            self.addItem(item)
            item.setPos(posF)
            textPos = QPointF(posF.x(), posF.y()+item.boundingRect().height()/2+5)

            self.itemInserted.emit(item, textPos)

            self.typeCount[self.myItemType] += 1
        elif self.myMode == DiagramScene.Mode.InsertLine:
            self.line = QGraphicsLineItem(
                            QLineF(posF, posF)
                            )
            self.line.setPen(QPen(self.myLineColor, 2))
            self.addItem(self.line)
        elif self.myMode == DiagramScene.Mode.InsertText:
            self.textItem = DiagramTextItem()
            self.textItem.setFont(self.myFont)
            self.textItem.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.textItem.setZValue(1000.)
            self.textItem.setPlainText(text)
            self.textItem.lostFocus[QGraphicsTextItem].connect(self.editorLostFocus)
            self.textItem.selectedChange[QGraphicsItem].connect(self.itemSelected)
            self.addItem(self.textItem)
            self.textItem.setDefaultTextColor(self.myTextColor)
            self.textItem.setPos(posF)
            self.textInserted.emit(self.textItem)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.setAccepted(True)
            self.update()
        else:
            event.setAccepted(False)

    def dragMoveEvent(self, event):
        event.setAccepted(True)

    def dragLeaveEvent(self, event):
        self.update()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            event.setAccepted(True)
            id = int(event.mimeData().text())

            self.myMode = DiagramScene.Mode.InsertItem
            self.myItemType = DiagramItem.DiagramType(id)

            self.insertItem(event.scenePos())

        self.update()

    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button() != Qt.LeftButton:
            return

        elif self.myMode == DiagramScene.Mode.DragScene:
            return

        # insert line
        self.insertItem(mouseEvent.scenePos())

        itemToBeMoved = self.itemAt(mouseEvent.scenePos(), QTransform())
        if isinstance(itemToBeMoved, DiagramItem):
            itemText = itemToBeMoved.getTextItem()
            self.oldMouseX =  mouseEvent.scenePos().x()
            self.oldMouseY = mouseEvent.scenePos().y()

            self.oldItemTextX = itemText.scenePos().x()
            self.oldItemTextY = itemText.scenePos().y()
        #print(itemMoved.scenePos())

        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.myMode == DiagramScene.Mode.DragScene:
            return
        view = self.views()[-1]
        view.setDragMode(QGraphicsView.NoDrag)
        if self.myMode == DiagramScene.Mode.InsertLine and self.line is not None:
            newLine = QLineF(self.line.line().p1(), mouseEvent.scenePos())
            self.line.setLine(newLine)
        elif self.myMode == self.Mode.MoveItem and self.mouseGrabberItem() is not None:
            # TODO: implement mouse move event where, item seems to hover
            item = self.mouseGrabberItem()
            if item is not None and isinstance(item, DiagramItem):
                textItem = item.getTextItem()
                newX = mouseEvent.scenePos().x()
                newY = mouseEvent.scenePos().y()
                dx = newX-self.oldMouseX
                dy = newY-self.oldMouseY
                textItem.setPos(QPointF(self.oldItemTextX, self.oldItemTextY) + QPointF(dx, dy))
            super().mouseMoveEvent(mouseEvent)
        else:
            view.setDragMode(QGraphicsView.RubberBandDrag)
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if self.line is not None and self.myMode == self.Mode.InsertLine:
            startItems = self.items(self.line.line().p1())
            if len(startItems) > 0 and startItems[0] == self.line:
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if len(endItems) > 0 and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)

            if len(startItems) > 0 and len(endItems) > 0 and \
                startItems[0].type() == DiagramItem.Type and \
                endItems[0].type() == DiagramItem.Type and \
                startItems[0] != endItems[0]:
                startItem = startItems[0]
                endItem = endItems[0]
                arrow = Arrow(startItem, endItem)
                arrow.setColor(self.myLineColor)
                startItem.addArrow(arrow)
                endItem.addArrow(arrow)
                arrow.setZValue(-1000.)
                self.addItem(arrow)
                arrow.updatePosition()

        self.line = None
        super().mouseReleaseEvent(mouseEvent)  

    def mouseDoubleClickEvent(self, mouseEvent):
        if self.myMode == DiagramScene.Mode.DragScene:
            return

        if len(self.selectedItems()) > 0:
            super().mouseDoubleClickEvent(mouseEvent)
            return

        self.myMode = DiagramScene.Mode.InsertText

        self.insertItem(mouseEvent.scenePos())

        super().mouseDoubleClickEvent(mouseEvent)


class CellListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def mouseMoveEvent(self, event):
        item = self.currentItem()
        id = item.data(Qt.UserRole)
        
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(str(id))
        drag.setMimeData(mimeData)
        
        icon = item.icon()
        iconPixmap = icon.pixmap(icon.actualSize(QSize(48, 48)))
        drag.setPixmap(iconPixmap)

        drag.exec_()

class DiagramView(QGraphicsView):
    zoomScale = 100

    zoomSignal = pyqtSignal(int)

    def __init__(self, scene, parent=None):
        super().__init__(parent=parent)

        self.setScene(scene)

        self.setAcceptDrops(True)

    def setupMatrix(self, value):
        if value > 0:
            self.zoomScale += 25
        else:
            self.zoomScale -= 25
        
        if self.zoomScale > 150:
            self.zoomScale = 150
        elif self.zoomScale < 50:
            self.zoomScale = 50

        newScale = self.zoomScale/100.
        
        oldMatrix = self.transform()
        self.resetTransform()
        self.translate(oldMatrix.dx(), oldMatrix.dy())
        self.scale(newScale, newScale)

        self.zoomSignal.emit(self.zoomScale)

    def wheelEvent(self, event):
        self.setupMatrix(event.angleDelta().y())
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.createActions()
        self.createMenus()
        self.createToolBox()

        self.scene = DiagramScene(self.itemMenu, self)
        self.scene.setSceneRect(QRectF(0, 0, 5000, 5000))
        self.scene.itemInserted[DiagramItem, QPointF].connect(self.itemInserted)
        self.scene.textInserted[QGraphicsTextItem].connect(self.textInserted)
        self.scene.itemSelected[QGraphicsItem].connect(self.itemSelected)
        self.createToolbars()

        layout = QHBoxLayout()
        layout.addWidget(self.toolBox)
        self.view = DiagramView(self.scene) #QGraphicsView(self.scene)
        self.view.zoomSignal[int].connect(self.sceneScaleAutoChanged)
        layout.addWidget(self.view)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle('Diagramscene in Python (with additional stuffs)')
        self.setUnifiedTitleAndToolBarOnMac(True)

    @pyqtSlot(DiagramItem, QPointF)
    def itemInserted(self, item, textpos):
        self.scene.setMode(DiagramScene.Mode.InsertText)
        itemLabel = str(item.diagramType())[12:] + '_' + str(self.scene.typeCount[item.diagramType()]+1)
        item.setMyName(itemLabel)
        self.scene.insertItem(textpos, itemLabel)
        textItem = self.scene.items()[0]
        textItem.setItemOwner(item)
        item.setTextItemOwnership(textItem)

        self.pointerTypeGroup.button(DiagramScene.Mode.MoveItem.value).setChecked(True)
        self.scene.setMode(DiagramScene.Mode(self.pointerTypeGroup.checkedId()))
        listWidget = self.toolBox.currentWidget()
        listWidget.clearSelection()
        self.setDragOrNoDrag()
        # self.buttonGroup.button(item.diagramType().value).setChecked(False)

    @pyqtSlot(QGraphicsTextItem)
    def textInserted(self, item):
        # self.buttonGroup.button(InsertTextButton).setChecked(False)
        self.scene.setMode(DiagramScene.Mode(self.pointerTypeGroup.checkedId()))

    @pyqtSlot(QGraphicsItem)
    def itemSelected(self, textItem):
        font = textItem.font()
        self.fontCombo.setCurrentFont(font)
        self.fontSizeCombo.setEditText(str(font.pointSize()))
        self.boldAction.setChecked(font.weight() == QFont.Bold)
        self.italicAction.setChecked(font.italic())
        self.underlineAction.setChecked(font.underline())
    
    @pyqtSlot()
    def bringToFront(self):
        if len(self.scene.selectedItems()) == 0:
            return
        
        selectedItem = self.scene.selectedItems()[0]
        overlapItems = selectedItem.collidingItems()

        zValue = 0
        for item in overlapItems:
            if item.zValue() >= zValue and item.type() == DiagramItem.Type:
                zValue = item.zValue() + 0.1
        selectedItem.setZValue(zValue)

    @pyqtSlot()
    def sendToBack(self):
        if len(self.scene.selectedItems()) == 0:
            return

        selectedItem = self.scene.selectedItems()[0]
        overlapItems = selectedItem.collidingItems()
        
        zValue = 0.
        for item in overlapItems:
            if item.zValue() <= zValue and item.type() == DiagramItem.Type:
                zValue = item.zValue() - 0.1
        selectedItem.setZValue(zValue)

    @pyqtSlot()
    def deleteItem(self):
        selectedItems = self.scene.selectedItems()
        for item in selectedItems:
            if item.type() == Arrow.Type:
                self.scene.removeItem(item)
                arrow = item
                arrow.startItem().removeArrow(arrow)
                arrow.endItem().removeArrow(arrow)

        selectedItems = self.scene.selectedItems()
        for item in selectedItems:
            if item.type() == DiagramItem.Type:
                item.removeArrows()
                textItem = item.getTextItem()
                self.scene.removeItem(textItem)
                self.scene.removeItem(item)

        selectedItems = self.scene.selectedItems()
        for item in selectedItems:
            self.scene.removeItem(item)

    @pyqtSlot(QAbstractButton)
    def pointerGroupClicked(self, button):
        self.scene.setMode(DiagramScene.Mode(self.pointerTypeGroup.checkedId()))
        self.setDragOrNoDrag()

    def setDragOrNoDrag(self):
        if self.scene.myMode == DiagramScene.Mode.DragScene:
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        else:
            self.view.setDragMode(QGraphicsView.NoDrag)

    @pyqtSlot()
    def handleFontChange(self):
        font = self.fontCombo.currentFont()
        font.setPointSize(int(self.fontSizeCombo.currentText()))
        font.setWeight(QFont.Bold if self.boldAction.isChecked() else QFont.Normal)
        font.setItalic(self.italicAction.isChecked())
        font.setUnderline(self.underlineAction.isChecked())

        self.scene.setFont(font)

    @pyqtSlot(QFont)
    def currentFontChanged(self, font):
        self.handleFontChange()

    @pyqtSlot(str)
    def fontSizeChanged(self, textSize):
        self.handleFontChange()

    @pyqtSlot()
    def textButtonTriggered(self):
        self.scene.setTextColor(self.textAction.data())

    @pyqtSlot()
    def fillButtonTriggered(self):
        self.scene.setItemColor(self.fillAction.data())

    @pyqtSlot()
    def lineButtonTriggered(self):
        self.scene.setLineColor(self.lineAction.data())

    @pyqtSlot()
    def textColorChanged(self):
        self.textAction = self.sender()
        filename = os.path.join(DIR_NAME, 'images\\textpointer.png')
        self.fontColorToolButton.setIcon(self.createColorToolButtonIcon(filename, self.textAction.data()))

        self.textButtonTriggered()

    @pyqtSlot()
    def itemColorChanged(self):
        self.fillAction = self.sender()
        filename = os.path.join(DIR_NAME, 'images\\floodfill.png')
        self.fillColorToolButton.setIcon(self.createColorToolButtonIcon(filename, self.fillAction.data()))
        
        self.fillButtonTriggered()

    @pyqtSlot()
    def lineColorChanged(self):
        self.lineAction = self.sender()
        filename = os.path.join(DIR_NAME, 'images\\linecolor.png')
        self.lineColorToolButton.setIcon(self.createColorToolButtonIcon(filename, self.lineAction.data()))

        self.lineButtonTriggered()

    @pyqtSlot(str)
    def sceneScaleChanged(self, scale):
        newScale = float(scale.strip('%'))/100.
        oldMatrix = self.view.transform()
        self.view.resetTransform()
        self.view.translate(oldMatrix.dx(), oldMatrix.dy())
        self.view.scale(newScale, newScale)

    @pyqtSlot(int)
    def sceneScaleAutoChanged(self, scale):
        scaleStr = str(scale)+'%'
        self.sceneScaleCombo.currentTextChanged[str].disconnect()
        self.sceneScaleCombo.setCurrentText(scaleStr)
        self.sceneScaleCombo.currentTextChanged[str].connect(self.sceneScaleChanged)

    @pyqtSlot()
    def about(self):
        QMessageBox.about(self, 'About Diagram Scene', 
                        "The <b>Diagram Scene</b> example shows "
                        "use of the graphics framework.")

    @pyqtSlot(QAbstractButton)
    def buttonGroupClicked(self, button):
        buttons = self.buttonGroup.buttons()
        for myButton in buttons:
            if myButton != button:
                button.setChecked(False)
        id = self.buttonGroup.id(button)
        if id == InsertTextButton:
            self.scene.setMode(DiagramScene.Mode.InsertText)
        else:
            self.scene.setItemType(DiagramItem.DiagramType(id))
            self.scene.setMode(DiagramScene.Mode.InsertItem)

    @pyqtSlot(QAbstractButton)
    def backgroundButtonGroupClicked(self, button):
        buttons = self.backgroundButtonGroup.buttons()
        for myButton in buttons:
            if myButton != button:
                button.setChecked(False)
        text = button.text()
        if text == 'Blue Grid':
            filename = os.path.join(DIR_NAME, 'images\\background1.png') 
            self.scene.setBackgroundBrush(QBrush(QPixmap(filename)))
        elif text == 'White Grid':
            filename = os.path.join(DIR_NAME, 'images\\background2.png')
            self.scene.setBackgroundBrush(QBrush(QPixmap(filename)))
        elif text == 'Gray Grid':
            filename = os.path.join(DIR_NAME, 'images\\background3.png')
            self.scene.setBackgroundBrush(QBrush(QPixmap(filename)))
        else:
            filename = os.path.join(DIR_NAME, 'images\\background4.png')
            self.scene.setBackgroundBrush(QBrush(QPixmap(filename)))

        self.scene.update()
        self.view.update()

    def createCellWidget(self, text, type):
        item = DiagramItem(type, self.itemMenu)
        icon = QIcon(item.image())

        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.buttonGroup.addButton(button, type.value)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellListWidgetItem(self, text, type):
        item = DiagramItem(type, self.itemMenu)
        icon = QIcon(item.image())

        listWidgetItem = QListWidgetItem(text)
        listWidgetItem.setIcon(icon)

        listWidgetItem.setData(Qt.UserRole, type.value)

        return listWidgetItem

    def createBackgroundCellWidget(self, text, image):
        button = QToolButton()
        button.setText(text)
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.backgroundButtonGroup.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createActions(self):
        filename = os.path.join(DIR_NAME, 'images\\bringtofront.png')
        self.toFrontAction = QAction(QIcon(filename), 
                            'Bring to &Front', self)
        self.toFrontAction.setShortcut('Ctrl+F')
        self.toFrontAction.setStatusTip('Bring item to front')
        self.toFrontAction.triggered.connect(self.bringToFront)

        filename = os.path.join(DIR_NAME, 'images\\sendtoback.png')
        self.sendBackAction = QAction(QIcon(filename), 
                            'Send to &Back', self)
        self.sendBackAction.setShortcut('Ctrl+T')
        self.sendBackAction.setStatusTip('Send item to back')
        self.sendBackAction.triggered.connect(self.sendToBack)

        filename = os.path.join(DIR_NAME, 'images\\delete.png')
        self.deleteAction = QAction(QIcon(filename), 
                            '&Delete', self)
        self.deleteAction.setShortcut('Delete')
        self.deleteAction.setStatusTip('Delete item from diagram')
        self.deleteAction.triggered.connect(self.deleteItem)

        self.exitAction = QAction('E&xit', self)
        self.exitAction.setShortcut(QKeySequence.Quit)
        self.exitAction.setStatusTip('Quit Scenediagram example')
        self.exitAction.triggered.connect(self.close)

        self.boldAction = QAction('Bold', self)
        self.boldAction.setCheckable(True)
        filename = os.path.join(DIR_NAME, 'images\\bold.png')
        pixmap = QPixmap(filename)
        self.boldAction.setIcon(QIcon(pixmap))
        self.boldAction.setShortcut('Ctrl+B')
        self.boldAction.triggered.connect(self.handleFontChange)

        filename = os.path.join(DIR_NAME, 'images\\italic.png')
        self.italicAction = QAction(QIcon(filename), 'Italic', self)
        self.italicAction.setCheckable(True)
        self.italicAction.setShortcut('Ctrl+I')
        self.italicAction.triggered.connect(self.handleFontChange)

        filename = os.path.join(DIR_NAME, 'images\\underline.png')
        self.underlineAction = QAction(QIcon(filename), 'Underline', self)
        self.underlineAction.setCheckable(True)
        self.underlineAction.setShortcut('Ctrl+U')
        self.underlineAction.triggered.connect(self.handleFontChange)

        self.aboutAction = QAction('A&bout', self)
        self.aboutAction.setShortcut('F1')
        self.aboutAction.triggered.connect(self.about)

    def createToolBox(self):
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked[QAbstractButton].connect(self.buttonGroupClicked)
        layout = QGridLayout()
        layout.addWidget(self.createCellWidget('Conditional', DiagramItem.DiagramType.Conditional), 0, 0)
        layout.addWidget(self.createCellWidget('Process', DiagramItem.DiagramType.Step), 0, 1)
        layout.addWidget(self.createCellWidget('Input/Output', DiagramItem.DiagramType.Io), 1, 0)

        textButton = QToolButton()
        textButton.setCheckable(True)
        self.buttonGroup.addButton(textButton, InsertTextButton)
        filename = os.path.join(DIR_NAME, 'images\\textpointer.png')
        textButton.setIcon(QIcon(QPixmap(filename)))
        textButton.setIconSize(QSize(50, 50))
        textLayout = QGridLayout()
        textLayout.addWidget(textButton, 0, 0, Qt.AlignHCenter)
        textLayout.addWidget(QLabel('Text'), 1, 0, Qt.AlignCenter)
        textWidget = QWidget()
        textWidget.setLayout(textLayout)
        layout.addWidget(textWidget, 1, 1)

        layout.setRowStretch(3, 10)
        layout.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.setLayout(layout)

        listWidget = CellListWidget()
        listWidget.setViewMode(QListWidget.IconMode)
        listWidget.setAcceptDrops(False)
        #listWidget.clearSelection()
        listWidget.setSpacing(10)
        listWidget.addItem(self.createCellListWidgetItem('Conditional', DiagramItem.DiagramType.Conditional))
        listWidget.addItem(self.createCellListWidgetItem('Process', DiagramItem.DiagramType.Step))
        listWidget.addItem(self.createCellListWidgetItem('Input/Output', DiagramItem.DiagramType.Io))
        #listWidget.addItem(self.createCellListWidgetItem('Start/End', DiagramItem.DiagramType.StartEnd))
        
        # listItem = QListWidgetItem('Text')
        # filename = os.path.join(DIR_NAME, 'images\\textpointer.png')
        # listItem.setIcon(QIcon(QPixmap(filename)))
        # listItem.setData(Qt.UserRole, InsertTextButton)
        # listWidget.addItem(listItem)

        self.backgroundButtonGroup = QButtonGroup(self)
        self.backgroundButtonGroup.buttonClicked[QAbstractButton].connect(self.backgroundButtonGroupClicked)

        backgroundLayout = QGridLayout()
        filename = os.path.join(DIR_NAME, 'images\\background1.png')
        backgroundLayout.addWidget(self.createBackgroundCellWidget('Blue Grid', filename), 0, 0)
        filename = os.path.join(DIR_NAME, 'images\\background2.png')
        backgroundLayout.addWidget(self.createBackgroundCellWidget('White Grid', filename), 0, 1)
        filename = os.path.join(DIR_NAME, 'images\\background3.png')
        backgroundLayout.addWidget(self.createBackgroundCellWidget('Gray Grid', filename), 1, 0)
        filename = os.path.join(DIR_NAME, 'images\\background4.png')
        backgroundLayout.addWidget(self.createBackgroundCellWidget('No Grid', filename), 1, 1)

        backgroundLayout.setRowStretch(2, 10)
        backgroundLayout.setColumnStretch(2, 10)

        backGroundWidget = QWidget()
        backGroundWidget.setLayout(backgroundLayout)

        self.toolBox = QToolBox()
        self.toolBox.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored))
        self.toolBox.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox.addItem(listWidget, 'Basic Flowchart Shapes')
        #self.toolBox.addItem(itemWidget, 'Basic Flowchart Shapes')
        self.toolBox.addItem(backGroundWidget, 'Backgrounds')

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.exitAction)

        self.itemMenu = self.menuBar().addMenu('&Item')
        self.itemMenu.addAction(self.deleteAction)
        self.itemMenu.addSeparator()
        self.itemMenu.addAction(self.toFrontAction)
        self.itemMenu.addAction(self.sendBackAction)

        self.aboutMenu = self.menuBar().addMenu('&Help')
        self.aboutMenu.addAction(self.aboutAction)

    def createColorIcon(self, color):
        pixmap = QPixmap(20, 20)
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)
        painter.fillRect(QRect(0, 0, 20, 20), color)
        painter.end()

        return QIcon(pixmap)

    def createColorMenu(self, slot, defaultColor):
        # colors = [Qt.black, Qt.white, Qt.red, Qt.blue, Qt.yellow]
        # names = ['black', 'white', 'red', 'blue', 'yellow']

        colorMenu = QMenu(self)
        for key in COLORKEY:
            action = QAction(key, self)
            action.setData(COLORKEY[key])
            action.setIcon(self.createColorIcon(COLORKEY[key]))
            action.triggered.connect(slot)
            colorMenu.addAction(action)
            if COLORKEY[key] == defaultColor:
                colorMenu.setDefaultAction(action)
        
        return colorMenu

    def createColorToolButtonIcon(self, imageFile, color):
        pixmap = QPixmap(50, 80)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        image = QPixmap(imageFile)
        # Draw icon centred horizontally on button.
        target = QRect(4, 0, 42, 43)
        source = QRect(0, 0, 42, 43)
        painter.fillRect(QRect(0, 60, 50, 80), color)
        painter.drawPixmap(target, image, source)
        painter.end()

        return QIcon(pixmap)

    def createToolbars(self):
        self.editToolBar = self.addToolBar('Edit')
        self.editToolBar.addAction(self.deleteAction)
        self.editToolBar.addAction(self.toFrontAction)
        self.editToolBar.addAction(self.sendBackAction)

        self.fontCombo = QFontComboBox()
        self.fontCombo.currentFontChanged[QFont].connect(self.currentFontChanged)

        self.fontSizeCombo = QComboBox()
        self.fontSizeCombo.setEditable(True)
        for i in range(8,30,2):
            self.fontSizeCombo.addItem(str(i))
        validator = QIntValidator(2, 64, self)
        self.fontSizeCombo.setValidator(validator)
        self.fontSizeCombo.currentTextChanged[str].connect(self.fontSizeChanged)

        self.fontColorToolButton = QToolButton()
        self.fontColorToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.fontColorToolButton.setMenu(self.createColorMenu(self.textColorChanged, Qt.black))
        self.textAction = self.fontColorToolButton.menu().defaultAction()
        filename = os.path.join(DIR_NAME, 'images\\textpointer.png')
        self.fontColorToolButton.setIcon(self.createColorToolButtonIcon(filename, Qt.black))
        self.fontColorToolButton.setAutoFillBackground(True)
        self.fontColorToolButton.clicked.connect(self.textButtonTriggered)

        self.fillColorToolButton = QToolButton()
        self.fillColorToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.fillColorToolButton.setMenu(self.createColorMenu(self.itemColorChanged, Qt.white))
        self.fillAction = self.fillColorToolButton.menu().defaultAction()
        filename = os.path.join(DIR_NAME, 'images\\floodfill.png')
        self.fillColorToolButton.setIcon(self.createColorToolButtonIcon(filename, Qt.white))
        self.fillColorToolButton.clicked.connect(self.fillButtonTriggered)

        self.lineColorToolButton = QToolButton()
        self.lineColorToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.lineColorToolButton.setMenu(self.createColorMenu(self.lineColorChanged, Qt.black))
        self.lineAction = self.lineColorToolButton.menu().defaultAction()
        filename = os.path.join(DIR_NAME, 'images\\linecolor.png')
        self.lineColorToolButton.setIcon(self.createColorToolButtonIcon(filename, Qt.black))
        self.lineColorToolButton.clicked.connect(self.lineButtonTriggered)

        self.textToolBar = self.addToolBar('Font')
        self.textToolBar.addWidget(self.fontCombo)
        self.textToolBar.addWidget(self.fontSizeCombo)
        self.textToolBar.addAction(self.boldAction)
        self.textToolBar.addAction(self.italicAction)
        self.textToolBar.addAction(self.underlineAction)

        self.colorToolBar = self.addToolBar('Color')
        self.colorToolBar.addWidget(self.fontColorToolButton)
        self.colorToolBar.addWidget(self.fillColorToolButton)
        self.colorToolBar.addWidget(self.lineColorToolButton)

        pointerButton = QToolButton()
        pointerButton.setCheckable(True)
        pointerButton.setChecked(True)
        filename = os.path.join(DIR_NAME, 'images\\pointer.png')
        pointerButton.setIcon(QIcon(filename))
        linePointerButton = QToolButton()
        linePointerButton.setCheckable(True)
        filename = os.path.join(DIR_NAME, 'images\\linepointer.png')
        linePointerButton.setIcon(QIcon(filename))
        handGrabButton = QToolButton()
        handGrabButton.setCheckable(True)
        filename = os.path.join(DIR_NAME, 'images\\hand.png')
        handGrabButton.setIcon(QIcon(filename))

        self.pointerTypeGroup = QButtonGroup(self)
        self.pointerTypeGroup.addButton(pointerButton, DiagramScene.Mode.MoveItem.value)
        self.pointerTypeGroup.addButton(linePointerButton, DiagramScene.Mode.InsertLine.value)
        self.pointerTypeGroup.addButton(handGrabButton, DiagramScene.Mode.DragScene.value)
        self.pointerTypeGroup.buttonClicked[QAbstractButton].connect(self.pointerGroupClicked)

        self.sceneScaleCombo = QComboBox()
        scales = ["50%", "75%", "100%", "125%", "150%"]
        self.sceneScaleCombo.addItems(scales)
        self.sceneScaleCombo.setCurrentIndex(2)
        self.sceneScaleCombo.currentTextChanged[str].connect(self.sceneScaleChanged)

        self.pointerToolbar = self.addToolBar('Pointer type')
        self.pointerToolbar.addWidget(pointerButton)
        self.pointerToolbar.addWidget(linePointerButton)
        self.pointerToolbar.addWidget(handGrabButton)
        self.pointerToolbar.addWidget(self.sceneScaleCombo)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()