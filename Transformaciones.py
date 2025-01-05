import swifter
import pandas as pd
import ast
import json
from typing import Optional, List

# Se cargan los archivos CSV
df=pd.read_csv("Movies/movies_dataset.csv", dtype={"popularity": str})

credits_df = pd.read_csv("Movies/credits.csv")

df.drop([19730,29503,35587], inplace=True) #Elimino esas 3 filas debido a que dan error, al revisarlas manualmente se ve que les falta informacion

# Se determino con este codigo que las 3 filas eliminadas son las que tienen valores nulos en la columna 'release_date'
#nan_rows = df[df['release_date'].isna()]

# Se cambia el valor del id a int despues de eliminar las 3 filas
df['id'] = df['id'].astype(int)
credits_df['id'] = credits_df['id'].astype(int)

# Se unen los DataFrames en base a la columna 'id'
df = pd.merge(df, credits_df, on='id', how='left')


#Transformacion 1

# Función para convertir cadenas de texto en diccionarios o listas de diccionarios, para acceder directamente a los valores
def clear_dict(cadena): 
        if cadena and isinstance(cadena, str):
                if isinstance(cadena, (dict, list)):
                        return cadena
                try:
                        cadena = ast.literal_eval(cadena)
                except (ValueError, SyntaxError):
                        cadena = json.loads(cadena.replace("'", '"'))
                return cadena
        
# Aplicar la función de conversión a varias columnas usando swifter
columns_to_clear = ["belongs_to_collection", "genres", "production_companies", "production_countries", "spoken_languages", "cast", "crew"]
df[columns_to_clear] = df[columns_to_clear].swifter.applymap(clear_dict)

#Transformacion 2

# Se cambia el tipo de las columnas 'revenue' y 'budget' a float
df["revenue"]=df["revenue"].astype(float)

df["budget"]=df["budget"].astype(float)

df["revenue"]=df["revenue"].fillna(0)

df["budget"]=df["budget"].fillna(0)

# Y también la columna 'popularity' a float y 'title' a string

df["popularity"]=df["popularity"].astype(float)

df["title"]=df["title"].astype(str)

#Transformacion 3

# Se convierte la columna 'release_date' a datetime
df["release_date"] = pd.to_datetime(df["release_date"], format='%Y-%m-%d',errors='coerce') #Debido a un error, se agrego el error="coerce"
df = df.dropna(subset="release_date")

# y se crea la columna release_year
df["release_year"] = df["release_date"].dt.year


#Transformacion 4

# Creacion de la columna 'return' que representa la relación entre la ganancia y el presupuesto
df['return'] = df['revenue'] / df['budget']
df['return'] = df['return'].fillna(0)

#Transformacion 5

# Eliminacion de las columnas que no se necesitan
df.drop("video", axis=1, inplace=True)
df.drop("imdb_id", axis=1, inplace=True)
df.drop("adult", axis=1, inplace=True)
df.drop("original_title", axis=1, inplace=True)
df.drop("poster_path", axis=1, inplace=True)
df.drop("homepage", axis=1, inplace=True)

# Mantener una columna con el título original
df["original_title"] = df["title"]

# Función para formatear los títulos para incluir el año entre paréntesis si hay duplicados
df['title'] = df.groupby('title').cumcount().astype(str).radd(df['title'] + ' (').radd(df['release_year'].astype(str) + ')')

# Función para reducir la información de la columna 'cast'
def reduce_cast(cast_list):
    if isinstance(cast_list, list):
        return [{'cast_id': cast['cast_id'], 'character': cast['character'], 'name': cast['name']} for cast in cast_list]
    return []

# Aplicar la función de reducción a la columna 'cast'
df['cast'] = df['cast'].apply(reduce_cast)

# Se crean DF especificos para get_actor y get_director
df_actor_success = df[['id', 'cast']]
df_revenue_budget = df[['id', 'revenue', 'budget']]
df_director_success = df[['id', 'crew', 'title', 'release_date']]
# Crear DataFrame específico para recomendaciones
df_recommendations = df.sort_values(by='release_date', ascending=False)[['id', 'title', 'original_title', 'release_year']]
df = df[['id', 'title', 'release_year', 'release_date', 'vote_average', 'popularity', 'vote_count']]

df.to_csv("./Datos/df.csv", index=False)
df_actor_success.to_csv("./Datos/df_actor_success.csv", index=False)
df_director_success.to_csv("./Datos/df_director_success.csv", index=False)
df_recommendations.to_csv("./Datos/df_recommendations.csv", index=False)
df_revenue_budget.to_csv("./Datos/df_revenue_budget.csv", index=False)