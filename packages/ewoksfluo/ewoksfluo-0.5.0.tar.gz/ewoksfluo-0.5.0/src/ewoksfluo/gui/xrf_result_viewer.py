from PyMca5.PyMcaGui.pymca.RGBCorrelator import RGBCorrelator


class XrfResultViewer(RGBCorrelator):
    def removeAllImages(self):
        for label in list(self._imageList):
            self.removeImage(label)
