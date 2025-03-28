# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 13:38:47 2025

@author: tinajero
"""

import pandas as pd

ruta_archivo = r'C:\Users\tinajero\Desktop\codes_Cristopher\CODE3_FIA_script1\code1.xlsx'
df = pd.read_excel(ruta_archivo, header=None)

matches = []
for i in range(df.shape[0]):
    for j in range(df.shape[1]):
        val = str(df.iat[i, j]).strip()
        if "compound" in val.lower():
            matches.append(((i, j), val))
            
print("Se encontraron coincidencias:")
for pos, texto in matches:
    print(f"Celda {pos}: {texto}")