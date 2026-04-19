from PyQt6.QtWidgets import (QVBoxLayout, QPushButton, QLabel, QTextEdit, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
import ssl

from src.utils.proxy import parse_proxy, to_url


class ProxyCheckThread(QThread):
    progress = pyqtSignal(str, str)
    finished = pyqtSignal(int, int)

    def __init__(self, proxies, proxy_type, proxy_format):
        super().__init__()
        self.proxies = proxies
        self.proxy_type = proxy_type
        self.proxy_format = proxy_format
        self.valid_count = 0
        self.invalid_count = 0

    async def check_single(self, proxy_line):
        try:
            proxy_data = parse_proxy(proxy_line, self.proxy_format)
            if not proxy_data:
                return False

            proxy_url = to_url(proxy_data, self.proxy_type)

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = ProxyConnector.from_url(proxy_url, ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=2, connect=1)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get('https://httpbin.org/ip', timeout=timeout, ssl=ssl_context) as response:
                    if response.status == 200:
                        return True
            return False
        except Exception:
            return False

    async def check_all(self):
        semaphore = asyncio.Semaphore(100)

        async def check_with_semaphore(proxy):
            async with semaphore:
                result = await self.check_single(proxy)
                if result:
                    self.valid_count += 1
                    self.progress.emit(proxy, 'valid')
                else:
                    self.invalid_count += 1
                    self.progress.emit(proxy, 'invalid')

        tasks = [check_with_semaphore(proxy) for proxy in self.proxies]
        await asyncio.gather(*tasks)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.check_all())
            self.finished.emit(self.valid_count, self.invalid_count)
        finally:
            loop.close()


class ProxyCheckDialog(QDialog):
    def __init__(self, proxies, proxy_type, proxy_format, parent=None):
        super().__init__(parent)
        self.proxies = proxies
        self.proxy_type = proxy_type
        self.proxy_format = proxy_format
        self.drag_position = None
        self.check_thread = None
        self.setup_ui()
        self.start_check()

    def setup_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(600, 450)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background: #ffffff;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel('Проверка прокси')
        title.setFont(QFont('Segoe UI', 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #212529;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.status_label = QLabel('Проверка...')
        self.status_label.setFont(QFont('Segoe UI', 9))
        self.status_label.setStyleSheet("color: #6c757d;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont('Consolas', 8))
        self.terminal.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                color: #d4d4d4;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.terminal)

        self.btn_close = QPushButton('Закрыть')
        self.btn_close.setFont(QFont('Segoe UI', 9))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFixedHeight(36)
        self.btn_close.setEnabled(False)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #5a6268;
            }
            QPushButton:disabled {
                background: #e9ecef;
                color: #adb5bd;
            }
        """)
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)

    def start_check(self):
        self.check_thread = ProxyCheckThread(self.proxies, self.proxy_type, self.proxy_format)
        self.check_thread.progress.connect(self.on_progress)
        self.check_thread.finished.connect(self.on_finished)
        self.check_thread.start()

    def on_progress(self, proxy, status):
        if status == 'valid':
            self.terminal.append(f'<span style="color: #66bb6a;">+ {proxy}</span>')
        else:
            self.terminal.append(f'<span style="color: #ef5350;">- {proxy}</span>')

    def on_finished(self, valid, invalid):
        self.status_label.setText(f'Валидных: {valid} | Невалидных: {invalid}')
        self.terminal.append('\n<span style="color: #4fc3f7;">Проверка завершена</span>')
        self.btn_close.setEnabled(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
