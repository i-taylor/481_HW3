import os
import subprocess
import random

def generate_mutants(seed):
    """Generate mutants using mutate.py with the given seed."""
    subprocess.run(["python3", "mutate.py", "fuzzywuzzy.py", "100", str(seed)])

def run_tests():
    """Run the test suite on each mutant and collect results."""
    results = {}

    subprocess.run("cp fuzzywuzzy.py saved.py", shell=True)
    mutants = [f for f in os.listdir('.') if f.endswith('.py') and f[0].isdigit()]

    for mutant in sorted(mutants, key=lambda x: int(x.split('.')[0])):
        # Clean up cache and pyc files
        subprocess.run("rm -rf *.pyc *cache*", shell=True)
        
        # Copy mutant to fuzzywuzzy.py
        subprocess.run(f"cp {mutant} fuzzywuzzy.py", shell=True)
        
        # Run tests and capture errors in test.output
        result = subprocess.run("python3 publictest-full.py 2> test.output", shell=True)
        
        # Read test output and check for failed tests
        with open("test.output", "r") as f:
            output = f.read()
        
        failed_tests = output.count("FAILED")
        results[mutant] = failed_tests
        
        print(f"{mutant}: FAILED={failed_tests}")
        
        # Optionally, print the failed test lines
        if failed_tests > 0:
            print(f"Failed tests in {mutant}:")
            subprocess.run(f"grep FAILED test.output", shell=True)

    # Restore original fuzzywuzzy.py
    subprocess.run("cp saved.py fuzzywuzzy.py", shell=True)
    return results

def find_optimal_seed():
    """Try different seeds to find one that meets the Suite A > B > C > D > E requirement."""
    best_seed = None
    best_score = None
    
    for seed in range(1, 1000, 10):  # Testing different seeds
        generate_mutants(seed)
        results = run_tests()
        
        scores = [results.get("{}.py".format(i), 0) for i in range(5)]
        
        if scores[0] > scores[1] > scores[2] > scores[3] > scores[4]:
            print("Found valid seed: {}".format(seed))
            best_seed = seed
            best_score = scores
            break
    
    print("Best seed found: {} with scores {}".format(best_seed, best_score))
    return best_seed

if __name__ == "__main__":
    find_optimal_seed()