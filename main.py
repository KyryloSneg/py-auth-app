from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QFontDatabase
from ui.MainWidget import MainWidget

import os, sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    QFontDatabase.addApplicationFont(os.path.abspath("Montserrat-Regular.ttf"))
    QFontDatabase.addApplicationFont(os.path.abspath("Montserrat-Bold.ttf"))
    
    # not an elegant way to deal with custom fonts but i haven't found a way to add one in qt designer
    main_font = QFont("Montserrat-Regular", 10)  
    
    app.setFont(main_font)
    
    widget = MainWidget()
    widget.show()

    app.exec_()
