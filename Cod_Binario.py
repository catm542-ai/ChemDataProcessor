import re
import pandas as pd

# Read the Excel file without assuming headers
file_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE1_FIA_script1\code1.xlsx'
df = pd.read_excel(file_path, header=None)

# Print part of the DataFrame to visualize its structure (optional)
print(df.head(10))

# Search for the cell containing the word "compound" (case-insensitive)
compound_position = None
for i in range(df.shape[0]):
    for j in range(df.shape[1]):
        value = str(df.iat[i, j])
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
    for row in range(row_compound + 1, df.shape[0]):
        cell = df.iat[row, col_compound]
        # Stop if an empty or NaN cell is found
        if pd.isna(cell) or str(cell).strip() == "":
            break
        compounds.append(cell)
    
    print("Compounds found:", compounds)
else:
    print("No cell containing the word 'Compound' was found.")

compound_names = compounds

# Read the full content of the text file
text_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE1_FIA_script1\decoded_output.txt'
with open(text_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def extract_compound_block(compound, lines):
    """
    Searches the list of lines for the appearance of 'Compound' followed by the name.
    Returns the lines (as a list) that contain the vial table (i.e., lines containing 'vial').
    """
    # Prepare the search pattern. Case-insensitive.
    pattern = re.compile(r'Compound\s+\d+:\s+' + re.escape(compound), re.IGNORECASE)
    start_index = None

    # Search for the line containing the compound
    for i, line in enumerate(lines):
        if pattern.search(line):
            start_index = i
            break

    if start_index is None:
        return None

    # Traverse from the found line until another "Compound" block is detected or end of file
    block_lines = []
    for j in range(start_index + 1, len(lines)):
        # Stop if another "Compound" block is detected
        if re.search(r'Compound\s+\d+:', lines[j], re.IGNORECASE):
            break
        # Only consider lines containing the word "vial" (to identify table rows)
        if "vial" in lines[j].lower():
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
    # Ensure there are 5 values (pad with zeros if fewer)
    while len(areas) < 5:
        areas.append(0.0)
    return areas[:5]  # Only take the first 5

# Prepare a list to store the information for each compound
data = []
for compound in compound_names:
    block = extract_compound_block(compound, lines)
    if block is None:
        print(f"No block found for compound: {compound}")
        areas = [0.0] * 5
    else:
        areas = extract_areas_from_block(block)
    data.append({
        "Compound": compound,
        "vial1": areas[0],
        "vial2": areas[1],
        "vial3": areas[2],
        "vial4": areas[3],
        "vial5": areas[4]
    })

# Create and display the table (DataFrame)
df_areas = pd.DataFrame(data)
print(df_areas)
print(df_areas.to_markdown(index=False))

# List of numeric columns to be converted
vial_columns = ["vial1", "vial2", "vial3", "vial4", "vial5"]

# Convert the values of each column to 0 or 1 based on a threshold
for col in vial_columns:
    df_areas[col] = df_areas[col].apply(lambda x: 1 if x > 50 else 0)

# Display the result
print(df_areas)

# Columns of interest (excluding 'Compound')
vials = ["vial1", "vial2", "vial3", "vial4", "vial5"]

final_phrase = ""

for vial in vials:
    # Extract the 32 bits (in top-to-bottom order)
    bits = df_areas[vial].tolist()  # This yields a list of 32 zeros/ones
    
    # Split into 4 groups of 8 bits
    groups_of_8 = [bits[i:i+8] for i in range(0, 32, 8)]
    
    # Convert each group of 8 bits to an ASCII character
    substring = ""
    for group in groups_of_8:
        # Convert the bit list to a binary string (e.g., "01000001")
        bin_str = "".join(str(bit) for bit in group)
        # Convert binary to decimal
        decimal_value = int(bin_str, 2)
        # Convert decimal to ASCII character
        character = chr(decimal_value)
        substring += character
    
    # Append to the final text
    final_phrase += substring

print("Final decoded phrase:")
print(final_phrase[:-1])
