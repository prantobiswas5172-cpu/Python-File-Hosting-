import os

# Placeholder malware signatures (dangerous python commands)
DANGEROUS_SIGNATURES = [
    b"os.system('rm -rf",
    b"subprocess.Popen(['rm', '-rf'",
    b"eval(compile(",
    b"__import__('os').system",
    b"os.execl",
    b"pty.spawn('/bin/sh')"
]

def scan_file_for_malware(filepath: str) -> bool:
    """
    Scans a file against known dangerous signatures.
    Returns True if the file is SAFE, False if MALWARE detected.
    """
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            for signature in DANGEROUS_SIGNATURES:
                if signature in content:
                    return False
        return True
    except Exception:
        # If we can't read it, it's safer to flag it
        return False