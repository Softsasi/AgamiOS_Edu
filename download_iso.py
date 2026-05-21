import os
import sys
import urllib.request
import hashlib
import time

url_list = [
    "http://mirrors.ocf.berkeley.edu/debian-cd/current-live/amd64/iso-hybrid/debian-live-13.5.0-amd64-gnome.iso",
    "https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/debian-live-13.5.0-amd64-gnome.iso",
    "http://ftp.osuosl.org/pub/debian-cd/current-live/amd64/iso-hybrid/debian-live-13.5.0-amd64-gnome.iso"
]
expected_size = 3800989696
expected_sha256 = "dd9db384f7e818d7ea8f8fa1dff2b65d73a15280664469845724369da10fccd9"
filename = "base.iso"
temp_filename = filename + ".part"

def check_sha256(filepath, expected):
    sha = hashlib.sha256()
    total_size = os.path.getsize(filepath)
    processed = 0
    last_print = time.time()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(4096 * 1024)
            if not chunk:
                break
            sha.update(chunk)
            processed += len(chunk)
            now = time.time()
            if now - last_print > 2:
                print(f"Hashing progress: {(processed * 100) // total_size}%", end='\r')
                sys.stdout.flush()
                last_print = now
    print()
    actual = sha.hexdigest()
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    return actual.lower() == expected.lower()

def main():
    print("Starting ultra-resilient multi-mirror download pipeline...")
    
    # If base.iso already exists and is correct, we are done
    if os.path.exists(filename):
        print("Checking existing base.iso...")
        if check_sha256(filename, expected_sha256):
            print("base.iso is already complete and verified!")
            sys.exit(0)
        else:
            print("Existing base.iso is corrupted or incomplete. Deleting...")
            os.remove(filename)

    url_idx = 0
    consecutive_errors = 0
    
    while True:
        # Check current size of the part file
        downloaded = 0
        if os.path.exists(temp_filename):
            downloaded = os.path.getsize(temp_filename)
            
        if downloaded >= expected_size:
            print(f"\nPart file is fully downloaded ({downloaded} bytes). Finalizing to {filename}...")
            if os.path.exists(filename):
                os.remove(filename)
            os.rename(temp_filename, filename)
            
            print("Verifying SHA256 integrity...")
            if check_sha256(filename, expected_sha256):
                print("Verification successful! base.iso is ready.")
                break
            else:
                print("Verification failed! Redownloading from scratch...")
                os.remove(filename)
                downloaded = 0
                consecutive_errors = 0
                continue

        url = url_list[url_idx % len(url_list)]
        print(f"\n--- Resuming download from {downloaded} bytes using mirror: {url} ---")
        
        headers = {}
        if downloaded > 0:
            headers['Range'] = f'bytes={downloaded}-'
            
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status_code = response.getcode()
                
                # If we requested a range but got 200 instead of 206, the server doesn't support ranges.
                # In that case, we must start from scratch for this mirror.
                if downloaded > 0 and status_code != 206:
                    print("Server does not support Range requests. Restarting download for this mirror...")
                    downloaded = 0
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    req = urllib.request.Request(url)
                    response = urllib.request.urlopen(req, timeout=30)
                
                content_len = int(response.headers.get('Content-Length', 0))
                full_size = content_len + downloaded if downloaded > 0 and status_code == 206 else content_len
                
                if full_size != expected_size and full_size > 0:
                    print(f"Warning: Server reported total size {full_size} which differs from expected {expected_size}!")
                
                mode = 'ab' if (downloaded > 0 and status_code == 206) else 'wb'
                chunk_size = 1024 * 1024 # 1MB chunks
                last_print = time.time()
                
                with open(temp_filename, mode) as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        now = time.time()
                        if now - last_print > 2:
                            percent = (downloaded * 100) // expected_size
                            print(f"Progress: {percent}% ({downloaded // (1024*1024)} MB / {expected_size // (1024*1024)} MB)", end='\r')
                            sys.stdout.flush()
                            last_print = now
                            
                print(f"\nStream ended. Downloaded size: {downloaded} bytes.")
                consecutive_errors = 0 # Reset error count on successful read
                
                if downloaded < expected_size:
                    print("Server closed connection prematurely. Rotating mirror to resume...")
                    url_idx += 1
                    time.sleep(2)
                
        except Exception as e:
            print(f"\nError occurred: {e}")
            consecutive_errors += 1
            if consecutive_errors > 20:
                print("Too many consecutive errors. Exiting.")
                sys.exit(1)
            print("Rotating mirror and retrying in 5 seconds...")
            url_idx += 1
            time.sleep(5)
            
    print("\nDownload process completed successfully!")

if __name__ == "__main__":
    main()
