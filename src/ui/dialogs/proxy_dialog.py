from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QFrame,
                             QRadioButton, QButtonGroup, QLineEdit, QScrollArea, QComboBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
from src.ui.dialogs.base_dialog import BaseDialog
from src.utils.theme import Theme


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class ProxyDialog(BaseDialog):
    def __init__(self, parent=None, colors=None):
        self.proxy_path = ''
        self.proxy_format = 'host_port_login_password'
        self.proxy_type = 'socks5'
        super().__init__(parent, colors)
        self.setup_ui()

    def setup_ui(self):
        self.setup_frameless(480, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = self._create_header()
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content = self._create_content()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        footer = self._create_footer()
        layout.addWidget(footer)

    def _create_header(self) -> QWidget:
        header = QWidget()
        header.setStyleSheet(f"background: {self.colors['dialog_bg']}; border-radius: 12px 12px 0 0;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 25, 30, 20)
        header_layout.setSpacing(15)

        title = QLabel('Загрузка прокси')
        title.setFont(QFont('Segoe UI', 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.colors['text_primary']}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        desc = QLabel('Настрой параметры')
        desc.setFont(QFont('Segoe UI', 9))
        desc.setStyleSheet(f"color: {self.colors['text_secondary']}; background: transparent;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(desc)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedWidth(120)
        divider.setFixedHeight(2)
        divider.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.5 #17a2b8, stop:1 transparent); border: none;")
        divider_container = QWidget()
        divider_container.setStyleSheet("background: transparent;")
        divider_layout = QHBoxLayout(divider_container)
        divider_layout.setContentsMargins(0, 0, 0, 0)
        divider_layout.addStretch()
        divider_layout.addWidget(divider)
        divider_layout.addStretch()
        header_layout.addWidget(divider_container)

        return header

    def _create_content(self) -> QWidget:
        content = QWidget()
        content.setStyleSheet(f"background: {self.colors['dialog_bg']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(18)

        format_label = QLabel('Формат прокси')
        format_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        format_label.setStyleSheet(f"color: {self.colors['text_primary']}; background: transparent;")
        content_layout.addWidget(format_label)

        self.format_group = QButtonGroup(self)

        self.rb_host_port = QRadioButton('host:port:login:password')
        self.rb_host_port.setFont(QFont('Segoe UI', 9))
        self.rb_host_port.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rb_host_port.setChecked(True)
        self.rb_host_port.setStyleSheet(Theme.get_radio_style(self.colors))
        self.format_group.addButton(self.rb_host_port)
        content_layout.addWidget(self.rb_host_port)

        self.rb_login_pass = QRadioButton('login:password:host:port')
        self.rb_login_pass.setFont(QFont('Segoe UI', 9))
        self.rb_login_pass.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rb_login_pass.setStyleSheet(Theme.get_radio_style(self.colors))
        self.format_group.addButton(self.rb_login_pass)
        content_layout.addWidget(self.rb_login_pass)

        self.rb_at_format = QRadioButton('login:password@host:port')
        self.rb_at_format.setFont(QFont('Segoe UI', 9))
        self.rb_at_format.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rb_at_format.setStyleSheet(Theme.get_radio_style(self.colors))
        self.format_group.addButton(self.rb_at_format)
        content_layout.addWidget(self.rb_at_format)

        type_label = QLabel('Тип прокси:')
        type_label.setFont(QFont('Segoe UI', 8))
        type_label.setStyleSheet(f"color: {self.colors['text_secondary']}; background: transparent; margin-top: 8px;")
        content_layout.addWidget(type_label)

        self.combo_type = NoScrollComboBox()
        self.combo_type.addItems(['socks5', 'http', 'https'])
        self.combo_type.setFont(QFont('Segoe UI', 9))
        self.combo_type.setFixedHeight(34)
        self.combo_type.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_type.setStyleSheet(Theme.get_combobox_style(self.colors))
        content_layout.addWidget(self.combo_type)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background: {self.colors['divider']}; max-height: 1px; margin: 5px 0;")
        content_layout.addWidget(separator)

        path_label = QLabel('Путь к прокси')
        path_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        path_label.setStyleSheet(f"color: {self.colors['text_primary']}; background: transparent;")
        content_layout.addWidget(path_label)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(8)

        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText('Укажи путь к файлу с прокси')
        self.input_path.setFixedHeight(38)
        self.input_path.setStyleSheet(Theme.get_input_style(self.colors))
        path_layout.addWidget(self.input_path)

        btn_browse = QPushButton('...')
        btn_browse.setFont(QFont('Segoe UI', 14))
        btn_browse.setFixedSize(38, 38)
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['input_border']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {self.colors['button_hover']};
                border-color: {self.colors['input_focus']};
            }}
        """)
        btn_browse.clicked.connect(self.browse_file)
        path_layout.addWidget(btn_browse)

        content_layout.addLayout(path_layout)
        content_layout.addStretch()

        return content

    def _create_footer(self) -> QWidget:
        footer = QWidget()
        footer.setStyleSheet(f"background: {self.colors['dialog_bg']}; border-radius: 0 0 12px 12px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(25, 15, 25, 20)
        footer_layout.setSpacing(10)

        btn_check = QPushButton('Проверить прокси')
        btn_check.setFont(QFont('Segoe UI', 9))
        btn_check.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_check.setFixedSize(130, 36)
        btn_check.setStyleSheet("""
            QPushButton {
                background: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #e0a800;
            }
            QPushButton:disabled {
                background: #6c757d;
                color: #999999;
            }
        """)
        btn_check.clicked.connect(self.check_proxies)
        footer_layout.addWidget(btn_check)

        footer_layout.addStretch()

        btn_cancel = QPushButton('Отмена')
        btn_cancel.setFont(QFont('Segoe UI', 9))
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedSize(90, 36)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.colors['text_secondary']};
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                color: {self.colors['text_primary']};
                background: {self.colors['button_hover']};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        footer_layout.addWidget(btn_cancel)

        btn_load = QPushButton('Загрузить')
        btn_load.setFont(QFont('Segoe UI', 9))
        btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_load.setFixedSize(100, 36)
        btn_load.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['info']};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: #138496;
            }}
        """)
        btn_load.clicked.connect(self.load_proxies)
        footer_layout.addWidget(btn_load)

        return footer

    def _get_format(self) -> str:
        if self.rb_at_format.isChecked():
            return 'at_format'
        return 'host_port_login_password' if self.rb_host_port.isChecked() else 'login_password_host_port'

    def browse_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл с прокси", "", "Text Files (*.txt);;All Files (*)")
        if file:
            self.input_path.setText(file)

    def check_proxies(self):
        path = self.input_path.text().strip()
        if not path or not os.path.exists(path):
            self.input_path.setStyleSheet(Theme.get_error_input_style())
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f if line.strip()]
            if not proxies:
                return
            from src.ui.dialogs.proxy_check_dialog import ProxyCheckDialog
            ProxyCheckDialog(proxies, self.combo_type.currentText(), self._get_format(), self).exec()
        except Exception:
            pass

    def load_proxies(self):
        path = self.input_path.text().strip()
        if not path or not os.path.exists(path):
            self.input_path.setStyleSheet(Theme.get_error_input_style())
            return
        self.proxy_path = path
        self.proxy_format = self._get_format()
        self.proxy_type = self.combo_type.currentText()
        self.accept()

    def get_data(self):
        proxies = []
        try:
            with open(self.proxy_path, 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f if line.strip()]
        except Exception:
            pass

        return {
            'path': self.proxy_path,
            'proxies': proxies,
            'format': self.proxy_format,
            'type': self.proxy_type
        }
