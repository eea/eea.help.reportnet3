---
title: "Create CSV-files"
source_url: https://help.reportnet.europa.eu/reportnet-3-1-reporter-howto/load-data/create-csv-files/
---

# Create CSV-files
Reportnet 3 supports data import using CSV files, but it requires a specific format when using the web interface. In particular, the file must be encoded in Unicode (UTF-8), which can sometimes cause confusion. This help page is designed to guide you through the correct formatting and encoding steps in case you encounter any issues.

# CSV Structure

CSV (Comma-Separated Values) files can vary widely in structure depending on how they are created and formatted. To ensure that Reportnet 3 can correctly read and import your data through the web interface, the CSV must follow a clearly defined structure. This includes the correct use of column names, data formats, and UTF-8 encoding. To help you understand what the system expects, the easiest approach is to first export a dataset from the web interface. This will give you a clear example of the required column headers, value formatting, and overall layout that your own CSV file should follow when preparing data for import.

  * **Header row** : The first row contains column names (country, year, pollutant, emissions) and must exactly match the field names defined in your Reportnet 3 data schema.
  * **Delimiter** : Values are separated by commas (,)
  * **Enclosure** : Double quotes (“) are used only for text fields
  * **Line Breaks** : Each row ends with a Windows-style line break (\r\n)
  * **Character Encoding** : The file must be saved in UTF-8 encoding (Unicode)

Some CSV generators can produce a Byte Order Mark (BOM) that provide some additional information. Reportnet is not using this function at this moment. The BOM code might be included as part of the first field name what would create a field name mismatch error. Turn this feature off in your CSV writer.

## Example CSV-File
```
country,year,pollutant,description
    "DE",2022,"NOx","Reported as ""high"" due to increased traffic"
    "FR",2022,"NOx","Stable levels"
    "IT",2022,"NOx","Slightly decreased in ""urban"" zones"
```

# Upload all tables at once using a compressed .zip file

Reportnet allows you to import one table at the time or have all tables at once using a .zip file. When you create a .zip file it’s important that all .csv-files are named exactly like the table-names in Reportnet 3. The files need to be in the root folder of the .zip file.

TIP : The easiest way to learn quickly is to perform an export inside Reportnet 3 and learn from the file returned. Use the “Export dataset data”->”ZIP (.csv for each table)”

### Example: ZIP File for Reportnet 3

Suppose your dataset schema includes the following tables:

  * country_data
  * emission_sources
  * pollutants

Your .zip file should contain **exactly one .csv file for each table** , with file names matching the table names **exactly (case-sensitive)**. Inside each .csv, the **header row must match the field names** in the corresponding table schema.
```
your_submission.zip
    ├── country_data.csv
    ├── emission_sources.csv
    └── pollutants.csv
```

## Evaluate if the CSV file(s) is encoded in UTF-8

Are you in doubt you are writing your CSV-files in UTF-8 you can do the following if you have a Windows platform. If your file contains strange characters after you imported into Reportnet 3 you can be fairly sure that something has gone wrong with your data export encoding. Your local computer might use a national character encoding schema making it look right on your side but when used on a system outside your country might look corrupted.

## Use Notepad to convert towards UTF-8

Converting a locally coded CSV file to UTF-8 encoding using Notepad is a straightforward process. This can be particularly useful if you have a CSV file that was created or saved in an encoding that does not support certain characters properly, and you need to convert it to UTF-8 for Reportnet to encode it correctly. Here’s how you can do it:

### Open the CSV File in Notepad

  * Right-click on the CSV file you wish to convert.
  * Choose “Open with” and then select “Notepad.” If Notepad is not listed, you may need to select “Choose another app” and find Notepad in the list.

### Check Current Encoding (Optional)

  * You can usually see the current encoding of the file in Notepad’s title bar next to the file name. If it’s not UTF-8, you’ll want to proceed with the conversion.

### Convert to UTF-8

  * In Notepad, with your CSV file open, click on “File” in the menu bar.
  * Select “Save As…” from the dropdown menu.
  * In the “Save As” dialog, look for the “Encoding” dropdown menu near the bottom of the window.
  * Click on the “Encoding” dropdown and select “UTF-8” from the list.
  * Choose a location to save your file, and you may rename your file if necessary. Ensure the file extension remains “.csv”.
  * Click “Save.”

### Overwrite or Rename

  * If you’re saving the file in the same location with the same name, Notepad will ask if you want to overwrite the existing file. If you choose to overwrite, the original file will be replaced with the new UTF-8 encoded version. If you’re unsure, you can save the new file with a slightly different name to preserve the original.

### Verification

  * After saving the file, you can re-open it in Notepad and check the title bar to ensure it indicates that the file is now encoded in UTF-8.
  * Optionally, you can open your CSV file in a program that displays encoding information more explicitly, such as Notepad++, to verify that the conversion was successful.

### Important Notes

  * Backup: Always make a backup of your original file before conversion. This ensures that you have a safe copy in case anything goes wrong during the conversion process.
  * Special Characters: After converting to UTF-8, it’s a good idea to check the file and ensure that all characters are displayed correctly. This is especially important if your CSV contains special characters or characters from non-Latin scripts.
