import logging
import os
from pathlib import Path

from PySide2.QtCore import QProcess
from PySide2.QtCore import QStandardPaths
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QComboBox
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QProgressBar
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from pycmd2.common.config import TomlConfigMixin


class VideoConverterConfig(TomlConfigMixin):
    SRC_DIR = Path.home() / "Desktop"
    OUTPUT_DIR = Path.home() / "Desktop"
    TITLE = "FFmpeg 视频转换工具"
    WIN_SIZE = [720, 0]


conf = VideoConverterConfig()


class VideoConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(conf.TITLE)
        self.setMinimumSize(*conf.WIN_SIZE)

        # 主部件和布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # 输入文件选择
        self.input_layout = QHBoxLayout()
        self.input_label = QLabel("输入文件:")
        self.input_path = QLineEdit()
        self.input_button = QPushButton("浏览...")
        self.input_button.clicked.connect(self.select_input_file)
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_path)
        self.input_layout.addWidget(self.input_button)

        # 输出文件选择
        self.output_layout = QHBoxLayout()
        self.output_label = QLabel("输出目录:")
        self.output_path = QLineEdit()
        self.output_button = QPushButton("浏览...")
        self.output_button.clicked.connect(self.select_output_dir)
        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_path)
        self.output_layout.addWidget(self.output_button)

        # 输出文件名
        self.output_name_layout = QHBoxLayout()
        self.output_name_label = QLabel("输出文件名:")
        self.output_name = QLineEdit()
        self.output_name.setPlaceholderText("例如: output.mp4")
        self.output_name_layout.addWidget(self.output_name_label)
        self.output_name_layout.addWidget(self.output_name)

        # 格式选择
        self.format_layout = QHBoxLayout()
        self.format_label = QLabel("输出格式:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "avi", "mov", "mkv", "flv", "webm"])
        self.format_layout.addWidget(self.format_label)
        self.format_layout.addWidget(self.format_combo)

        # 质量选择
        self.quality_layout = QHBoxLayout()
        self.quality_label = QLabel("质量:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["高", "中", "低"])
        self.quality_layout.addWidget(self.quality_label)
        self.quality_layout.addWidget(self.quality_combo)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # 转换按钮
        self.convert_button = QPushButton("开始转换")
        self.convert_button.clicked.connect(self.start_conversion)

        # 添加到主布局
        self.layout.addLayout(self.input_layout)
        self.layout.addLayout(self.output_layout)
        self.layout.addLayout(self.output_name_layout)
        self.layout.addLayout(self.format_layout)
        self.layout.addLayout(self.quality_layout)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.convert_button)

        # FFmpeg 进程
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self.conversion_finished)

        # 设置默认输出路径为文档目录
        docs_path = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation
        )
        self.output_path.setText(docs_path)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv *.webm);;所有文件 (*.*)",
        )
        if file_path:
            self.input_path.setText(file_path)
            # 自动设置输出文件名
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_name.setText(f"{base_name}_converted")

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_path.setText(dir_path)

    def start_conversion(self):
        input_file = self.input_path.text()
        output_dir = self.output_path.text()
        output_name = self.output_name.text()
        output_format = self.format_combo.currentText()
        quality = self.quality_combo.currentText()

        # 验证输入
        if not input_file or not os.path.exists(input_file):
            QMessageBox.critical(self, "错误", "请选择有效的输入文件")
            return

        if not output_dir or not os.path.isdir(output_dir):
            QMessageBox.critical(self, "错误", "请选择有效的输出目录")
            return

        if not output_name:
            QMessageBox.critical(self, "错误", "请输入输出文件名")
            return

        # 构建输出路径
        output_file = os.path.join(output_dir, f"{output_name}.{output_format}")

        # 检查输出文件是否已存在
        if os.path.exists(output_file):
            reply = QMessageBox.question(
                self,
                "文件已存在",
                "输出文件已存在，是否覆盖?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        # 构建 FFmpeg 命令
        cmd = ["ffmpeg", "-i", input_file]

        # 根据质量设置参数
        if quality == "高":
            cmd.extend(["-c:v", "libx264", "-crf", "18", "-preset", "slow"])
        elif quality == "中":
            cmd.extend(["-c:v", "libx264", "-crf", "23", "-preset", "medium"])
        else:  # 低
            cmd.extend(["-c:v", "libx264", "-crf", "28", "-preset", "fast"])

        cmd.extend(["-c:a", "aac", "-strict", "experimental", "-b:a", "192k"])
        cmd.append(output_file)

        # 显示命令（调试用）
        print("执行命令:", " ".join(cmd))

        # 禁用按钮，防止重复点击
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)

        # 启动进程
        self.process.start(cmd[0], cmd[1:])

    def handle_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        print("输出:", output)
        # 这里可以解析进度信息来更新进度条

    def handle_error(self):
        error = self.process.readAllStandardError().data().decode()
        print("错误:", error)

        # 尝试从错误输出中解析进度
        if "time=" in error:
            time_pos = error.find("time=")
            time_str = error[time_pos + 5 : time_pos + 13]
            try:
                # 简单的时间进度计算（实际应用中需要更复杂的解析）
                h, m, s = map(float, time_str.split(":"))
                total_seconds = h * 3600 + m * 60 + s
                # 假设视频长度为60秒（实际应用中需要获取真实长度）
                progress = (total_seconds / 60) * 100
                self.progress_bar.setValue(min(int(progress), 100))
            except Exception as e:
                logging.error("解析进度信息失败:", e)

    def conversion_finished(self, exit_code, exit_status):
        self.convert_button.setEnabled(True)

        if exit_code == 0:
            QMessageBox.information(self, "完成", "视频转换完成!")
            self.progress_bar.setValue(100)
        else:
            QMessageBox.critical(
                self, "错误", f"转换失败，错误代码: {exit_code}"
            )
            self.progress_bar.setValue(0)


def main():
    app = QApplication([])
    converter = VideoConverter()
    converter.show()
    app.exec_()


if __name__ == "__main__":
    main()
