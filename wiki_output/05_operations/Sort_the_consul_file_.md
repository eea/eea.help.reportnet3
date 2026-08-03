---
title: "Sort the consul file"
---

# Sort the consul file

This script sorts the items in a JSON file alphabetically by the "key" field.

[Edit this section](Sort_the_consul_file_/edit.md)

## Instructions:

1\. **Create the script** : Copy the following code block into a file named sort-json-by-key.sh:  

[code]
    #!/bin/bash
    
    # Check if the correct number of arguments is provided
    if [ "$#" -ne 1 ]; then
        echo "Usage: $0 <input_json_file>" 
        exit 1
    fi
    
    # Get the input file name and derive the output file name
    INPUT_FILE="$1" 
    FILENAME=$(basename "$INPUT_FILE" .json)
    OUTPUT_FILE="$FILENAME-alphabetically.json" 
    
    # Use jq to sort the array of JSON objects by the "key" field
    jq 'sort_by(.key)' "$INPUT_FILE" > "$OUTPUT_FILE" 
    
    echo "File sorted by key created: $OUTPUT_FILE" 
    
[/code]

2\. **Make the script executable** :  

[code]
    chmod +x sort-json-by-key.sh
    
[/code]

3\. **`jq` Installation** (ignore if is installed):  

[code]
    #Windows
    curl -L -o /usr/bin/jq.exe https://github.com/jqlang/jq/releases/latest/download/jq-win64.exe
    #Linux
    sudo apt-get install jq
    
[/code]

4\. **Run the script** : Place the input JSON file in the same folder and execute the script. The output file will be named `[FILENAME]-alphabetically`.json.  

[code]
    $ ls
    consulKV.json  sort-json-by-key.sh*
    
    $ ./sort-json-by-key.sh consulKV.json
    File sorted by key created: consulKV-alphabetically.json
    
    $ ls
    consulKV-alphabetically.json  consulKV.json  sort-json-by-key.sh*
    
[/code]

## Verification notes

No source code verification applicable — operational runbook; accuracy depends on current infrastructure configuration, not source code.

The script is a self-contained `bash` + `jq` utility. The Consul KV export JSON format uses a `key` field on each object, making `sort_by(.key)` the correct `jq` expression for alphabetical sorting. This is a companion tool to `Decode_consul_file.md` and is correctly described as useful when comparing two decoded Consul export files.
