import time
from PySide import QtCore

class Worker(QtCore.QThread):
    """
    Threaded worker for handling long-running model generation.
    """

    check_url = ""

    #This is the signal that will be emitted during the processing.
    updateProgress = QtCore.Signal(int)
    modelReady = QtCore.Signal()

    def __init__(self):
        from PySide import QtCore
        QtCore.QThread.__init__(self)

    def run(self):
        """
        Starts this thread.
        """

        #Notice this is the same thing you were doing in your progress() function
        for i in range(1, 5):  #101):
            print("Progress: " + str(i))
            #Emit the signal so it can be received on the UI side.
            self.updateProgress.emit(i)
            time.sleep(0.5)

        # Let the caller know that we are done
        self.modelReady.emit()
