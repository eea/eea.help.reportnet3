---
title: "Decode consul file"
---

# Decode consul file

This script decodes Base64-encoded values in Consul JSON files, making it easier to identify differences or spot misconfigurations.  
In case you want to compare 2 decoded files you may also need to sort the consul file. There is another bash script. 

  * [ Sort the consul file](Sort_the_consul_file_.md)



[Edit this section](Decode_consul_file/edit.md)

## Instructions:

1\. **Create the script** : Copy the following code block into a file named `decode-consul.sh`:
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
    OUTPUT_FILE="$FILENAME-decoded.json" 
    
    # Use jq to parse and decode base64 values, then write to the new file
    jq 'map(
        if .value then
            .value |= @base64d
        else
            .
        end
    )' "$INPUT_FILE" > "$OUTPUT_FILE" 
    
    echo "Decoded file created: $OUTPUT_FILE" 
    
    
[/code]

2\. **Make the script executable** :  

[code]
    chmod +x decode-consul.sh
    
[/code]

3\. **`jq` Installation**:  

[code]
    #Windows
    curl -L -o /usr/bin/jq.exe https://github.com/jqlang/jq/releases/latest/download/jq-win64.exe
    #Linux
    sudo apt-get install jq
    
[/code]

4\. **Run the script** : Place the input JSON file in the same folder and execute the script. The output file will be named `[FILENAME]-decoded.json`.  

[code]
    $ ls
    consulKV.json  decode-consul.sh*
    
    $ ./decode-consul.sh consulKV.json
    Decoded file created: consulKV-decoded.json
    
    $ ls
    consulKV-decoded.json  consulKV.json  decode-consul.sh*
    
[/code]

## Verification notes

No source code verification applicable — operational runbook; accuracy depends on current infrastructure configuration, not source code.

The script itself is a self-contained `bash` + `jq` utility. Consul stores its Key/Value data as Base64-encoded values in its JSON export format, so the `@base64d` decode step is correct. The approach is consistent with the Consul usage described in `Operation_guidelines.md`, where all service configuration lives in the `config/` hierarchy of Consul KV. The `jq` dependency installation instructions are correct for Debian/Ubuntu Linux and Windows.
