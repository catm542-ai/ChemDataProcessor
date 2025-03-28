import re 
import pandas as pd
import numpy as np
# from PIL import Image   # Image generation removed

# Read the Excel file without assuming headers
excel_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE3_octal_script3\code3_octal_FIA\code2.xlsx'
df_excel = pd.read_excel(excel_path, sheet_name=0, header=None)

# Search for the cell containing "Compound" (case- and whitespace-insensitive)
compound_position = None
for i in range(df_excel.shape[0]):
    for j in range(df_excel.shape[1]):
        val = str(df_excel.iat[i, j]).strip()
        if "compound" in val.lower():
            compound_position = (i, j)
            break
    if compound_position:
        break

if compound_position is not None:
    row_compound, col_compound = compound_position
    compounds = []
    for row in range(row_compound + 1, df_excel.shape[0]):
        cell = df_excel.iat[row, col_compound]
        # Stop if the cell is empty or NaN
        if pd.isna(cell) or str(cell).strip() == "":
            break
        compounds.append(str(cell).strip())
    print("Compounds found:", compounds)
else:
    print("The word 'Compound' was not found in the Excel sheet.")
    compounds = []

compound_names = compounds

# Read the full content of the text file
text_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE3_octal_script3\code3_octal_FIA\decoded_output.txt'
with open(text_path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

def extract_compound_block(compound, lines):
    """
    Searches for the section starting with 'Compound n: <compound>'
    and returns the lines until the next 'Compound n:' appears.
    """
    pattern = re.compile(r'Compound\s+\d+:\s+' + re.escape(compound), re.IGNORECASE)
    start_index = None
    for i, line in enumerate(lines):
        if pattern.search(line):
            start_index = i
            break
    if start_index is None:
        return []
    block = []
    for j in range(start_index + 1, len(lines)):
        if re.search(r'Compound\s+\d+:\s+', lines[j], re.IGNORECASE):
            break
        block.append(lines[j].strip())
    return block

def extract_octal_area(block_lines):
    """
    Searches for the line containing 'octal_UPLC' and extracts the last value (concentration).
    Returns 0.0 if the value cannot be converted to float.
    """
    area = 0.0
    for line in block_lines:
        if "octal_uplc" in line.lower():
            parts = line.split()
            try:
                area = float(parts[-1])
            except:
                area = 0.0
            break
    return area

# Build the structure for a single vial per compound
data = []
for comp in compound_names:
    block = extract_compound_block(comp, lines)
    if not block:
        print(f"No block found for compound: {comp}")
        area = 0.0
    else:
        area = extract_octal_area(block)
    data.append({"Compound": comp, "vial1": area})

# Create and display the DataFrame
df_areas = pd.DataFrame(data)
print("\n=== DataFrame with Areas ===")
print(df_areas)
print(df_areas.to_markdown(index=False))

# Convert area values into octal classification based on defined thresholds
def classify_area(concentration):
    if concentration >= 0 and concentration <= 30:
        return 0
    elif concentration > 30 and concentration <= 70:
        return 1
    elif concentration > 70 and concentration <= 130:
        return 2
    elif concentration > 130 and concentration <= 260:
        return 3
    elif concentration > 260 and concentration <= 500:
        return 4
    elif concentration > 500 and concentration <= 750:
        return 5
    elif concentration > 750 and concentration <= 1189:
        return 6
    else:  # concentration > 1189
        return 7

df_areas["vial1"] = df_areas["vial1"].apply(classify_area)
print("\n=== DataFrame with Octal Classification ===")
print(df_areas)

# Decode the 'vial1' column from octal classification into ASCII text
# - The list is not reversed.
# - Each value is translated into 3 bits.
# - If there are 81 bits, remove the first bit to keep 80 (10 characters).
# - Group the bits into bytes and convert to ASCII.

# Step 1: Get the octal values from the DataFrame
octal_values = df_areas["vial1"].tolist()

# Step 2: Convert each value into a 3-bit binary string and concatenate
bitstream = ''.join(format(val, '03b') for val in octal_values)

# Step 3: If 81 bits are present, remove the first to align to 80 bits
if len(bitstream) == 81:
    bitstream = bitstream[1:]

# Step 4: Group into bytes (8 bits) and convert to ASCII characters
decoded_text = ''
for i in range(0, len(bitstream), 8):
    byte = bitstream[i:i+8]
    if len(byte) == 8:
        decoded_text += chr(int(byte, 2))

# Display final message
print("\n=== Octal to Text Decoding ===")
print("Decoded message:", decoded_text)
