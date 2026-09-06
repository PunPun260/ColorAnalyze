from krita import *

def trigger_my_plugin():
    Krita.instance().action("python_scripter").trigger()

#n = Krita.instance().activeDocument().activeNode()
#f = Krita.instance().filter("autocontrast")

#f.apply(n, 500, 500, 1000, 5000)

#Krita.instance().activeDocument().refreshProjection()

#doc = Krita.instance().createDocument(100, 100, "Doc1", "RGBA", "U8", "", 120.0)
#Krita.instance().activeWindow().addView(doc)

