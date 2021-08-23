# -*- coding: utf-8 -*-

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QCloseEvent, QMoveEvent, QResizeEvent
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QMessageBox, QDialog

from window import main, console
from window.desinger.ui_float_scale import Ui_form


class AdjustBox(QWidget):
    def __init__(self):
        super().__init__()
        self.move(
            main.configs['float']['x'],
            main.configs['float']['y']
        )
        self.resize(
            main.configs['float']['width'] - console.window_frame_delta_width,
            main.configs['float']['height'] - console.window_frame_delta_height
        )
        self.setWindowTitle('悬浮窗调整')
        self.setWindowIcon(QIcon(QPixmap(
            'frontend/dist/favicon.ico'
            if os.path.exists('frontend/dist/favicon.ico')
            else 'frontend/public/favicon.ico'
        )))
        self.horizontal_layout = QHBoxLayout(self)
        self.label_message = QLabel(self)
        self.label_message.setAlignment(Qt.AlignCenter)
        self.horizontal_layout.addWidget(self.label_message)
        self.setLayout(self.horizontal_layout)
        self.show()
        if not main.configs['float']['mindedTransparent']:
            QMessageBox.information(
                main.console, '提示',
                '拖动、伸缩悬浮窗下的空白窗口，悬浮窗会跟随它变化。\n'
                '若您没有在悬浮窗下面看到一个空白的窗口，请先将悬浮窗不透明度降低。\n'
                '但调整窗口一直存在，只是被不透明的悬浮窗遮住而已。'
            )
            main.configs['float']['mindedTransparent'] = True

    def moveEvent(self, e: QMoveEvent):
        main.configs['float']['x'] = self.x()
        main.configs['float']['y'] = self.y()
        super().moveEvent(e)
        self.adjust_update(0)

    def resizeEvent(self, e: QResizeEvent):
        main.configs['float']['width'] = self.frameGeometry().width()
        main.configs['float']['height'] = self.frameGeometry().height()
        super().resizeEvent(e)
        self.adjust_update(1)

    def closeEvent(self, e: QCloseEvent):
        main.console.action_float_window_transform.setChecked(False)
        self.destroy()
        console.adjust_box_instance = None
        super().closeEvent(e)

    def adjust_update(self, update_index):
        if console.browser_instance is not None:
            console.browser_instance.update_adjust(update_index)
        self.label_message.setText('拖拽或缩放此窗口调整悬浮窗的位置和大小。\n\n位置：(%d,%d)\n大小：%d×%d' % (
            main.configs['float']['x'], main.configs['float']['y'],
            main.configs['float']['width'], main.configs['float']['height']
        ))


class TransformEdit(QDialog, Ui_form):
    def __init__(self):
        QWidget.__init__(self)
        Ui_form.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QIcon(QPixmap(
            'frontend/dist/favicon.ico'
            if os.path.exists('frontend/dist/favicon.ico')
            else 'frontend/public/favicon.ico'
        )))
        self.horizontal_slider_scale.valueChanged.connect(
            lambda: change_scale(self.horizontal_slider_scale.value())
        )
        self.horizontal_slider_scale.valueChanged.connect(self.spin_box_scale.setValue)
        self.spin_box_scale.valueChanged.connect(
            lambda: change_scale(self.spin_box_scale.value())
        )
        self.spin_box_scale.valueChanged.connect(self.horizontal_slider_scale.setValue)
        self.show()

    def closeEvent(self, e: QCloseEvent):
        main.console.action_float_window_transform_edit.setChecked(False)
        self.destroy()
        console.transform_edit_instance = None
        super().closeEvent(e)


def change_scale(percent: int):
    main.configs['float']['scale'] = percent
    if console.browser_instance is not None:
        console.browser_instance.update_adjust(2)
