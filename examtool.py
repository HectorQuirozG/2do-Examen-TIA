import pandas as pd
import json

anexob = pd.read_csv("AnexoB.csv")
incidentes_nuevos = pd.read_csv("incidents_master-selected-columns.csv")

quitar_id = lambda df: df.drop('ID', axis=1)

def limpiar(df):
    df = df.dropna(subset=["Registros_Comprometidos (Miles)", "Tiempo_Contencion (Hrs)"])
    Q1 = df["Registros_Comprometidos (Miles)"].quantile(0.25)
    Q3 = df["Registros_Comprometidos (Miles)"].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    df_resultado = df[(df["Registros_Comprometidos (Miles)"] >= limite_inferior) & (df["Registros_Comprometidos (Miles)"] <= limite_superior)]

    Q1 = df_resultado["Tiempo_Contencion (Hrs)"].quantile(0.25)
    Q3 = df_resultado["Tiempo_Contencion (Hrs)"].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    df_resultado = df_resultado[(df_resultado["Tiempo_Contencion (Hrs)"] >= limite_inferior) & (df_resultado["Tiempo_Contencion (Hrs)"] <= limite_superior)]
    return df_resultado

def formato_incidentes(df):
    df['data_compromised_records'] = df['data_compromised_records'] / 1000
    with open('sectores.json', 'r', encoding='utf-8') as f:
        sectores = json.load(f)
        df['industry_primary'] = df['industry_primary'].map(sectores)
    df['attack_vector_primary'] = df['attack_vector_primary'].str.capitalize()
    df = df[['industry_primary','attack_vector_primary','downtime_hours','data_compromised_records']]
    df.columns = ['Sector', 'Ataque', 'Tiempo_Contencion (Hrs)', 'Registros_Comprometidos (Miles)']
    return df
    
def combinar(df1, df2):
    df_lista = [df1, df2]
    df_combinado = pd.concat(df_lista, ignore_index=True)
    return df_combinado

def dataset_encode(df):
    with open('codigos_s.json', 'r', encoding='utf-8') as f:
        codigos = json.load(f)
        df['Sector'] = df['Sector'].map(codigos)
    with open('codigos_t.json', 'r', encoding='utf-8') as f:
        codigos = json.load(f)
        df['Ataque'] = df['Ataque'].map(codigos)
    return df

anexob = quitar_id(anexob)
incidentes_nuevos = formato_incidentes(incidentes_nuevos)

df_combinado = combinar(anexob, incidentes_nuevos)
df_combinado.to_csv('dataset_raw.csv', index=False)
print("Base de datos completa guardada como dataset_raw.csv")
df_combinado = limpiar(df_combinado)
df_combinado.to_csv('dataset.csv', index=False)
print("Base de datos limpia y homóloga guardada como dataset.csv")
