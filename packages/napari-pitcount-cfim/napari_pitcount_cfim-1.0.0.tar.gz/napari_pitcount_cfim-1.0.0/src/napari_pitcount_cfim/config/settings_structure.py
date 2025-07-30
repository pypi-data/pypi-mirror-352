import os
from typing import Optional

from pydantic import BaseModel, Field

def get_default_output_folder() -> str:
    base = os.getenv('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    return os.path.join(base, "napari-pitcount-cfim", "output")

def get_default_input_folder() -> str:
    base = os.getenv('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    return os.path.join(base, "napari-pitcount-cfim", "input")

def get_default_model_folder() -> str:
    base = os.getenv('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    return os.path.join(base, "napari-pitcount-cfim", "model")

class DebugSettings(BaseModel):
    """
    Settings for debugging.
    """
    debug: bool = Field(default=False)
    verbosity_level: int = Field(default=1)

class AutomationSettings(BaseModel):
    """
        Settings specifying what steps to run automatically.
    """
    folder_prompt: bool = Field(default=True, description="Prompt for folder selection.")

class FileSettings(BaseModel):
    """
        Settings for file handling.
    """
    input_folder: str = Field(default_factory=get_default_input_folder, description="Folder containing the input files.")
    output_folder: str = Field(default_factory=get_default_output_folder, description="Folder to save the output files.")

    # Attempted virtual fields
    debug: Optional[bool] = Field(default=None, exclude=True)
    folder_prompt: Optional[bool] = Field(default=None, exclude=True)
    family_grouping: str = Field(default="default", description="Strategy for grouping results. Options: 'default', 'file', 'folder', 'all'.")


class CellposeSettings(BaseModel):
    """
    Settings for the Cellpose segmentation.
    """
    diameter: Optional[float] = Field(default=None
                            , description="Diameter of the cells in pixels. If None, Cellpose will estimate it.")
    border_filter: bool = Field(default=True)
    model_type: str = Field(default="cyto3")
    gpu: bool = Field(default=False)
    sharpen_radius: int = Field(default=0)

    # Attempted virtual fields
    debug: Optional[bool] = Field(default=None, exclude=True)

class ModelSettings(BaseModel):
    """
    Settings for analysis model.
    """
    model: str = Field(default="unused", description="Model name. (unused)")
    model_folder: str = Field(default="none", description="Path to the folder containing a model.joblib and transformer.joblib file.")
    mask_color: str = Field(default="Blue", description="Color for the mask overlay. Color name or RGBA tuple. (e.g. 'Blue' or (0, 0, 255, 128))")


class CFIMSettings(BaseModel):
    """
        Settings for the napari pitcount CFIM plugin.

        Update the version number here after a change.
    """
    __version__: str = "1.0.0"

    version: str = Field(default=__version__)
    automation_settings: AutomationSettings = AutomationSettings()
    file_settings: FileSettings = FileSettings()
    cellpose_settings: CellposeSettings = CellposeSettings()
    model_settings: ModelSettings = ModelSettings()
    debug_settings: DebugSettings = DebugSettings()


    def as_dict_with_virtuals(self) -> dict:
        d = self.model_dump()
        d["file_settings"]["debug"] = self.debug_settings.debug
        d["cellpose_settings"]["debug"] = self.debug_settings.debug
        d["model_settings"]["debug"] = self.debug_settings.debug
        d["file_settings"]["folder_prompt"] = self.automation_settings.folder_prompt
        return d
