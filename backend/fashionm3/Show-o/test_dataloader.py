import sys
import os
sys.path.append(".")

from fashionrec_dataset import FashionRecDataset

def test_dataset_creation():
    dataset = FashionRecDataset(data_root = "/mnt/c/Users/jonat/desktop/styleai/backend/data")
    print("length of dataset: ", dataset.__len__())

def test_sample_loading():
    dataset = FashionRecDataset(data_root="/mnt/c/Users/jonat/desktop/styleai/backend/data")
    sample = dataset[0]  # Load first sample
    print("✅ Sample loaded successfully!")
    print(f"📝 Task type: {sample['task_type']}")
    print(f"🖼️  Number of images: {len(sample['images'])}")
    print(f"💬 Conversation length: {len(sample['conversation'])} characters")

def test_all_tasks():
    dataset = FashionRecDataset(data_root="/mnt/c/Users/jonat/desktop/styleai/backend/data")
    import random
    sample_size = 100
    random_indices = random.sample(range(len(dataset)), min(sample_size, len(dataset)))
    task_counts = {}
    for idx in random_indices:
        sample = dataset[idx]
        task = sample["task_type"]
        task_counts[task] = task_counts.get(task, 0) + 1
    print(f"📊 Task distribution from {sample_size} samples:")
    for task, count in task_counts.items():
        percentage = (count / sample_size) * 100
        print(f"   {task}: {count}/{sample_size} ({percentage:.1f}%)")

    # Check if distribution is reasonable
    expected = {"basic_recommendation": 26, "personalized_recommendation": 63, "alternative_recommendation": 11}
    print("🎯 Expected vs Actual:")
    for task, expected_pct in expected.items():
        actual_pct = (task_counts.get(task, 0) / sample_size) * 100
        diff = abs(actual_pct - expected_pct)
        status = "✅" if diff < 10 else "⚠️"  # 10% tolerance
        print(f"{task}: Expected {expected_pct}%, Got {actual_pct:.1f}%{status}")
def check_alternative_samples():
    dataset = FashionRecDataset(data_root="/mnt/c/Users/jonat/desktop/styleai/backend/data")

    # Check first 1000 samples for task types
    alt_count = 0
    for i in range(min(1000, len(dataset))):
        if dataset.samples[i][0] == "alternative_recommendation":
            alt_count += 1

    print(f"Alternative samples in first 1000: {alt_count}")

    # Try to load one alternative sample if it exists
    if alt_count > 0:
        for i in range(min(1000, len(dataset))):
            if dataset.samples[i][0] == "alternative_recommendation":
                try:
                    sample = dataset[i]
                    print(f"✅ Alternative sample loaded successfully!")
                    break
                except Exception as e:
                    print(f"❌ Alternative sample failed: {e}")
                    break

def debug_tar_contents():
    """Let's see what's actually in the tar files"""
    import tarfile
    tar_path = "/mnt/c/Users/jonat/desktop/styleai/backend/data/basic_recommendation/train/000.tar"

    with tarfile.open(tar_path, 'r') as tar:
        print("🔍 Contents of first tar file:")
        all_files = tar.getnames()[:20]  # First 20 files
        for filename in all_files:
            print(f"  📄 {filename}")

        print(f"\n📊 Total files in tar: {len(tar.getnames())}")
        json_files = [f for f in tar.getnames() if f.endswith('.json')]
        img_files = [f for f in tar.getnames() if f.endswith(('.jpg', '.png'))]
        print(f"📄 JSON files: {len(json_files)}")
        print(f"🖼️ Image files: {len(img_files)}")


def debug_json_structure():
    """Let's see what JSON files actually contain"""
    import tarfile, json
    tar_path = "/mnt/c/Users/jonat/desktop/styleai/backend/data/basic_recommendation/train/000.tar"

    with tarfile.open(tar_path, 'r') as tar:
        json_files = [f for f in tar.getnames() if f.endswith('.json')][:3]

        for json_name in json_files:
            print(f"\n🔍 Structure of {json_name}:")
            json_file = tar.extractfile(json_name)
            data = json.load(json_file)
            print(f"  Keys: {list(data.keys())}")
              # Print first few lines of the actual JSON
            json_file = tar.extractfile(json_name)
            content = json_file.read().decode('utf-8')[:500]
            print(f"  Content preview: {content}...")

def analyze_dataset_structure():
    dataset = FashionRecDataset(data_root="/mnt/c/Users/jonat/desktop/styleai/backend/data")

    print(f"📊 Total samples: {len(dataset)}")

    # Check task distribution across different ranges
    ranges = [
        (0, 1000, "First 1000"),
        (len(dataset)//2, len(dataset)//2 + 1000, "Middle 1000"),
        (len(dataset)-1000, len(dataset), "Last 1000")
    ]

    for start, end, name in ranges:
        task_counts = {}
        for i in range(start, min(end, len(dataset))):
            task = dataset.samples[i][0]
            task_counts[task] = task_counts.get(task, 0) + 1

        print(f"\n{name} samples:")
        for task, count in task_counts.items():
            print(f"  {task}: {count}")

def count_alternative_files():
    import os
    alt_path = "/mnt/c/Users/jonat/desktop/styleai/backend/data/alternative_recommendation/train"

    if os.path.exists(alt_path):
        tar_files = [f for f in os.listdir(alt_path) if f.endswith('.tar')]
        print(f"Alternative recommendation tar files: {len(tar_files)}")
        print(f"Files: {tar_files}")
    else:
        print("Alternative recommendation folder not found!")

def get_full_dataset_distribution():
    dataset = FashionRecDataset(data_root="/mnt/c/Users/jonat/desktop/styleai/backend/data")

    print(f"📊 Analyzing all {len(dataset)} samples...")

    # Count all task types
    task_counts = {}
    for i in range(len(dataset)):
        task = dataset.samples[i][0]  # Get task type from index
        task_counts[task] = task_counts.get(task, 0) + 1

        # Progress indicator
        if (i + 1) % 50000 == 0:
            print(f"  Processed {i + 1:,} samples...")

    print(f"\n🎯 Full Dataset Distribution:")
    total = sum(task_counts.values())
    for task, count in task_counts.items():
        percentage = (count / total) * 100
        print(f"  {task}: {count:,} ({percentage:.1f}%)")

    print(f"\n📋 Expected vs Actual:")
    expected = {
        "basic_recommendation": 86776,
        "personalized_recommendation": 208599,
        "alternative_recommendation": 8559
    }

    for task, expected_count in expected.items():
        actual_count = task_counts.get(task, 0)
        print(f"  {task}:")
        print(f"    Expected: {expected_count:,}")
        print(f"    Actual: {actual_count:,}")
        print(f"    Difference: {actual_count - expected_count:,}")

if __name__ == "__main__":
    print("🚀 Testing FashionRec Dataloader")
    #debug_tar_contents()
    #debug_json_structure()
    #test_sample_loading()
    #check_alternative_samples()
    #analyze_dataset_structure()
    #count_alternative_files()
    get_full_dataset_distribution()
    #test_all_tasks()
    print("✅ All tests complete!")