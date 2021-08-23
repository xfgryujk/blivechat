# -*- coding: utf-8 -*-

import logging
import os
import re

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from window import main, setting, console

JS_LOAD_CSS_FROM_URL = '''(function(){
    let link = document.createElement('link');
    link.href = '%s';
    link.rel = 'stylesheet';
    document.head.append(link);
    console.log('Additional link to style sheet:\\n', link);
})();
'''
JS_LOAD_CSS_FROM_STR = '''(function(){
    let style_node = document.createElement('style');
    style_node.append(document.createTextNode(`\n%s\n`));
    document.head.append(style_node);
    console.log('Additional inline style sheet:\\n', style_node);
})();
'''
ESCAPE_REGEX = re.compile(r'([`\\])')

logger = logging.getLogger(__name__)


class BrowserRoot(QWidget):
    def __init__(self):
        super().__init__()
        logger.debug('Open a browser')
        self.setWindowTitle('room')
        self.setWindowIcon(QIcon(QPixmap(
            'frontend/dist/favicon.ico'
            if os.path.exists('frontend/dist/favicon.ico')
            else 'frontend/public/favicon.ico'
        )))
        self.setWindowOpacity(main.configs['float']['transparent']/100)
        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.webview = WebView()
        self.webview.page().setBackgroundColor(QColor(0x00, 0x00, 0x00, 0x00))
        self.webview.titleChanged.connect(self.setWindowTitle)
        self.update_executes = [
            lambda: self.move(main.configs['float']['x'], main.configs['float']['y']),
            lambda: self.resize(main.configs['float']['width'], main.configs['float']['height']),
            lambda: self.webview.page().setZoomFactor(main.configs['float']['scale']/100)
        ]
        self.horizontal_layout.addWidget(self.webview)
        self.setLayout(self.horizontal_layout)

        self.lock(True)
        self.update_executes[0]()
        self.update_executes[1]()
        main.room_url = setting.get_url()
        self.webview.load(QUrl(main.room_url))
        self.update_executes[2]()
        self.show()

    def load_url(self, url):
        self.webview.load(QUrl(url))

    def lock(self, on: bool):
        self.setAttribute(Qt.WA_TransparentForMouseEvents, on)
        self.setWindowFlag(Qt.FramelessWindowHint, on)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, on)
        self.setAttribute(Qt.WA_TranslucentBackground, on)

    def update_adjust(self, index: int = 3):
        if index < 3:
            self.update_executes[index]()
        elif index == 3:
            for i in self.update_executes:
                i()

    def closeEvent(self, e: QCloseEvent):
        logger.debug('Close the browser')
        main.console.button_float_window.setText('公屏浮窗')
        main.console.action_float_window.setChecked(False)
        self.destroy()
        console.browser_instance = None
        super().closeEvent(e)


class WebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        java_script = ''
        for i in main.configs['css']:
            java_script += get_css_insert_script(i)
        script = QWebEngineScript()
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setSourceCode(java_script)
        self.page().scripts().insert(script)

    def additional_css(self, css):
        script = get_css_insert_script(css)
        self.page().runJavaScript(script)


def get_css_insert_script(css):
    if QUrl == type(css) and css.isLocalFile() and os.path.isfile(css.toLocalFile()):
        with open(css.toLocalFile(), 'r', encoding='UTF-8') as file:
            return JS_LOAD_CSS_FROM_STR % ESCAPE_REGEX.sub(
                repl=lambda matched: '\\%s' % matched.group(0),
                string=file.read()
            )
    elif QUrl == type(css) and not css.isLocalFile():
        return JS_LOAD_CSS_FROM_URL % bytes(css.toEncoded()).decode('ASCII')
    elif str == type(css) and os.path.isfile(css):
        with open(css, 'r', encoding='UTF-8') as file:
            return JS_LOAD_CSS_FROM_STR % ESCAPE_REGEX.sub(
                repl=lambda matched: '\\%s' % matched.group(0),
                string=file.read()
            )
    elif str == type(css):
        return JS_LOAD_CSS_FROM_STR % ESCAPE_REGEX.sub(
            repl=lambda matched: '\\%s' % matched.group(0),
            string=css
        )
    else:
        logger.warning(
            'Generated script error: Unknown type of stylesheet. \nType: %s\nPointer: %s\n-----\n%s' %
            (type(css), id(css), css)
        )
