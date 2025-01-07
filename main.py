import pandas as pd
from fastapi import FastAPI
import sklearn as sk

# Cargar los datos desde los archivos CSV generados en Transformaciones.py
df_funciones = pd.read_csv("./Datos/df_funciones.csv")
df_actor_success = pd.read_csv("./Datos/df_actor_success.csv")
df_director_success = pd.read_csv("./Datos/df_director_success.csv")
df_recommendations = pd.read_csv("./Datos/df_recommendations.csv")
df_revenue_budget = pd.read_csv("./Datos/df_revenue_budget.csv")

df_funciones['release_date'] = pd.to_datetime(df_funciones['release_date'], format='%Y-%m-%d', errors='coerce')


# Creacion de la API
app= FastAPI()
app.title = "Movies List"
app.version = "1.0.0"

# Se designa a cada mes su respectivo valor numerico
meses = { 'enero': 1,
          'febrero': 2, 
          'marzo': 3, 
          'abril': 4, 
          'mayo': 5, 
          'junio': 6, 
          'julio': 7, 
          'agosto': 8, 
          'septiembre': 9, 
          'octubre': 10, 
          'noviembre': 11, 
          'diciembre': 12 } 

# Se crea el endpoint para obtener la cantidad de filmaciones por mes
@app.get('/movies/release_date')
def cantidad_filmaciones_mes(mes: str):
    mes = mes.lower()
    if mes not in meses: 
        return {"error": "Mes inválido. Por favor, ingrese un mes en español correctamente."}
    mes_num = meses[mes] 
    peliculas_mes = df_funciones[df_funciones['release_date'].dt.month == mes_num]
    cantidad = peliculas_mes.shape[0] 
    return {"mes": mes, "cantidad": cantidad, "peliculas": peliculas_mes['title'].tolist()}

# Se designa a cada dia de la semana su respectivo valor numerico
dias_semana = {
    'lunes': 0,
    'martes': 1,
    'miércoles': 2,
    'jueves': 3,
    'viernes': 4,
    'sábado': 5,
    'domingo': 6
}

# Se crea el endpoint para obtener la cantidad de filmaciones por dia
@app.get('/movies/release_date_day')
def cantidad_filmaciones_dia(dia: str):
    dia = dia.lower()
    if dia not in dias_semana:
        return {"error": "Día inválido. Por favor, ingrese un día en español correctamente."}
    dia_num = dias_semana[dia]
    peliculas_dia = df_funciones[df_funciones['release_date'].dt.dayofweek == dia_num]
    cantidad = peliculas_dia.shape[0]
    return {"dia": dia, "cantidad": cantidad, "peliculas": peliculas_dia['title'].tolist()}

# Se crea el endpoint para obtener el score de una pelicula y el año de estreno
@app.get('/movies/score')
def score_titulo(titulo_de_la_filmacion: str):
    # Se busca la película por el título, en caso de no encontrar se avisa, si no es exacto al título se muestran las películas que contienen el texto ingresado 
    # y en caso de encontrarlo se muestra el título, el año de estreno y el score
    indices_titulo = df_funciones[df_funciones['title'].str.lower() == titulo_de_la_filmacion.lower()].index.tolist()
    if not indices_titulo:
        matching_movies = df_funciones[df_funciones['title'].str.lower().str.contains(titulo_de_la_filmacion.lower())]
        if matching_movies.empty:
            return {"error": "No se encontró ninguna película con el título proporcionado."}
        else:
            return {
                "message": f"Se encontraron {matching_movies.shape[0]} películas con el título '{titulo_de_la_filmacion}'.",
                "peliculas": matching_movies[['title', 'release_year']].to_dict(orient='records')
            }
    pelicula = df_funciones[df_funciones['title'].str.lower() == titulo_de_la_filmacion.lower()]
    titulo = pelicula['title'].values[0]
    anio_estreno = int(pelicula['release_year'].values[0])
    score = pelicula['popularity'].values[0]
    return {"titulo": titulo, "año de estreno": anio_estreno, "score": score}


# Se crea el endpoint para obtener los votos y el promedio de una pelicula y el año de estreno
@app.get('/movies/votes')
def votos_titulo(titulo_de_la_filmacion: str):
    # Se busca la película por el título, en caso de no encontrar se avisa, si no es exacto al título se muestran las películas que contienen el texto ingresado 
    # y en caso de encontrarlo se muestra el título, el año de estreno, los votos y el promedio de votos

    indices_titulo = df_funciones[df_funciones['title'].str.lower() == titulo_de_la_filmacion.lower()].index.tolist()
    
    if not indices_titulo:
        matching_movies = df_funciones[df_funciones['title'].str.lower().str.contains(titulo_de_la_filmacion.lower())]
        if matching_movies.empty:
            return {"error": "No se encontró ninguna película con el título proporcionado."}
        else:
            return {
                "message": f"Se encontraron {matching_movies.shape[0]} películas con el título '{titulo_de_la_filmacion}'.",
                "peliculas": matching_movies[['title', 'release_year']].to_dict(orient='records')
            }
    pelicula = df_funciones[df_funciones['title'].str.lower() == titulo_de_la_filmacion.lower()]
    votos = int(pelicula['vote_count'].values[0])
    if votos < 2000:
        return {"error": "La película no cumple con el mínimo de 2000 valoraciones."}
    return {
        "titulo": pelicula['title'],
        "año de estreno": int(pelicula['release_year'].values[0]),
        "votos": votos,
        "promedio_votos": float(pelicula['vote_average'])
        }

@app.get('/actor/success')
def get_actor(nombre_actor: str):
    # Se busca el actor en la columna 'cast' y se muestra la cantidad de peliculas en las que ha participado, el retorno total y el promedio de retorno
    actor_movies = df_actor_success[df_actor_success['name'].str.lower() == nombre_actor.lower()]
    if actor_movies.empty:
        return {"error": "Actor no encontrado. Por favor, ingrese un nombre válido."}
    cantidad_peliculas = actor_movies.shape[0]
    retorno_total = df_revenue_budget.loc[df_revenue_budget['id'].isin(actor_movies['id']), 'revenue'].sum() - df_revenue_budget.loc[df_revenue_budget['id'].isin(actor_movies['id']), 'budget'].sum()
    promedio_retorno = retorno_total / cantidad_peliculas if cantidad_peliculas > 0 else 0
    return {
        "actor": nombre_actor,
        "cantidad_peliculas": cantidad_peliculas,
        "retorno_total": retorno_total,
        "promedio_retorno": promedio_retorno
    }

@app.get('/director/success')
def get_director(nombre_director: str):

    # Se busca el director en la columna 'crew' y se muestra la cantidad de peliculas en las que ha participado, el retorno total y el promedio de retorno
    director_movies = df_director_success[df_director_success['name'].str.lower() == nombre_director.lower()]
    if director_movies.empty:
        return {"error": "Director no encontrado. Por favor, ingrese un nombre válido."}
    peliculas = []
    for _, row in director_movies.iterrows():
        retorno_individual = df_revenue_budget.loc[df_revenue_budget['id'] == row['id'], 'revenue'].values[0] - df_revenue_budget.loc[df_revenue_budget['id'] == row['id'], 'budget'].values[0]
        peliculas.append({
            "titulo": row['title'],
            "fecha lanzamiento": row['release_date'],
            "retorno individual": retorno_individual,
            "costo": df_revenue_budget.loc[df_revenue_budget['id'] == row['id'], 'budget'].values[0],
            "ganancia": df_revenue_budget.loc[df_revenue_budget['id'] == row['id'], 'revenue'].values[0]
        })
    retorno_total = df_revenue_budget.loc[df_revenue_budget['id'].isin(director_movies['id']), 'revenue'].sum() - df_revenue_budget.loc[df_revenue_budget['id'].isin(director_movies['id']), 'budget'].sum()
    return {
        "director": nombre_director,
        "retorno_total": retorno_total,
        "peliculas": peliculas
    }

# Se hizo el respectivo EDA, y se determino que la columna 'title' es la que se usara para las recomendaciones
# Se vectorizan los títulos de las películas usando TF-IDF y se crea el modelo KNN

vectorizer = sk.feature_extraction.text.TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df_recommendations['title'])

knn = sk.neighbors.NearestNeighbors(metric='cosine', algorithm='brute')
knn.fit(tfidf_matrix)


# Se crea la función para obtener las recomendaciones
def get_recommendations(title, df_recommendations, knn, vectorizer, top_n=5):
    # Se busca la película por el título, en caso de no encontrar se avisa, si no es exacto al título se muestran las películas que contienen el texto ingresado    
    indices_titulo = df_recommendations[df_recommendations['title'].str.lower() == title.lower()].index.tolist()
    if not indices_titulo:
        matching_movies = df_recommendations[df_recommendations['title'].str.lower().str.contains(title.lower())]
        if matching_movies.empty:
            return {"error": "No se encontró ninguna película con el título proporcionado."}
        else:
            return {
                "message": f"Se encontraron {matching_movies.shape[0]} películas con el título '{title}'.",
                "peliculas": matching_movies[['title', 'release_year']].to_dict(orient='records')
            }
    # Cuando el titulo es correcto, se procede con las recomendaciones
    
    # Se obtiene el vector TF-IDF del título original
    title_vector = vectorizer.transform([df_recommendations.loc[indices_titulo[0], 'original_title']])

    # Se obtienen los índices y distancias de las películas similares
    distances, indices = knn.kneighbors(title_vector, n_neighbors=top_n + len(indices_titulo) + 5)

    # Se aplanan los índices y distancias
    movie_indices = indices.flatten()
    distances = distances.flatten()

    # Excluir la película original de las recomendaciones
    movie_indices = [i for i in movie_indices if i not in indices_titulo]
    distances = [d for i, d in zip(indices.flatten(), distances) if i not in indices_titulo]

    # Y se obtienen las películas similares
    similar_movies = df_recommendations.iloc[movie_indices].copy()

    # Se agrega la columna de similaridad
    similar_movies['similarity_score'] = distances

    # Se ordenan las películas por similaridad
    similar_movies = similar_movies.sort_values(by='similarity_score', ascending=True)

    # Retornar los títulos de las películas recomendadas
    return similar_movies['title'].head(top_n).tolist()

# Se crea el endpoint para obtener las recomendaciones
@app.get("/recomendacion")
def recomendacion(title: str):
    return get_recommendations(title, df_recommendations, knn, vectorizer)
