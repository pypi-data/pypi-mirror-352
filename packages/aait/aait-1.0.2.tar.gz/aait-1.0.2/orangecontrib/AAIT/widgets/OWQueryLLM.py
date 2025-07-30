import os
import sys

import Orange.data
from AnyQt.QtWidgets import QApplication, QLabel
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.widgets.settings import Setting
from AnyQt.QtWidgets import QLineEdit, QTextBrowser

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.llm import answers
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.llm import answers
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file

#TODO Ajouter un bouton d'autorun

@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWQueryLLM(widget.OWWidget):
    name = "Query LLM"
    description = "Generate a response to a column 'prompt' with a LLM"
    icon = "icons/owqueryllm.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owqueryllm.svg"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owqueryllm.ui")
    want_control_area = True
    priority = 1089

    class Inputs:
        data = Input("Data", Orange.data.Table)
        model_path = Input("Model", str)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    n_ctx: str = Setting("4096")
    workflow_id = Setting("")

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        if self.autorun:
            self.run()

    @Inputs.model_path
    def set_model_path(self, in_model_path):
        self.model_path = in_model_path
        answers.check_gpu(in_model_path, self)
        if self.autorun:
            self.run()

    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(700)
        self.setFixedHeight(500)
        uic.loadUi(self.gui, self)
        self.label_description = self.findChild(QLabel, 'Description')
        # Context size
        self.edit_nCtx = self.findChild(QLineEdit, 'lineEdit')
        self.edit_nCtx.setText(str(self.n_ctx))
        self.edit_nCtx.editingFinished.connect(self.update_n_ctx)
        # Text browser
        self.textBrowser = self.findChild(QTextBrowser, 'textBrowser')
        # Workflow ID for streaming
        self.edit_ID = self.findChild(QLineEdit, 'lineEdit_2')
        self.edit_ID.setText(self.workflow_id)
        self.edit_ID.editingFinished.connect(self.update_workflow_id)

        # # Data Management
        self.data = None
        self.model_path = None
        self.thread = None
        self.autorun = True
        self.use_gpu = False
        self.can_run = True
        self.result = None
        self.n_ctx = self.edit_nCtx.text() if self.edit_nCtx.text().isdigit() else "4096"
        self.workflow_id = self.edit_ID.text()

        # Custom updates
        self.post_initialized()

    def update_n_ctx(self):
        value = self.edit_nCtx.text()  # Read the current value
        self.n_ctx = value if value.isdigit() else "4096"  # Default or parsed value
        self.edit_nCtx.setText(self.n_ctx)
        answers.check_gpu(self.model_path, self)

    def update_workflow_id(self):
        self.workflow_id = self.edit_ID.text()
        if self.workflow_id != "":
            if self.thread is None:
                self.run()

    def run(self):
        if not self.can_run:
            return

        # If Thread is already running, interrupt it
        if self.thread is not None:
            if self.thread.isRunning():
                self.thread.safe_quit()

        if self.data is None:
            return

        if self.model_path is None or not os.path.exists(self.model_path):
            return

        if not "prompt" in self.data.domain:
            return

        # Start progress bar
        self.progressBarInit()
        self.textBrowser.setText("")

        # Connect and start thread : main function, progress, result and finish
        # --> progress is used in the main function to track progress (with a callback)
        # --> result is used to collect the result from main function
        # --> finish is just an empty signal to indicate that the thread is finished
        self.thread = thread_management.Thread(answers.generate_answers, self.data, self.model_path,
                                               self.use_gpu, int(self.n_ctx), self.workflow_id)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    def handle_progress(self, progress) -> None:
        value = progress[0]
        text = progress[1]
        if value is not None:
            self.progressBarSet(value)
        if text is None:
            self.textBrowser.setText("")
        else:
            self.textBrowser.insertPlainText(text)

    def handle_result(self, result):
        try:
            self.result = result
            self.Outputs.data.send(result)
        except Exception as e:
            print("An error occurred when sending out_data:", e)
            self.Outputs.data.send(None)
            return

    def handle_finish(self):
        print("Generation finished")
        self.progressBarFinished()

    def post_initialized(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWQueryLLM()
    my_widget.show()
    app.exec_()
