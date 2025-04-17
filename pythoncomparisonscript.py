import re
import hashlib
import json

# Function to extract keywords and logic blocks (with return patterns)
def extract_keywords_and_logic(code, keywords):
    # Keyword matching pattern (find keywords and their variations)
    keyword_matches = []
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\w*\b', code):  # Match keyword variations
            keyword_matches.append(keyword)

    # Function-like matching (including arrow functions, regular functions, and blocks with return logic)
    function_re = r'(function\s+[A-Za-z_]\w*\s*\([^\)]*\)\s*\{[^}]*\})'
    arrow_re = r'([A-Za-z_]\w*\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\})'
    block_re = r'[^\n]*\b(return\s+(?:null|undefined|void)[^}]*\})'  # Matches return null or undefined

    blocks = []
    blocks.extend(re.findall(function_re, code, re.DOTALL))
    blocks.extend(re.findall(arrow_re, code, re.DOTALL))
    blocks.extend(re.findall(block_re, code, re.DOTALL))

    return keyword_matches, blocks

# Function to normalize function and return logic (for matching similar flow)
def normalize_logic_blocks(code):
    # Normalize function bodies to focus on structural elements rather than variable names
    code = re.sub(r'([A-Za-z_]\w*)', 'ID', code)  # Replace identifiers with 'ID'
    code = re.sub(r'(null|undefined|void)', 'RETURN', code)  # Normalize return values
    return code

# Generate a hash for a code block (for comparing logic across different files)
def generate_code_hash(code):
    return hashlib.md5(code.encode('utf-8')).hexdigest()

# Function to compare logic blocks between two groups of files
def compare_logic_blocks(groupA_files, groupB_files, keywords):
    comparison_results = {}
    
    # Loop through all files in both groups
    for group_name, files in {'Group A': groupA_files, 'Group B': groupB_files}.items():
        comparison_results[group_name] = {}
        
        for file_name, path in files.items():
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # Extract keywords and logic blocks
            keyword_matches, logic_blocks = extract_keywords_and_logic(code, keywords)
            
            # Normalize and hash logic blocks
            normalized_blocks = [normalize_logic_blocks(block) for block in logic_blocks]
            logic_hashes = {}
            for orig, norm in zip(logic_blocks, normalized_blocks):
                logic_hashes[orig] = generate_code_hash(norm)

            comparison_results[group_name][file_name] = {
                'Keyword Matches': keyword_matches,
                'Logic Blocks': logic_blocks,
                'Normalized Logic Hashes': logic_hashes
            }
    
    return comparison_results

# Define the file paths
group_A_files = {
    'Line wrap.txt': 'C:..../......../Line wrap.txt',
    'var t=t={var e;consttxt.txt': 'C:..../................/var t=t={var e;consttxt.txt'
}
group_B_files = {
    'initLogsExt.js': 'C:..../................/order_in_total_fucking_chaos/initLogsExt.js',
    'initlogs549359chars.txt': 'C:..../................/order_in_total_fucking_chaos/initlogs549359chars.txt'
}

# Define the list of keywords to search for in the code
keywords = [
    'toast', 'toaster', 'toaststack',  # Toast-related keywords
    'intercept', 'interception', 'interceptor',  # Intercept-related
    'log', 'logged', 'logger', 'logs', 'logger',  # Logging-related
    'panel', 'panel-', 'panels', 'log-panel'  # Panel-related
]

# Run the comparison
comparison_results = compare_logic_blocks(group_A_files, group_B_files, keywords)

# Output the results in a more structured and readable format
for group, files in comparison_results.items():
    print(f"Results for {group}:")
    for file_name, result in files.items():
        print(f"\nFile: {file_name}")
        print(f"  Keywords found: {', '.join(result['Keyword Matches'])}")
        print(f"  Matching Logic Blocks:")
        for idx, block in enumerate(result['Logic Blocks']):
            print(f"    Block {idx + 1} (Hash: {result['Normalized Logic Hashes'][block]}):")
            print(f"      {block[:100]}...")  # Show the first 100 characters of each matching block
        print("\n")
