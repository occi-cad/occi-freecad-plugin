import time
from PySide import QtCore
import requests

class Worker(QtCore.QThread):
    """
    Threaded worker for handling long-running model generation.
    """

    job_url = ""  # The URL of the job to watch for completion
    model_url = ""  # The URL to pass to the slot when the processing is done

    #This is the signal that will be emitted during the processing.
    updateProgress = QtCore.Signal(int)
    modelReady = QtCore.Signal(str)
    modelTimedOut = QtCore.Signal()

    def __init__(self):
        from PySide import QtCore
        QtCore.QThread.__init__(self)

    def run(self):
        """
        Starts this thread so that it can poll the job URL and pass the model URL
        back to the UI when it is ready.
        """

        # Poll the job URL until the model is finished and ready for download
        i = 0
        while True:
            i += 1

            # Poll the job URL
            response = requests.get(self.job_url, allow_redirects=False)
            if response.status_code == 200:
                # Let the caller know that we are done
                self.modelReady.emit(self.model_url)
                break
            elif response.status_code == 202:
                # Clamp the status update to 100%
                if i > 100:
                    status = 100
                else:
                    status = i

                # Let the UI know about progress any progress being made
                self.updateProgress.emit(status)
            else:
                print("Unknown status code: " + str(response.status_code))

            # Trap door to keep execution from going on forever
            # Capped at 10 minutes
            if i >= 120:
                self.modelTimedOut.emit()
                break

            time.sleep(5.0)
