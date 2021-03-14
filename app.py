import random
import sys
from functools import partial

import pandas as pandas
import numpy as np
from random import sample
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QGridLayout, QDialog, QMessageBox, QLineEdit, \
    QComboBox


class AnyDictionaryTester(QWidget):
    is_hard_mode = False
    is_hard_mode_with_autocomplete = None

    dialogs = []
    dictionary = {}
    dialogs_iterator = iter(dialogs)
    current_dialog: QDialog = None

    answers_count = 0
    correct_answers_count = 0

    grid = QGridLayout()

    def set_answer(self, word, answer):
        self.answers_count += 1
        correct_translation = self.dictionary[word]
        if correct_translation != answer:
            wrong_answer_message_box = QMessageBox(QMessageBox.Critical, 'Incorrect',
                                                   '"' + word + '" is "' + correct_translation + '"')
            wrong_answer_message_box.exec_()
            wrong_answer_message_box.deleteLater()
        else:
            self.correct_answers_count += 1

        self.grid.removeWidget(self.current_dialog)
        self.current_dialog.hide()
        self.current_dialog.deleteLater()

        try:
            self.current_dialog = next(self.dialogs_iterator)
            self.grid.addWidget(self.current_dialog)

            if self.is_hard_mode:
                self.current_dialog.layout().itemAt(1).widget().setFocus()
        except StopIteration:
            self.close()

    def __init__(self, dictionary: dict):
        super().__init__()

        self.dictionary = dictionary

        self.setFocus()
        self.setMinimumWidth(300)
        self.setWindowTitle('Any Dictionary Tester')
        self.setFont(QFont('Arial', 14))

        self.setLayout(self.grid)

        words = list(dictionary.keys())
        random.shuffle(words)

        ask_message_box = QMessageBox(
            QMessageBox.Question,
            'Configuration',
            'Enable hard mode?',
            QMessageBox.Yes | QMessageBox.No
        )
        ask_message_box.exec_()
        ask_message_box.deleteLater()
        self.is_hard_mode = ask_message_box.result() == ask_message_box.Yes

        if self.is_hard_mode:
            ask_message_box = QMessageBox(
                QMessageBox.Question,
                'Configuration',
                'Use autocomplete?',
                QMessageBox.Yes | QMessageBox.No
            )
            ask_message_box.exec_()
            ask_message_box.deleteLater()
            self.is_hard_mode_with_autocomplete = ask_message_box.result() == ask_message_box.Yes

        for word in words:
            dialog = QDialog()

            dialog_grid = QGridLayout()
            dialog.setLayout(dialog_grid)

            values = list(np.random.choice(list(dictionary.values()), 4, replace=False))

            if dictionary[word] not in values:
                values.remove(values[0])
                values.append(dictionary[word])
                random.shuffle(values)

            original_word_label = QLabel(word)
            dialog_grid.addWidget(original_word_label, 0, 0, Qt.AlignCenter)

            if self.is_hard_mode and not self.is_hard_mode_with_autocomplete:
                answer_line_edit = QLineEdit()
                answer_line_edit.returnPressed.connect(
                    lambda associated_word=word, associated_line_edit=answer_line_edit:
                    self.set_answer(associated_word, associated_line_edit.text())
                )
                dialog_grid.addWidget(answer_line_edit, 1, 0)

                answer_button = QPushButton("Answer")
                answer_button.clicked.connect(
                    lambda state, associated_word=word, associated_line_edit=answer_line_edit:
                    self.set_answer(associated_word, associated_line_edit.text())
                )
                dialog_grid.addWidget(answer_button, 2, 0)
            elif self.is_hard_mode and self.is_hard_mode_with_autocomplete:
                answer_combo_box = QComboBox()

                answer_combo_box.setEditable(True)
                answer_combo_box.addItems(sample(list(dictionary.values()), len(dictionary.values())))
                answer_combo_box.setCurrentText('')
                answer_combo_box.lineEdit().returnPressed.connect(
                    lambda associated_word=word, associated_combo_box=answer_combo_box:
                    self.set_answer(associated_word, associated_combo_box.currentText())
                )
                dialog_grid.addWidget(answer_combo_box, 1, 0)

                answer_button = QPushButton("Answer")
                answer_button.clicked.connect(
                    lambda state, associated_word=word, associated_combo_box=answer_combo_box:
                    self.set_answer(associated_word, associated_combo_box.currentText())
                )
                dialog_grid.addWidget(answer_button, 2, 0)
            else:
                for i in range(4):
                    answer_button = QPushButton(values[i])
                    answer_button.clicked.connect(partial(self.set_answer, word, values[i]))
                    dialog_grid.addWidget(answer_button, i + 1, 0)

            self.dialogs.append(dialog)

        self.current_dialog = next(self.dialogs_iterator)
        self.grid.addWidget(self.current_dialog)

        self.show()

    def closeEvent(self, event):
        if self.answers_count != 0:
            complete_message_box = QMessageBox(QMessageBox.Information,
                                               'Test completed',
                                               'The percentage of correct answers is {0:.0%}.'
                                               .format(float(self.correct_answers_count) / self.answers_count))
            complete_message_box.exec_()
            complete_message_box.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dictionary_data_frame = pandas.read_csv('dictionary.csv', header=None)

    ex = AnyDictionaryTester(dict(zip(dictionary_data_frame[0], dictionary_data_frame[1])))
    sys.exit(app.exec_())
