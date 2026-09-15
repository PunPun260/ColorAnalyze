from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import colorsys # rgb and hsl

class ColorAnalyzeDocker(DockWidget):

    def __init__(self):
        super().__init__()

        # The main Docker page
        self.setWindowTitle("Color Harmonica OwO")
        mainWidget = QWidget(self)
        self.setWidget(mainWidget)
        mainWidget.setLayout(QVBoxLayout())
        # mainWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # button for testfication
        testButton = QPushButton("Show Popup")
        testButton.clicked.connect(self.popup)

        # Group box for ---colorpicker---
        colorPicker = QGroupBox("Color Selector")
        colorPicker.setLayout(QHBoxLayout())
        colorPicker.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # colorPicker.layout().addWidget(testButton)

        # --- Eyedroper ---
        colorDropper = QPushButton(Krita.instance().icon('krita_tool_color_sampler'), "")
        colorDropper.clicked.connect(self.colorDrop)
        colorPicker.layout().addWidget(colorDropper)

        # --- RGB & HSV ---
        # self.colorCode = QComboBox()
        # self.colorCode.addItem("RGB")
        # self.colorCode.addItem("HSL")
        # colorPicker.layout().addWidget(self.colorCode)

        # --- Color code (Hex) inputer ---
        # currentColor = Krita.instance().activeWindow().activeView().foregroundColor()
        self.mainColor = QLineEdit()
        self.mainColor.setMaxLength(7)
        self.mainColor.textEdited.connect(self.colorinput)
        self.mainColor.setPlaceholderText("Hex : #FFFFFF")
        colorPicker.layout().addWidget(QLabel("Hex Code : "))
        colorPicker.layout().addWidget(self.mainColor)
        
        # apply colorpicker
        mainWidget.layout().addWidget(colorPicker)
        
        # Group box for ---Color Harmonies---
        colorHarmony = QGroupBox("Color Harmonies :3")
        colorHarmony.setLayout(QVBoxLayout())
        colorHarmony.layout().setAlignment(Qt.AlignTop)
        # colorHarmony.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # Selector
        self.harmony = QComboBox()
        self.harmony.addItems(["Complementary", "Split-Complementary", "Analogous", "Triadic", "Square"])
        self.harmony.currentIndexChanged.connect(self.harmonychange)
        colorHarmony.layout().addWidget(self.harmony)

        # Visualizer 
        self.visualizeHar = QWidget()
        self.visualizeHar.setLayout(QHBoxLayout())
        
        # Draw Vis
        self.visializeDraw = ColorHarmonyDraw()
        self.visualizeHar.layout().addWidget(self.visializeDraw)
        
        # Output Result
        self.output = QWidget()
        self.output.setLayout(QVBoxLayout())
        # self.output.resize(mainWidget.width()/2, 80)

        self.visualizeHar.layout().addWidget(self.output)

        colorHarmony.layout().addWidget(self.visualizeHar)
        
        mainWidget.layout().addWidget(colorHarmony)

        self.lastColor = None
        self.checker = QTimer()
        self.checker.timeout.connect(self.checkColor)
        self.checker.start(100)

    def checkColor(self):
        if not Krita.instance().activeWindow():
            return
        if not Krita.instance().activeWindow().activeView():
            return
        if not Krita.instance().activeWindow().activeView().foregroundColor():
            return
        
        color = Krita.instance().activeWindow().activeView().foregroundColor().componentsOrdered()
        if color != self.lastColor:
            self.lastColor = color
            hex = self.num2hex(color[0]*255, color[1]*255, color[2]*255)
            self.mainColor.setText(hex)
            self.lastColorHLS = self.hex2hsl(hex)

            # ===== Calculate Harmony =====
            self.cn512 = self.hsl2hex(((self.lastColorHLS[0] - 5/12)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            self.cn13 = self.hsl2hex(((self.lastColorHLS[0] - 1/3)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            self.cn14 = self.hsl2hex(((self.lastColorHLS[0] - 1/4)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            self.cn112 = self.hsl2hex(((self.lastColorHLS[0] - 1/12)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            self.c112 = self.hsl2hex(((self.lastColorHLS[0] + 1/12)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            self.c14 = self.hsl2hex(((self.lastColorHLS[0] + 1/4)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            self.c13 = self.hsl2hex(((self.lastColorHLS[0] + 1/3)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            self.c512 = self.hsl2hex(((self.lastColorHLS[0] + 5/12)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            self.c12 = self.hsl2hex(((self.lastColorHLS[0] + 1/2)%1.0, self.lastColorHLS[1], self.lastColorHLS[2]))
            
            self.visializeDraw.setColor(
                self.mainColor.text(),
                [self.cn512, self.cn13, self.cn14, self.cn112, self.c112, self.c14, self.c13, self.c512, self.c12]
            )
            self.visializeDraw.update()

            self.outputupdate()


    def colorinput(self):
        code = self.mainColor.text()
        try:
            color = self.hex2num(code)
            applycolor = ManagedColor("RGBA", "U8", "")
            applycolor.setComponents(color)
            Krita.instance().activeWindow().activeView().setForeGroundColor(applycolor)
        except:
            pass

    def outputupdate(self):
        while self.output.layout().count(): 
            item = self.output.layout().takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        mode = self.harmony.currentIndex()

        if (mode == 0): # +---- COM
            harhex = [self.c12]
        if (mode == 1): # +---- SPLTCOM
            harhex = [self.c512, self.cn512]
        if (mode == 2): # +---- ANA
            harhex = [self.c112, 0, self.cn112]
        if (mode == 3): # +---- TRI
            harhex = [self.c13, 0, self.cn13]
        if (mode == 4): # +---- QUA
            harhex = [self.c14, self.c12, self.cn14]

        for hx in harhex:
            if hx:
                tex = QLineEdit()
                tex.setText(hx)
                tex.setReadOnly(True)
                self.output.layout().addWidget(tex)
            else:
                self.output.layout().addSpacerItem(QSpacerItem(40, 40))
            

       
    def colorDrop(self):
        Krita.instance().action('KritaSelected/KisToolColorSampler').trigger()

    def harmonychange(self):
        self.visializeDraw.mode = self.harmony.currentIndex()
        self.visializeDraw.update()
        self.outputupdate()

    def popup(self):
        QMessageBox.information(QWidget(), "Docker Example", "This example button works")

    # ===== COLOR CONVERSION =====

    def num2hex(self, r, g, b):
        return f"#{round(r):02X}{round(g):02X}{round(b):02X}"

    def hex2num(self, hexx):
        hexx = hexx.strip().lstrip("#")
        if len(hexx) == 6:
            try:
                colorr = Krita.instance().activeWindow().activeView().foregroundColor().components()
                colorr[2] = int(hexx[0:2], 16) / 255
                colorr[1] = int(hexx[2:4], 16) / 255
                colorr[0] = int(hexx[4:6], 16) / 255
                return colorr
            except ValueError:
                return
    
    def hex2hsl(self, hexx):
        color = self.hex2num(hexx) # got [BGR]
        return colorsys.rgb_to_hls(color[2], color[1], color[0]) #Swap

    def hsl2hex(self, hsl):
        r, g, b = colorsys.hls_to_rgb(hsl[0], hsl[1], hsl[2]) #0.0-1.0
        return self.num2hex(r * 255, g * 255, b * 255) #0.0-1.0 -> 0-255

    # ============================

    def canvasChanged(self, canvas):
        pass    

class ColorHarmonyDraw(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(120)
        # self.setMinimumHeight(120)
        self.mode = 0
        self.mainColor = "#FFFFFF"
        self.harmonyColor = ["#FFFFFF"] * 9 #protect

        pallete = self.palette()
        self.lineCol = pallete.color(self.foregroundRole())

        '''
        0 : COM
        1 : SPLTCOM
        2 : ANA
        3 : TRI
        4 : QUA
        '''

    def setColor(self, mainCol, harCols):
        self.mainColor = mainCol #Hex 
        self.harmonyColor = harCols #Hexes

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # setting the width unit
        w = self.width()

        painter.setPen(QPen(QColor(self.lineCol), 3))

        # 1 : COM
        if (self.mode == 0):
            # self.setMinimumHeight(round(w/32)*5)
            painter.drawLine(22, 22, 92, 22)
            painter.setBrush(QBrush(QColor(self.mainColor)))
            painter.drawEllipse(10, 10, 25, 25)
            painter.setBrush(QBrush(QColor(self.harmonyColor[8])))
            painter.drawEllipse(80, 10, 25, 25)
        elif (self.mode == 1):
            painter.drawLine(92, 62, 92, 22)
            painter.drawLine(22, 42, 92, 62)
            painter.drawLine(22, 42, 92, 22)
            painter.setBrush(QBrush(QColor(self.mainColor)))
            painter.drawEllipse(10, 30, 25, 25)
            painter.setBrush(QBrush(QColor(self.harmonyColor[7])))
            painter.drawEllipse(80, 10, 25, 25)
            painter.setBrush(QBrush(QColor(self.harmonyColor[0])))
            painter.drawEllipse(80, 50, 25, 25)
        elif (self.mode == 2):
            arc = QRectF(42 , 22-16.6 , 113.1, 113.1)
            painter.drawArc(arc, 135*16, 90*16)
            painter.setBrush(QBrush(QColor(self.harmonyColor[4])))
            painter.drawEllipse(47, 10, 25, 25)
            painter.setBrush(QBrush(QColor(self.mainColor)))
            painter.drawEllipse(30, 50, 25, 25)
            painter.setBrush(QBrush(QColor(self.harmonyColor[3])))
            painter.drawEllipse(47, 90, 25, 25)
        elif (self.mode == 3):
            painter.drawLine(92, 102, 92, 22)
            painter.drawLine(22, 62, 92, 102)
            painter.drawLine(22, 62, 92, 22)
            painter.setBrush(QBrush(QColor(self.harmonyColor[6])))
            painter.drawEllipse(80, 10, 25, 25)
            painter.setBrush(QBrush(QColor(self.mainColor)))
            painter.drawEllipse(10, 50, 25, 25)
            painter.setBrush(QBrush(QColor(self.harmonyColor[1])))
            painter.drawEllipse(80, 90, 25, 25)
        elif (self.mode == 4):
            painter.drawLine(102, 62, 62, 22)
            painter.drawLine(102, 62, 62, 102)
            painter.drawLine(22, 62, 62, 102)
            painter.drawLine(22, 62, 62, 22)
            painter.setBrush(QBrush(QColor(self.harmonyColor[5])))
            painter.drawEllipse(50, 10, 25, 25)
            painter.setBrush(QBrush(QColor(self.mainColor)))
            painter.drawEllipse(10, 50, 25, 25)
            painter.setBrush(QBrush(QColor(self.harmonyColor[8])))
            painter.drawEllipse(90, 50, 25, 25)
            painter.setBrush(QBrush(QColor(self.harmonyColor[2])))
            painter.drawEllipse(50, 90, 25, 25)
            
            
            


        painter.end()


        
Krita.instance().addDockWidgetFactory(DockWidgetFactory("colorAnalyze", DockWidgetFactoryBase.DockRight, ColorAnalyzeDocker))

