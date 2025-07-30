
from pathlib import Path

from battkit.data.dataset.table_manager import TableManager
from battkit.data.dataset.utils import infer_data_converter, extract_file_grouping, standardize_files
from battkit.data.dataset.dataset import Dataset


# Hides non-specified functions from auto-import
__all__ = [
    "Dataset", "TableManager"
    "infer_data_converter", "extract_file_grouping", "standardize_files",
]


def load_dataset(dir_dataset:Path) -> Dataset:
    """
    Loads the BattKit dataset stored at the given directory. \n
    Example: `load_dataset(Path("../BattKitDataset MyDataset"))`
    """

    dir_config = dir_dataset.joinpath("config.json")
    if not dir_dataset.exists() or not dir_config.exists():
        raise FileNotFoundError(f"No BattKit dataset exists at {dir_dataset}")
    
    name = dir_dataset.name
    dataset_name = name[name.rindex("BattKitDataset") + len("BattKitDataset") + 1: ]
    return Dataset(
        name=dataset_name,
        dir_storage=dir_dataset.parent,
        overwrite_existing=False
    )


