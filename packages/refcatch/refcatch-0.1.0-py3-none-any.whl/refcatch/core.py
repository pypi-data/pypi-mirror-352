"""
Core functionality for RefCatch package.
"""

import re
import requests
import urllib.parse
import time
import random
import os

def get_doi_for_reference(reference_text, max_attempts=3, log=True):
    """
    Search CrossRef API for a DOI matching the reference text with multiple attempts.
    
    Args:
        reference_text (str): The reference text to search for.
        max_attempts (int): Maximum number of attempts to find the DOI.
        log (bool): Whether to log the process details.
        
    Returns:
        str or None: The DOI if found, None otherwise.
    """
    for attempt in range(max_attempts):
        try:
            # Clean up reference text and encode for URL
            clean_text = reference_text.strip()
            # Remove reference number if present
            if re.match(r'^\d+\.\t', clean_text):
                clean_text = re.sub(r'^\d+\.\t', '', clean_text)
            
            # For retry attempts, try different subsets of the text
            if attempt == 1:
                # Try with just the first part (usually authors and title)
                parts = clean_text.split('.')
                if len(parts) >= 2:
                    clean_text = parts[0] + '.' + parts[1]
            elif attempt == 2:
                # Try with just the title and journal name
                parts = clean_text.split('.')
                if len(parts) >= 3:
                    clean_text = parts[1] + '.' + parts[2]
              encoded_query = urllib.parse.quote(clean_text)
            url = f"https://api.crossref.org/works?query={encoded_query}&rows=1"
            
            if log:
                print(f"Attempt {attempt+1}/{max_attempts} - Searching for: {clean_text[:50]}...")
              # Make the API request with user-agent header
            headers = {
                'User-Agent': 'RefCatch/0.1.0 (https://github.com/AhsanKhodami/refcatch; mailto:ahsan.khodami@gmail.com)'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('message', {}).get('items', [])
                
                if items and len(items) > 0:
                    doi = items[0].get('DOI')
                    if doi:
                        if log:
                            print(f"Found DOI: {doi}")
                        return doi
            
            if log:
                print(f"No DOI found on attempt {attempt+1}")
            
            # Wait between attempts
            if attempt < max_attempts - 1:
                wait_time = 1 + random.random()  # 1-2 seconds
                time.sleep(wait_time)
        
        except Exception as e:
            if log:
                print(f"Error on attempt {attempt+1}: {str(e)}")
            
            # Wait between attempts
            if attempt < max_attempts - 1:
                time.sleep(1)
    
    if log:
        print("All attempts failed to find DOI")
    return None

def refcatch(input_file, output_file, doi_file=None, log=True):
    """
    Process references from a plaintext file and find DOIs.
    
    Args:
        input_file (str): Path to the input file containing references.
        output_file (str): Path to save the output file with DOIs.
        doi_file (str, optional): Path to save just the DOIs.
        log (bool): Whether to log progress and details.
        
    Returns:
        tuple: (success (bool), message (str), doi_count (int))
    """
    # Set default doi_file if not provided
    if doi_file is None:
        dir_name = os.path.dirname(output_file)
        base_name = os.path.splitext(os.path.basename(output_file))[0]
        doi_file = os.path.join(dir_name, f"{base_name}_dois.txt")
    
    # Clear the doi.txt file
    with open(doi_file, 'w', encoding='utf-8') as f:
        f.write("")  # Create empty file
    
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # New content with DOIs
        new_content = []
        doi_count = 0
        
        # Track current reference number for progress reporting
        current_ref = 0
        total_refs = sum(1 for line in lines if re.match(r'^\d+\.\t', line))
        
        if log:
            print(f"Found {total_refs} references in the input file")
        
        # Process each line
        for line in lines:
            # Add the original line to the new content
            new_content.append(line)
            
            # Check if this is a reference line (starts with a number and a tab)
            if re.match(r'^\d+\.\t', line):
                # Extract reference number
                ref_match = re.match(r'^(\d+)\.', line)
                if ref_match:
                    current_ref += 1
                    ref_num = ref_match.group(1)
                    
                    if log:
                        print(f"\nProcessing reference {ref_num} ({current_ref}/{total_refs})")
                    
                    # Get DOI with multiple attempts
                    doi = get_doi_for_reference(line, log=log)
                    
                    # If DOI found, add it after the reference
                    if doi:
                        doi_line = f"    DOI: {doi}\n"
                        new_content.append(doi_line)
                        doi_count += 1
                        
                        # Append to doi.txt file
                        with open(doi_file, 'a', encoding='utf-8') as f:
                            f.write(f"{doi}\n")
                    
                    # Wait to avoid rate limiting
                    time.sleep(1 + random.random())  # 1-2 seconds
        
        # Write new content to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        
        success_message = f"Done! Found {doi_count}/{total_refs} DOIs. References with DOIs written to {output_file}. DOIs also saved to {doi_file}"
        if log:
            print(f"\n{success_message}")
        
        return True, success_message, doi_count
    
    except Exception as e:
        error_message = f"Error: {str(e)}"
        if log:
            print(error_message)
            import traceback
            traceback.print_exc()
        return False, error_message, 0
