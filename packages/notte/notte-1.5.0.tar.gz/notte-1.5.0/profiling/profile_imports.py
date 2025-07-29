from pathlib import Path
import time
import cProfile
import pstats
import importlib
import subprocess
import sys


DIR_PATH = Path(__file__).parent / "imports"
DIR_PATH.mkdir(parents=True, exist_ok=True)

def measure_import_time(module_name: str) -> float:
    """Measure the time it takes to import a module."""
    start_time = time.perf_counter()
    _ = importlib.import_module(module_name)
    end_time = time.perf_counter()
    return end_time - start_time

def measure_import_time_subprocess(module_name: str) -> float:
    code = (
        "import time, importlib; "
        "start = time.perf_counter(); "
        f"importlib.import_module('{module_name}'); "
        "end = time.perf_counter(); "
        "print(end - start)"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    print(f"Import time for {module_name} (subprocess): {result.stdout}")
    return float(result.stdout.strip())

def profile_import(module_name: str, output_file: str) -> None:
    """Profile the import of a module using cProfile."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Import the module
    import notte
    
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.dump_stats(output_file)
    print(f"Profile data saved to {output_file}")

def profile_import_subprocess(module_name: str, output_file: str) -> None:
    """Profile the import of a module using cProfile in a subprocess for cold import."""
    code = (
        "import cProfile, importlib, pstats; "
        f"profiler = cProfile.Profile(); "
        "profiler.enable(); "
        f"importlib.import_module('{module_name}'); "
        "profiler.disable(); "
        f"profiler.dump_stats(r'{output_file}')"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    if result.stderr:
        print(f"Error profiling {module_name}: {result.stderr}")
    else:
        print(f"Profile data saved to {output_file}")

def main() -> None:
    # Profile notte-sdk
    # packages = [
    #    "notte_core",
    #    "notte_browser",
    #    "notte_agent",
    #    "notte_sdk",
    # ]
    # for package in packages:
    #     print(f"Profiling {package}...")
    
    #     # Simple timing
    #     import_time = measure_import_time_subprocess(package)
    #     print(f"\nImport time for {package}: {import_time:.3f} seconds")
        
    #     # Detailed profiling
    #     print("\nDetailed import profile:")
    #     profile_import_subprocess(package, f"{DIR_PATH}/{package}.prof")
    profile_import("notte", f"{DIR_PATH}/notte.prof")

if __name__ == "__main__":
    main()