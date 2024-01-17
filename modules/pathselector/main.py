from PyQt5.QtWidgets import QFileDialog, QMessageBox
from calamares import ViewStep, job

class PathSelectorViewStep(ViewStep):
    def __init__(self):
        super().__init__()

    def onEnter(self):
        # This method is called when the module is entered in the installer
        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        if path:
            if self.isPathWritable(path):
                job.setGlobalStorage("selectedPath", path)
            else:
                QMessageBox.warning(None, "Warning", "The selected path is not writable. Please choose another directory.")
                # You might want to bring up the dialog again or handle this differently

    def isPathWritable(self, path):
        # Check if the path is writable
        try:
            testfile = os.path.join(path, "testfile")
            with open(testfile, 'w') as file:
                file.write("test")
            os.remove(testfile)
            return True
        except IOError:
            return False
