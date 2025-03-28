import re
import pandas as pd

# Read the Excel file without assuming headers
file_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE1_LC_script1\code1.xlsx'
df_excel = pd.read_excel(file_path, header=None)

# Print part of the DataFrame to visualize its structure (optional)
print(df_excel.head(10))

# Search for the cell containing the word "compound" (case-insensitive)
compound_position = None
for i in range(df_excel.shape[0]):
    for j in range(df_excel.shape[1]):
        value = str(df_excel.iat[i, j])
        if "compound" in value.lower():
            compound_position = (i, j)
            break
    if compound_position:
        break

if compound_position:
    row_compound, col_compound = compound_position
    print(f"'Compound' found at row {row_compound}, column {col_compound}")
    
    # Extract the values from the cells below the word "Compound"
    compounds = []
    for row in range(row_compound + 1, df_excel.shape[0]):
        cell = df_excel.iat[row, col_compound]
        # Stop if an empty or NaN cell is found
        if pd.isna(cell) or str(cell).strip() == "":
            break
        compounds.append(str(cell).strip())
    
    print("Compounds found:", compounds)
else:
    print("No cell containing the word 'Compound' was found.")

compound_names = compounds

# Read the full content of the text file
text_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE1_LC_script1\decoded_output.txt'
with open(text_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def extract_compound_block(compound, lines):
    """
    Searches the list of lines for the appearance of 'Compound <n>:' followed by the compound name.
    Returns the lines that contain the string 'code1_LC_152bits', which correspond to data rows.
    """
    pattern = re.compile(r'Compound\s+\d+:\s+' + re.escape(compound), re.IGNORECASE)
    start_index = None

    # Search for the line containing the compound
    for i, line in enumerate(lines):
        if pattern.search(line):
            start_index = i
            break

    if start_index is None:
        return []

    # Traverse from the found line until another "Compound" block is detected or end of file
    block_lines = []
    for j in range(start_index + 1, len(lines)):
        # Stop if another "Compound" block is detected
        if re.search(r'Compound\s+\d+:', lines[j], re.IGNORECASE):
            break
        # Only consider lines containing the phrase "code1_LC_152bits"
        if "code1_lc_152bits" in lines[j].lower():
            block_lines.append(lines[j].strip())
    return block_lines

def extract_areas_from_block(block_lines):
    """
    Extracts numeric area values from the block lines.
    Assumes the area value is the last element of the line (if it can be converted to float).
    If not, assigns 0.
    """
    areas = []
    for line in block_lines:
        parts = line.split()
        # Try to convert the last element to float (area)
        try:
            area = float(parts[-1])
        except:
            area = 0.0
        areas.append(area)
    return areas

# Prepare a list to store the area values for each compound
data = []
max_vials = 0  # Track the maximum number of vial entries across all compounds
for compound in compound_names:
    block = extract_compound_block(compound, lines)
    if not block:
        print(f"No block found for compound: {compound}")
        areas = []
    else:
        areas = extract_areas_from_block(block)
    max_vials = max(max_vials, len(areas))
    data.append({"Compound": compound, "areas": areas})

# Build the list of rows for the DataFrame,
# filling with zeros for compounds with fewer vials than the maximum found
rows_for_df = []
for d in data:
    row = {"Compound": d["Compound"]}
    for i in range(max_vials):
        row[f"vial{i+1}"] = d["areas"][i] if i < len(d["areas"]) else 0.0
    rows_for_df.append(row)

# Create and display the table (DataFrame)
df_areas = pd.DataFrame(rows_for_df)
print("\n=== DataFrame with Areas ===")
print(df_areas)
print(df_areas.to_markdown(index=False))

# Convert values to binary (0/1) using a threshold of 50
vial_columns = [col for col in df_areas.columns if col != "Compound"]
for col in vial_columns:
    df_areas[col] = df_areas[col].apply(lambda x: 1 if x > 50 else 0)

# Display binary result
print("\n=== Binary DataFrame (0/1) ===")
print(df_areas)

# Convert the binary columns into text
# For each vial column, take the list of bits, group them in 8-bit blocks (padding with zeros if needed),
# and convert each block to an ASCII character
final_phrase = ""
for vial in vial_columns:
    bits = df_areas[vial].tolist()
    remainder = len(bits) % 8
    if remainder != 0:
        bits += [0] * (8 - remainder)
    substring = ""
    for i in range(0, len(bits), 8):
        block_8 = bits[i:i+8]
        bin_str = "".join(str(b) for b in block_8)
        decimal_value = int(bin_str, 2)
        character = chr(decimal_value)
        substring += character
    final_phrase += substring

print("\nFinal decoded phrase:")
print(final_phrase)

