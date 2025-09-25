import subprocess

MMDC_PATH = r"C:\Users\PhanindraDharmavarap\AppData\Roaming\npm\\mmdc.cmd"

def validate_mermaid_code(code: str) -> tuple[bool, str]:
    try:
        with open("temp.mmd", "w", encoding="utf-8") as f:
            f.write(code)
        result = subprocess.run(
            [MMDC_PATH, "-i", "temp.mmd", "-o", "temp.svg"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)