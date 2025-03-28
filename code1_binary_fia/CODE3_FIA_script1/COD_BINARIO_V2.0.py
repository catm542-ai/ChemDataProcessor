import re
import pandas as pd

# Read the Excel file without assuming headers
file_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE3_FIA_script1\code1.xlsx'
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
text_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE3_FIA_script1\decoded_output.txt'
with open(text_path, 'r', encoding='latin-1') as f:
    lines = f.readlines()

def extract_compound_block(compound, lines):
    """
    Searches the list of lines for the appearance of 'Compound <n>:' followed by the compound name.
    Returns the lines that contain the string "flavonoids 80 bits" (vial indicator in this format).
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
        # Only consider lines containing the phrase "flavonoids 80 bits"
        if "flavonoids 80 bits" in lines[j].lower():
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

# Prepare a list to store the information for each compound
data = []
for compound in compound_names:
    block = extract_compound_block(compound, lines)
    if not block:
        print(f"No block found for compound: {compound}")
        area = 0.0
    else:
        areas = extract_areas_from_block(block)
        # Take the first (and only) value
        area = areas[0] if areas else 0.0
    data.append({"Compound": compound, "vial1": area})

# Create and display the table (DataFrame)
df_areas = pd.DataFrame(data)
print("\n=== DataFrame with Areas ===")
print(df_areas)
print(df_areas.to_markdown(index=False))

# Convert values to binary (0/1) based on whether the area is greater than 0
vial_columns = [col for col in df_areas.columns if col != "Compound"]
for col in vial_columns:
    df_areas[col] = df_areas[col].apply(lambda x: 1 if x > 0 else 0)

# Display binary result
print("\n=== Binary DataFrame (0/1) ===")
print(df_areas)

# Convert the vertical list of bits into text by grouping in 8-bit blocks
bits = df_areas["vial1"].tolist()
remainder = len(bits) % 8
if remainder != 0:
    bits += [0] * (8 - remainder)

final_phrase = ""
for i in range(0, len(bits), 8):
    block_8 = bits[i:i+8]
    bin_str = "".join(str(b) for b in block_8)
    decimal_value = int(bin_str, 2)
    character = chr(decimal_value)
    final_phrase += character

print("\nFinal decoded phrase:")
print(final_phrase)
