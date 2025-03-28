import re
import pandas as pd
import numpy as np
from PIL import Image

# Read the Excel file without assuming headers
excel_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\code4_QUAT_script2\QUAT_FIA\code1.xlsx'
# Use the appropriate sheet (in this case, the first one)
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
text_path = r'C:\Users\tinajero\Desktop\codes_Cristopher\code4_QUAT_script2\QUAT_FIA\decoded_output.txt'
with open(text_path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

def extract_compound_block(compound, lines):
    """
    Searches for the section starting with "Compound n: <compound>"
    and returns the lines until the next "Compound n:" appears.
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

def extract_analyte_areas(block_lines):
    """
    From the block of a compound, search for lines where the "Type" is "Analyte" (case-insensitive).
    For each line, extract the last token and attempt to convert it to float.
    Returns a list of values (one per "Analyte" line).
    """
    areas = []
    for line in block_lines:
        if "analyte" in line.lower():
            parts = line.split()
            try:
                area = float(parts[-1])
            except:
                area = 0.0
            areas.append(area)
    return areas

# Prepare a structure to store up to 10 vial values per compound
data = []
expected_vials = 10

for comp in compound_names:
    block = extract_compound_block(comp, lines)
    areas = extract_analyte_areas(block)
    if not areas:
        print(f"No 'Analyte' lines found for compound: {comp}")
    # Pad with zeros if fewer than 10 values
    if len(areas) < expected_vials:
        areas += [0.0] * (expected_vials - len(areas))
    # Trim if more than 10 values
    areas = areas[:expected_vials]

    # Build a dictionary for each row
    row_dict = {"Compound": comp}
    for i in range(expected_vials):
        row_dict[f"vial{i+1}"] = areas[i]
    data.append(row_dict)

# Create and display the table (DataFrame)
df_areas = pd.DataFrame(data)
print("\n=== DataFrame with Areas ===")
print(df_areas)
print(df_areas.to_markdown(index=False))

# Convert each area value to an octal classification based on defined thresholds
def classify_area(concentration):
    if concentration >= 0 and concentration <= 30:
        return 0
    elif concentration > 45 and concentration <= 200:
        return 1
    elif concentration > 400 and concentration <= 850:
        return 2
    elif concentration > 1050 and concentration <= 1950:
        return 3

vial_columns = [f"vial{i+1}" for i in range(expected_vials)]
for col in vial_columns:
    df_areas[col] = df_areas[col].apply(classify_area)

print("\n=== DataFrame with Octal Classification ===")
print(df_areas)

# Create an image representation from the classification matrix
# Convert the DataFrame into a matrix (dimensions: n_compounds x 10)
matrix_data = df_areas[vial_columns].to_numpy()
n_rows, n_cols = matrix_data.shape

# Define the color mapping for each classification
color_map = {
    0: [0, 0, 0],       # Black
    1: [0, 255, 0],     # Green
    2: [0, 0, 255],     # Blue
    3: [255, 255, 0],   # Yellow
    4: [255, 165, 0],   # Orange
    5: [255, 0, 0],     # Red
    6: [128, 0, 128],   # Purple
    7: [255, 255, 255]  # White
}

# ANSI color map for console output
ansi_color_map = {
    0: "\033[40m",        # Black background
    1: "\033[42m",        # Green background
    2: "\033[44m",        # Blue background
    3: "\033[43m",        # Yellow background
    4: "\033[48;5;208m",  # Orange background (256-color mode)
    5: "\033[41m",        # Red background
    6: "\033[45m",        # Purple background
    7: "\033[47m"         # White background
}
reset = "\033[0m"

# Console representation of the matrix
print("\nConsole representation of the image:")
for i in range(n_rows):
    row_str = ""
    for j in range(n_cols):
        value = matrix_data[i, j]
        row_str += ansi_color_map[value] + "  " + reset

# Rotate the matrix to orient the image horizontally if needed
matrix_data_rot = np.rot90(matrix_data, k=-1)
n_rows_rot, n_cols_rot = matrix_data_rot.shape

# Flip horizontally for correct visualization
matrix_data_flipped = np.fliplr(matrix_data_rot)
n_rows_flip, n_cols_flip = matrix_data_flipped.shape

# Display the flipped matrix in the console
for i in range(n_rows_flip):
    row_str = ""
    for j in range(n_cols_flip):
        value = matrix_data_flipped[i, j]
        row_str += ansi_color_map[value] + "  " + reset
    print(row_str)
