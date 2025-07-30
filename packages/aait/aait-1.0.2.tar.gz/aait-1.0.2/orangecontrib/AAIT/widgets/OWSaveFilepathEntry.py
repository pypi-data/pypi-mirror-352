import os
from Orange.data.table import Table
from Orange.widgets import gui, widget
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import Input

import pickle



class OWSaveFilepathEntry(widget.OWWidget):
    name = "Save with Filepath Entry"
    description = "Save data to a .pkl file, based on the provided path"
    icon = "icons/owsavefilepathentry.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owsavefilepathentry.svg"
    priority = 1220
    want_main_area = False
    resizing_enabled = False

    # Persistent settings for fileId and CSV delimiter
    filename: str = Setting("embeddings.pkl") # type: ignore

    class Inputs:
        data = Input("Data", Table)
        save_path = Input("Path", str)
        path_table = Input("Path Table", Table)


    @Inputs.data
    def dataset(self, data): 
        """Handle new data input."""
        self.data = data
        if self.data is not None:
            self.run()

    @Inputs.save_path
    def set_save_path(self, in_save_path):
        if in_save_path is not None:
            self.save_path = in_save_path
            self.run()

    @Inputs.path_table
    def set_path_table(self, in_path_table):
        if in_path_table is not None:
            if "path" in in_path_table.domain:
                self.save_path = in_path_table[0]["path"].value
                self.run()


    def __init__(self):
        super().__init__()
        self.info_label = gui.label(self.controlArea, self, "Initial info.")

        # Data Management
        self.save_path = None
        self.data = None
        self.setup_ui()


    def setup_ui(self):
        """Set up the user interface."""
        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)

    def run(self):
        """Save data to a file."""
        if self.data is None:
            return

        if self.save_path is None:
            return

        if os.path.isdir(self.save_path):
            self.save_path = os.path.join(self.save_path, self.filename)

        if len(self.save_path)>4:
            if self.save_path[-3:]!="pkl":
                import Orange.widgets.data.owsave as save_py

                saver = save_py.OWSave()
                saver.data = self.data
                saver.filename = self.save_path
                saver.add_type_annotations=True
                saver.do_save()
                return

        # add jcmhkh
        with open(self.save_path, "wb") as f:
            print("warning hard save pikle!")
            pickle.dump(self.data, f)

        self.data = None
        self.save_path = None



if __name__ == "__main__": 
    WidgetPreview(OWSaveFilepathEntry).run()
