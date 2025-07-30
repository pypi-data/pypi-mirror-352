from datetime import datetime

import qtawesome as qta
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QPlainTextEdit, QToolButton
from PyQt6.QtCore import Qt, pyqtSignal, QEvent

from bioview.utils import get_qcolor

class AnnotateEventPanel(QGroupBox):
    logEvent = pyqtSignal(str, str)
    
    def __init__(self, 
                 config, 
                 parent=None
        ):
        super().__init__('Mark Events', parent)    
        
        self.log_path = config.get_log_path()
        
        layout = QHBoxLayout()
        self.annotation_box = QPlainTextEdit(self)
        self.annotation_box.setReadOnly(False)
        layout.addWidget(self.annotation_box)
        
        self.make_annotation_button = QToolButton()
        self.make_annotation_button.setText('Mark Event')
        self.make_annotation_button.setIcon(qta.icon('fa6s.pen-to-square', color=get_qcolor('orange')))
        self.make_annotation_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.make_annotation_button.setEnabled(True)
        self.make_annotation_button.clicked.connect(self.record_annotation)
        layout.addWidget(self.make_annotation_button)
        
        self.setLayout(layout)
    
    # Handle theme changes 
    def _update_icons(self): 
        self.make_annotation_button.setIcon(qta.icon('fa6s.pen-to-square', color=get_qcolor('orange')))
        
    def event(self, event): 
        if event.type() == QEvent.Type.ApplicationPaletteChange: 
            self._update_icons()
        return super().event(event)
    
    def record_annotation(self):
        # Get current time, add to text file 
        try: 
            annotation = self.annotation_box.toPlainText()
            if not annotation.strip():  # Check if the text is empty or just whitespace
                self.logEvent.emit('debug', 'No text to append')
                
            with open(self.log_path, 'a') as f:
                f.write(f'{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {annotation}\n')
            
            self.annotation_box.clear()
        except Exception as e:
            self.logEvent.emit('error', f'An error occurred: {e}')
        

    