import kagglehub
import os
import shutil
import glob

def setup_test_dataset():
    print("Downloading dataset from Kaggle...")
    # Download latest version
    path = kagglehub.dataset_download("hadikp/resume-data-pdf")
    print("Path to dataset files:", path)
    
    # Let's find the first PDF in the downloaded directory
    pdfs = glob.glob(os.path.join(path, "**", "*.pdf"), recursive=True)
    
    if not pdfs:
        print("No PDFs found in the downloaded dataset.")
        return
        
    print(f"Found {len(pdfs)} PDFs in dataset.")
    
    # Target directory
    target_dir = os.path.join("local_data", "input_resumes")
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy up to 3 sample resumes for testing
    count = 0
    for pdf in pdfs:
        filename = os.path.basename(pdf)
        dest_path = os.path.join(target_dir, filename)
        
        # Don't overwrite if it exists, or do, it's fine for sample
        shutil.copy2(pdf, dest_path)
        print(f"Copied {filename} to {target_dir}")
        count += 1
        if count >= 3:
            break
            
    print("\nDataset is ready! You can now test the system with these PDFs.")
    print("Example command:")
    print(f"python src/main.py --resume \"local_data/input_resumes/{os.path.basename(pdfs[0])}\" --job \"Software Engineer\"")

if __name__ == "__main__":
    setup_test_dataset()
