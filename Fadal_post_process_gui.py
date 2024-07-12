import sys
import glob
from copy import copy
from pathlib import Path, PurePath
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QListWidget, QLineEdit, QMessageBox, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt

def process_files(files, fnames, directory):
    first_line_corrected = False
    o_filenames = []
    i_filenames = [Path(file) for file in files] # convert to Path objects
    
    # Handle the star operator (Windows is not as good as shell in this regard) as an input. IE resolve to all the nc files in the directory
    if len(i_filenames) == 1 and i_filenames[0].name == '*.nc':
        i_filenames = [Path(file) for file in glob.glob(str(i_filenames[0]))]
        
    if fnames is not None:
        if len(fnames) != len(files):
            QMessageBox.critical(None, "Error", "Number of output names must equal number of input names")
            return
        else:
            o_filenames = [Path(name) for name in fnames]
    else:
        o_filenames = copy(i_filenames)
        
    directory = Path(directory)
    
    for i, path in enumerate(o_filenames):
        if fnames is not None:
            o_filenames[i] = directory / path.name
        else:
            o_filenames[i] = directory / (path.stem + "_fd.nc")
            
    for f_index, fin in enumerate(i_filenames):
        print("Processing " + str(fin) + " -> " + str(o_filenames[f_index]))
        with fin.open() as f:
            with o_filenames[f_index].open(mode='w') as fout:
                input = f.readlines()
                input = [i.strip() for i in input]
                length = len(input)
                prog_len = 0
                old_coord = 0
                for number, line in enumerate(input):
                    if number > length - 13:
                        break
                    words = line.split()
                    if number == length - 14:
                        prog_len = int(words[0][1:])
                    for i, word in enumerate(words):
                        if word == "N10" and first_line_corrected == False:
                            fout.write("N10 G0G17G40G49G70G80G90G98")
                            words = []
                            first_line_corrected = True
                            break
                        if word[0] == 'A':
                            coord = float(word[1:])
                            # Modulus makes it so the sign is only ever between 0 and 360
                            if coord > old_coord:
                                words[i] = 'A'+f"{coord%360:.3f}" #if the new coordinate is larger than the old coordinate, the sign of the a coordinate should be positive
                            else:
                                words[i] = 'A-'+f"{coord%360:.3f}" #if the new coordinate is less than the old coordinate, the sign of the a coordinate should be negative
                            old_coord = coord
                        if word == 'M11':
                            words[i] = 'M61'
                        if word == 'M10':
                            words[i] = 'M60'
                        if word == 'F500.':
                            words[i] = 'F300.'
                        if word == 'G54': #fixture offsets
                            words[i] = 'E1'
                        if word == "G53":  #use machine coordinate system
                            words.pop(i)
                    line = " ".join(words)
                    if number > 1:
                        fout.write(line + "\n")
                fout.write("\n")
                fout.write("N"+str(prog_len+5)+" M5 M9\n")
                fout.write("N"+str(prog_len+15)+" G0 Z0 G49\n")
                fout.write("N"+str(prog_len+20)+" G0 X0 Y0 E0\n")
                fout.write("N"+str(prog_len+25)+" M2\n")
                fout.write("\n")
                fout.write("%\n")
                fout.write("\n")
    QMessageBox.information(None, "Success", "Files processed successfully!")

class GCodePostProcessor(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Fadal 4th Axis GCode Post-Processor')

        layout = QVBoxLayout()

        self.file_listbox = QListWidget(self)
        self.file_listbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.file_listbox)

        file_button_layout = QHBoxLayout()
        self.select_files_button = QPushButton('Select Files', self)
        self.select_files_button.clicked.connect(self.select_files)
        file_button_layout.addWidget(self.select_files_button)
        layout.addLayout(file_button_layout)

        self.output_fnames_label = QLabel('Output Filenames (space-separated):', self)
        layout.addWidget(self.output_fnames_label)

        self.output_fnames_edit = QLineEdit(self)
        self.output_fnames_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.output_fnames_edit)

        dir_button_layout = QHBoxLayout()
        self.output_dir_button = QPushButton('Select Output Directory', self)
        self.output_dir_button.clicked.connect(self.select_output_directory)
        dir_button_layout.addWidget(self.output_dir_button)
        layout.addLayout(dir_button_layout)

        self.output_dir_label = QLabel('No directory selected', self)
        layout.addWidget(self.output_dir_label)

        process_button_layout = QHBoxLayout()
        self.process_button = QPushButton('Process', self)
        self.process_button.clicked.connect(self.run_processing)
        process_button_layout.addWidget(self.process_button)
        layout.addLayout(process_button_layout)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #d3d3d3;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3b3b3b;
                color: #d3d3d3;
                border: 1px solid #555555;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QLabel {
                padding: 5px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3b3b3b;
                color: #d3d3d3;
            }
            QListWidget {
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3b3b3b;
                color: #d3d3d3;
            }
            QScrollBar {
                background: #2b2b2b;
                border: 1px solid #3b3b3b;
            }
            QScrollBar::handle {
                background: #555555;
            }
            QScrollBar::handle:hover {
                background: #777777;
            }
        """)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "NC files (*.nc)")
        if files:
            self.file_listbox.clear()
            for file in files:
                self.file_listbox.addItem(file)

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_label.setText(directory)

    def run_processing(self):
        files = [self.file_listbox.item(i).text() for i in range(self.file_listbox.count())]
        fnames = self.output_fnames_edit.text().split() if self.output_fnames_edit.text() else None
        directory = self.output_dir_label.text() if self.output_dir_label.text() != 'No directory selected' else "."
        if not files:
            QMessageBox.critical(self, "Error", "No input files selected")
            return
        process_files(files, fnames, directory)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GCodePostProcessor()
    ex.resize(600, 400)  # Set initial size
    ex.show()
    sys.exit(app.exec_())
