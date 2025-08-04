import os
import tarfile
import io
from PIL import Image
import torch
from torch.utils.data import Dataset


class FashionImageGenerationDataset(Dataset):
    """
    Dataset for Fashion Image Generation (T2I stream in FashionM3)
    
    Loads fashion product images with their text descriptions from tar files.
    Used for training the LT2I (text-to-image) loss component.
    
    Data format:
    - fashion_image_generation/000.tar, 001.tar, etc.
    - Each tar contains: 0000000.jpg + 0000000.txt pairs
    - Text files contain detailed product descriptions
    """
    
    def __init__(self, data_root, split="train"):
        """
        Args:
            data_root (str): Path to fashion_image_generation directory
            split (str): Currently only supports "train" 
        """
        self.data_root = data_root
        self.split = split
        self.samples = []
        
        # Load all samples from tar files
        self._load_samples()
        
        print(f"FashionImageGenerationDataset loaded {len(self.samples)} samples")
    
    def _load_samples(self):
        """Load all image-text pairs from tar files"""
        
        # Get all tar files in the directory
        tar_files = []
        split_path = os.path.join(self.data_root, self.split)
        for filename in os.listdir(split_path):
            if filename.endswith('.tar'):
                tar_path = os.path.join(self.data_root, filename)
                tar_files.append(tar_path)
        
        tar_files.sort()  # Ensure consistent ordering
        print(f"Found {len(tar_files)} tar files in {self.data_root}")
        
        # Extract all samples from each tar file
        for tar_path in tar_files:
            try:
                with tarfile.open(tar_path, 'r') as tar:
                    # Get all txt files (they define our samples)
                    txt_files = [name for name in tar.getnames() if name.endswith('.txt')]
                    
                    for txt_name in txt_files:
                        # Corresponding image file
                        img_name = txt_name.replace('.txt', '.jpg')
                        
                        # Verify both files exist in tar
                        if img_name in tar.getnames():
                            self.samples.append((tar_path, img_name, txt_name))
                        else:
                            print(f"Missing image for {txt_name} in {tar_path}")
                            
            except Exception as e:
                print(f"Error reading {tar_path}: {e}")
        
        print(f"Total samples loaded: {len(self.samples)}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """
        Returns a sample for T2I training
        
        Returns:
            dict: {
                "images": PIL Image of fashion product,
                "input_ids": str description of the product
            }
        """
        tar_path, img_name, txt_name = self.samples[idx]
        
        # Load from tar file
        with tarfile.open(tar_path, 'r') as tar:
            # Load text description
            try:
                txt_file = tar.extractfile(txt_name)
                if txt_file:
                    description = txt_file.read().decode('utf-8').strip()
                else:
                    print(f"Could not extract text: {txt_name}")
                    description = "A fashion item."
            except Exception as e:
                print(f"Error reading text {txt_name}: {e}")
                description = "A fashion item."
            
            # Load image
            try:
                img_file = tar.extractfile(img_name)
                if img_file:
                    image = Image.open(io.BytesIO(img_file.read()))
                    # Convert to RGB if necessary
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                else:
                    print(f"Could not extract image: {img_name}")
                    # Create a placeholder image if loading fails
                    image = Image.new('RGB', (512, 512), color='white')
            except Exception as e:
                print(f"Error reading image {img_name}: {e}")
                # Create a placeholder image if loading fails
                image = Image.new('RGB', (512, 512), color='white')
        
        return {
            "images": image,        # PIL Image for MAGVIT-v2 processing
            "input_ids": description  # Text description for T2I generation
        }


def test_fashion_image_generation_dataset():
    """Test function to verify the dataset works correctly"""
    
    data_root = "/mnt/c/Users/jonat/desktop/styleai/backend/data/fashion_image_generation"
    
    print("🧪 Testing FashionImageGenerationDataset...")
    
    # Create dataset
    dataset = FashionImageGenerationDataset(data_root=data_root)
    
    print(f"📊 Dataset size: {len(dataset)}")
    
    # Test first few samples
    for i in range(min(3, len(dataset))):
        sample = dataset[i]
        print(f"\n📝 Sample {i}:")
        print(f"   Image type: {type(sample['images'])}")
        print(f"   Image size: {sample['images'].size}")
        print(f"   Image mode: {sample['images'].mode}")
        print(f"   Description: {sample['input_ids'][:100]}...")
    
    print("\nFashionImageGenerationDataset test completed!")


if __name__ == "__main__":
    test_fashion_image_generation_dataset()