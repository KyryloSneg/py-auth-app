from PyQt5.QtWidgets import QApplication
from ui.MainWidget import MainWidget

from dotenv import load_dotenv


load_dotenv()


if __name__ == "__main__":
    app = QApplication([])
    widget = MainWidget()
    widget.show()

    app.exec_()
