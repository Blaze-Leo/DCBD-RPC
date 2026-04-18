# %%
import subprocess
import sys
    
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# --- Login ---
def login(student_id):
    while True:
        try:
            r = requests.post(f"{BASE_URL}/login", json={"student_id": student_id})
            if r.status_code == 200:
                return r.json()["secret_key"]
            elif r.status_code == 429:
                time.sleep(0.5)
            else:
                time.sleep(0.2)
        except:
            time.sleep(0.5)

# --- Lookup ---
def get_publication_title(secret_key, filename):
    while True:
        try:
            r = requests.post(
                f"{BASE_URL}/lookup",
                json={"secret_key": secret_key, "filename": filename}
            )
            if r.status_code == 200:
                return r.json().get("title", "")
            elif r.status_code == 429:
                time.sleep(0.5)
            else:
                time.sleep(0.2)
        except:
            time.sleep(0.5)

def extract_first_word(title):
    # Remove leading/trailing spaces
    title = title.strip()
    
    # Extract first valid word (letters only)
    match = re.match(r"[A-Za-z]+", title)
    
    if match:
        return match.group(0)   # KEEP ORIGINAL CASE
    return None

# --- Mapper ---
def mapper(filename_chunk):
    from collections import Counter
    counter = Counter()

    secret_key = login(STUDENT_ID)

    for filename in filename_chunk:
        title = get_publication_title(secret_key, filename)

        if title:
            word = extract_first_word(title)
            if word:
                counter[word] += 1

    return counter

# --- Reducer ---
def reduce_counters(counters):
    total = Counter()
    for c in counters:
        total.update(c)
    return total

def verify_top_10(student_id, top_10):
    secret_key = login(student_id)

    while True:
        try:
            r = requests.post(
                f"{BASE_URL}/verify",
                json={"secret_key": secret_key, "top_10": top_10}
            )

            if r.status_code == 200:
                print(r.json())
                break
            elif r.status_code == 429:
                time.sleep(0.5)
            else:
                time.sleep(0.2)
        except:
            time.sleep(0.5)

# %%
if __name__ == "__main__":
    
    install("requests")
    install("tqdm")
    
    import requests
    import time
    from multiprocessing import Pool, cpu_count
    from collections import Counter
    import re

    BASE_URL = "http://72.60.221.150:8080"
    STUDENT_ID = "BMC202309"
    
    filenames = [f"pub_{i}.txt" for i in range(1000)]

    num_workers = min(cpu_count(), 10)
    chunk_size = len(filenames) // num_workers

    chunks = [filenames[i:i+chunk_size] for i in range(0, len(filenames), chunk_size)]

    results = []

    with Pool(num_workers) as pool:
        for res in pool.imap_unordered(mapper, chunks):
            results.append(res)

    final_counts = reduce_counters(results)
    top_10 = [w for w, _ in final_counts.most_common(10)]

    print("Top 10:", top_10)

    verify_top_10(STUDENT_ID, top_10)


