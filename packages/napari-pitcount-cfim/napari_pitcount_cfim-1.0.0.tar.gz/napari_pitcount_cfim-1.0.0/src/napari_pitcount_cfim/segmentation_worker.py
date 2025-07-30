import logging
import uuid

import numpy as np
from qtpy.QtCore import QThread, Signal
from qtpy.QtWidgets import QProgressBar

from napari_pitcount_cfim.cellpose_analysis.cellpose_user import CellposeUser


# Worker thread class for running Cellpose on a single image
class SegmentationWorker(QThread):
    # Signal to emit the result (mask and image name) back to the main thread
    result = Signal(object, str, uuid.UUID)  # emits (mask_array, image_name)

    def __init__(self, image_data, image_name, image_uuid, cellpose_user: CellposeUser):
        super().__init__()
        self.image_data = image_data
        self.image_name = image_name
        self.uuid = image_uuid
        self.cellpose_user = cellpose_user
        self.setObjectName(f"SegWorker-{image_name}")

    def run(self):
        """Run Cellpose segmentation on the image in a separate thread."""
        logging.debug(f"Thread {self.objectName()}: starting segmentation")
        try:
            img = np.asarray(self.image_data)

            masks_list, *_ = self.cellpose_user.process_image(img)
            mask = masks_list[0] if isinstance(masks_list, list) else masks_list
            logging.debug(f"Thread {self.objectName()}: segmentation done, emitting result")
            self.result.emit(mask, self.image_name, self.uuid)
        except Exception:
            logging.exception(f"Thread {self.objectName()}: exception during segmentation")
        finally:
            logging.debug(f"Thread {self.objectName()}: exiting run()")
