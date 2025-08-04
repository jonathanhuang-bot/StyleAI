import os 
import json
import tarfile
from torch.utils.data import Dataset
from PIL import Image
import io
from typing import Dict, List, Tuple, Optional

class FashionRecDataset(Dataset):
    """
    Dataset class for FashionRec recommendation tasks
    Handles Basic, Personalized, and Alternative recommendation data
    """
    def __init__(self, data_root, split= "train", task_weights=None):
        """
          Args:
              data_root: Path to backend/data
              split: "train", "valid", or "test"
              task_weights: Dict with task sampling weights
        """
        self.data_root = data_root
        self.split = split
        self.task_weights = task_weights or {
          "basic_recommendation": 0.26,
          "personalized_recommendation": 0.63,
          "alternative_recommendation": 0.11
        }
        self.samples = []
        self._build_index()
    def __len__(self):
        return len(self.samples)
    def __getitem__(self, idx):
        task, tar_path, json_name = self.samples[idx]
        with tarfile.open(tar_path, 'r') as tar:
            json_file = tar.extractfile(json_name)
            data = json.load(json_file)
            image_name = json_name.replace('.json', '.jpg')
            # Load the single corresponding image
            try:
                image_file = tar.extractfile(image_name)
                if image_file:
                    image = Image.open(io.BytesIO(image_file.read()))
                else:
                    print(f"Image file {image_name} not found in tar")
                    image = None
            except KeyError:
                print(f"Missing corresponding image: {image_name}")
                image = None
            conversation_text = ""
            conversation = data["conversation"]
            for turn in conversation:
                speaker = turn["from"]
                message = turn["value"]
                conversation_text += f"{speaker}: {message}\n"
        return {
            "images": image,                        # Single PIL Image
            "input_ids": conversation_text.strip()  # Raw conversation text
        }
    def _build_index(self):
        task_dirs = ["basic_recommendation", "personalized_recommendation", "alternative_recommendation"] 
        for task in task_dirs:
            task_path = os.path.join(self.data_root, task, self.split)
            if os.path.exists(task_path):
                tar_files = [f for f in os.listdir(task_path) if f.endswith('.tar')]
                for tar_filename in tar_files:
                    tar_path = os.path.join(task_path, tar_filename)
                    with tarfile.open(tar_path, 'r') as tar:
                        json_files = [name for name in tar.getnames() if name.endswith('.json')]
                        for json_name in json_files:
                            self.samples.append((task, tar_path, json_name))