
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import sys
import random
import cv2

import db
import wsl

# References
# https://doc.qt.io/qtforpython/


def main():
    # If the database has not been created, then create it
    db.create_tables()

    # Set DISPLAY env variable accordingly if running under WSL
    wsl.set_display_to_host()

    sys_argv = sys.argv
    sys_argv += ['--style', 'Fusion']
    app = QApplication(sys_argv)  # Create application

    window = MainWindow()  # Create main window
    window.show()  # Show main window

    app.exec_()  # Start application

    exit(0)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("StudiOCR")
        self.resize(900, 900)

        self.main_widget = MainUI()

        # Set the central widget of the Window.
        self.setCentralWidget(self.main_widget)


class MainUI(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.welcome_label = QLabel('Welcome to StudiOCR')
        self.welcome_label.setAlignment(Qt.AlignCenter)

        self.documents = ListDocuments()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.welcome_label, alignment=Qt.AlignTop)
        self.layout.addWidget(self.documents, alignment=Qt.AlignTop)
        self.setLayout(self.layout)


class ListDocuments(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        self._layout = QVBoxLayout()

        grid = QGridLayout()

        self._docButtons = []

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for document name...")
        self.search_bar.textChanged.connect(self.update_filter)

        self._layout.addWidget(self.search_bar)

        # If there are no documents, then the for loop won't create the index variable
        idx = 0
        for idx, doc in enumerate(OcrDocument.select()):
            img = None
            name = doc.name
            if len(doc.pages) > 0:
                img = doc.pages[0].image

            doc_button = SingleDocumentButton(name, img)
            doc_button.pressed.connect(
                lambda doc=doc: self.create_doc_window(doc))
            grid.addWidget(doc_button, idx / 4, idx % 4, 1, 1)
            self._docButtons.append(doc_button)

        new_doc_button = SingleDocumentButton('Add New Document', None)
        new_doc_button.pressed.connect(
            lambda: self.create_new_doc_window())
        grid.addWidget(new_doc_button, (idx+1) / 4, (idx+1) % 4, 1, 1)

        self._layout.addLayout(grid)

        self.setLayout(self._layout)

    def create_doc_window(self, doc):
        self.doc_window = DocWindow(doc)
        self.doc_window.show()

    def create_new_doc_window(self):
        self.new_doc_window = NewDocWindow()
        self.new_doc_window.show()

    def update_filter(self):
        self._filter = self.search_bar.text()

        for button in self._docButtons:
            if(self._filter.lower() in button.name.lower()):
                print(self._filter)
                print(button.name)
                button.show()
            else:
                button.hide()




class NewDocWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Add New Document")

        self.settings = NewDocOptions()

        layout = QHBoxLayout()
        layout.addWidget(self.settings)
        # TODO: Create some kind of preview for the selected image files
        self.setLayout(layout)


class NewDocOptions(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file_names = []

        self.choose_file_button = QPushButton("Choose images")
        self.choose_file_button.clicked.connect(self.choose_files)

        self.options = QGroupBox("Options")
        self.name_label = QLabel("Document Name: ")
        self.name_edit = QLineEdit()
        options_layout = QVBoxLayout()
        options_layout.addWidget(self.name_label)
        options_layout.addWidget(self.name_edit)
        self.options.setLayout(options_layout)

        self.submit = QPushButton("Process Document")
        self.submit.clicked.connect(self.process_document)

        layout = QVBoxLayout()
        layout.addWidget(self.choose_file_button)
        layout.addWidget(self.options)
        layout.addWidget(self.submit, alignment=Qt.AlignBottom)
        self.setLayout(layout)

    def choose_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(
            "Images (*.png *.xpm *.jpg);;PDF Files (*.pdf);;Powerpoint Files (*.pptx)")
        file_dialog.selectNameFilter("Images (*.png *.xpm *.jpg)")

        if file_dialog.exec_():
            self.file_names = file_dialog.selectedFiles()

    def process_document(self):
        print('Process document clicked')
        # TODO: Spawn a new process to handle processing the new document

# I get an error saying the methods are undefined if the method is inside the DocWindow class
# reference for writeTofile: https://pynative.com/python-sqlite-blob-insert-and-retrieve-digital-data/

def writeTofile(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")
def resize_keep_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    new_dim = None
    h, w = image.shape[:2]

    if width is None and height is None:
        return image
    elif width is None:
        ratio = height / h
        new_dim = (int(w * ratio), height)
    else:
        ratio = width / w
        new_dim = (width, int(h * ratio))

    return cv2.resize(image, new_dim, interpolation=inter)

class DocWindow(QWidget):
    def __init__(self, doc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(doc.name)
        # TODO: Implement

        self._doc = doc

        self._filter = ''

        layout = QVBoxLayout()

        #search bar
        self.search_bar = QLineEdit()

        self.search_bar.setPlaceholderText("Search through notes...")

        self.search_bar.textChanged.connect(self.update_filter)

        layout.addWidget(self.search_bar, alignment=Qt.AlignTop)

        self.setLayout(layout)
    def resize_keep_aspect_ratio(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        new_dim = None
        h, w = image.shape[:2]

        if width is None and height is None:
            return image
        elif width is None:
            ratio = height / h
            new_dim = (int(w * ratio), height)
        else:
            ratio = width / w
            new_dim = (width, int(h * ratio))

        return cv2.resize(image, new_dim, interpolation=inter)

    def update_filter(self):
        #set filter to the value in the search bar
        self._filter = self.search_bar.text()

        #filter through each block in the pages of the document
        #pick the page with the first matching block to display
        setBlocks = set()
        listBlocks = []
        pageChosen = (self._doc.pages)[0]
        for page in self._doc.pages:
            for block in page.blocks:
                #if the filter value is contained in the text, print to console
                if(self._filter.lower() in block.text.lower()):
                    print(block.text)
                    if(block not in setBlocks):
                        listBlocks.append((block.left, block.top, block.width, block.height,page.number))
                        setBlocks.add(block)
        #doc_window2 = DocWindow2(list, page)
        #doc_window2.show()
        pageChosen = (self._doc.pages)[listBlocks[0][4]]
        writeTofile(pageChosen.image, "../test_img/conv_props3.jpg")
        img = cv2.imread("../test_img/conv_props3.jpg")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        for i in range(len(setBlocks)):
             img = cv2.rectangle(img, (listBlocks[i][0], listBlocks[i][1]), (listBlocks[i][0] + listBlocks[i][2], listBlocks[i][1] + listBlocks[i][3]), (255, 0, 0), 2)
        img_small = resize_keep_aspect_ratio(img, height=2000)
        cv2.imshow('img', img_small)
        #it should display for only 1 frame but it's not
        cv2.waitKey(1)

# Probably need to switch from cv2 display to inside a QT window
class DocWindow2(QWidget):
    def __init__(self, matchesCoordinates, page, input,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(input)
        qimg = QImage.fromData(page.image)
        pixmap = QPixmap.fromImage(qimg)

class SingleDocumentButton(QToolButton):
    def __init__(self, name, image, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._name = name

        self.setFixedSize(160, 160)

        layout = QVBoxLayout()

        label = QLabel(name)
        if image is not None:
            thumbnail = DocumentThumbnail(image, 140)
            layout.addWidget(thumbnail, alignment=Qt.AlignCenter)

        layout.addWidget(label, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name


class DocumentThumbnail(QLabel):
    def __init__(self, image, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qimg = QImage.fromData(image)
        self.height = height
        self.width = int((self.height / qimg.height()) * qimg.width())
        self.pixmap = QPixmap.fromImage(qimg)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return QSize(self.width, self.height)


if __name__ == "__main__":
    main()
