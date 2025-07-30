#!/usr/bin/env python3
"""
Test script to run Cellpose segmentation on a TIFF file and visualize results in Napari.

Modify `TIFF_PATH` below to point to your .tiff file.
"""
import cellpose.models
import napari
import numpy as np
from cellpose import models
from cellpose.utils import remove_edge_masks
from cellpose.dynamics import remove_bad_flow_masks
import tifffile
import importlib.resources as pkg_resources

"""
/Lib/site-packages/cellpose/models.py:38
normalize params = {
    "lowhigh": None,
    "percentile": None,
    "normalize": True,
    "norm3D": True,
    "sharpen_radius": 0,
    "smooth_radius": 0,
    "tile_norm_blocksize": 0,
    "tile_norm_smooth3D": 1,
    "invert": False
}
"""

class CellposeUser:
    def __init__(self, cellpose_settings = None):
        """
        Initialize the CellposeUser class.

        Parameters:
            cellpose_settings: Optional settings for Cellpose.
        """
        if cellpose_settings:
            self.cellpose_settings = cellpose_settings
        else:
            self.cellpose_settings = {
                "diameter": None,
                "border_filter": True,
                "model_type": "cyto3",
                "gpu": False,
                "sharpen_radius": 0,
            }
        self.normalize_params = {
            "lowhigh": None,
            "percentile": None,
            "normalize": True,
            "norm3D": True,
            "sharpen_radius": self.cellpose_settings["sharpen_radius"],
            "smooth_radius": 0,
            "tile_norm_blocksize": 0,
            "tile_norm_smooth3D": 1,
            "invert": False
        }

        try:
            self.model = models.Cellpose(
                gpu=self.cellpose_settings["gpu"],
                model_type=self.cellpose_settings["model_type"],
                nchan=2
            )
        except KeyError as e:
            raise ValueError(f"Invalid cellpose settings: {e}")


    def run_on_tiff(self, tiff_path: str, output_dir: str = 'cell_crops'):
        """
            Run processing on a TIFF file.
        """
        img = tifffile.imread(tiff_path)
        return self.process_image(img, output_dir)

    def process_image(self, img: np.ndarray):
        """
        Run Cellpose segmentation on a numpy array

        Parameters:
            img: np.ndarray
            output_dir: directory to save individual cell crops
        """

        masks_list, flows, styles, diameters = self.model.eval(
            [img],
            channels=[0, 0],
            resample=True,
            normalize=self.normalize_params,
            invert=False,
            diameter=self.cellpose_settings["diameter"],
            flow_threshold=0.4,
            cellprob_threshold=0.0,
            augment=False,
            min_size=30,


        )
        masks = np.array(masks_list[0])

        if self.cellpose_settings["border_filter"]:
            masks = remove_edge_masks(masks)

        # masks = remove_bad_flow_masks(masks, flows[0][1])

        return masks, flows[0], styles, diameters

    def estimate_size(self, img: np.ndarray):
        """
        Estimate the size of the objects in the image.

        Parameters:
            img: np.ndarray
        """

        if self.cellpose_settings.get("diameter", 0) > 0:
            return self.cellpose_settings["diameter"]
        size_model = self.model.sz
        diameter = size_model.eval(img, [0, 0], normalize=self.normalize_params)

        return diameter[0]


# if __name__ == '__main__':
#     import sys
#     from qtpy.QtWidgets import QApplication, QProgressBar, QWidget, QVBoxLayout
#     pkg_root = pkg_resources.files("src")
#     TIFF_PATH = pkg_root / "resources"/"test_files" / "P06 1-Tile-16-1-channel.tiff"
#
#     app = QApplication(sys.argv)
#
#     # Create a simple window with a QProgressBar
#
#     progress_bar = QProgressBar()
#     progress_bar.setMinimum(0)
#     progress_bar.setMaximum(100)
#     progress_bar.setValue(0)
#
#     viewer = napari.Viewer(ndisplay=2, show=True)
#     viewer.window.add_dock_widget(progress_bar, area="bottom", name="Cellpose Progress")
#     viewer.show()
#     cellpose_user = CellposeUser()
#     cellpose_user.attach_progress_bar(progress_bar)
#     masks, flows, styles, diams = cellpose_user.run_on_tiff(str(TIFF_PATH))
#     print(f"[*] Cellpose segmentation complete. Found {len(np.unique(masks))} unique masks.")
#
#     viewer.add_labels(masks[0], name='Cell Masks')
#
#     viewer.add_image(flows[0][0], name='Flow X')
#     viewer.add_image(flows[0][1], name='Flow Y')
#     viewer.add_image(flows[0][2], name='Cell Probability')
#
#     napari.run()



