from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List
from uuid import uuid4
import json

app = FastAPI()

# ----------- ROOT -----------

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running"}

# ----------- МОДЕЛЬ -----------

class Movie(BaseModel):
    title: str
    year: int
    rating: float

class MovieResponse(Movie):
    id: str

# ----------- ГОТОВАЯ "БАЗА" -----------

movies_db = [
    {"id": str(uuid4()), "title": "Inception", "year": 2010, "rating": 8.8},
    {"id": str(uuid4()), "title": "Interstellar", "year": 2014, "rating": 8.6},
    {"id": str(uuid4()), "title": "The Dark Knight", "year": 2008, "rating": 9.0},
    {"id": str(uuid4()), "title": "Fight Club", "year": 1999, "rating": 8.8},
    {"id": str(uuid4()), "title": "Forrest Gump", "year": 1994, "rating": 8.8},
]

# ----------- СПЕЦИАЛЬНЫЕ ПУТИ (СНАЧАЛА!) -----------

@app.get("/movies/pretty")
def get_movies_pretty(min_rating: float = Query(0, ge=0, le=10)):
    filtered_movies = [m for m in movies_db if m["rating"] >= min_rating]
    json_data = json.dumps(filtered_movies, indent=4)
    return JSONResponse(content=json.loads(json_data))
@app.get("/multiplication_table")
def table():
    res=''
    for x in range(1,11):
        for y in range(1,11):
            res+=f'{x}*{y}={x*y}\n'
    return res




@app.get("/movies/html", response_class=HTMLResponse)
def get_movies_html(min_rating: float = Query(0, ge=0, le=10)):
    filtered_movies = [m for m in movies_db if m["rating"] >= min_rating]

    html_content = """
    <html>
    <head>
        <title>Movie List</title>x
        <style>
            table {border-collapse: collapse; width: 70%; margin: 20px auto;}
            th, td {border: 1px dashed #333; padding: 25px; text-align: center;}
            th {background-color: hotpink; color: white;}
            tr:nth-child(even) {background-color: #f2f2f2;}
        </style>
    </head>
    <body>
        <h2 style="text-align:center;">Movie Catalog</h2>
        <table>
            <tr>
                <th>#</th>
                <th>Title</th>
                <th>Year</th>
                <th>Rating</th>
            </tr>
    """
    for idx, movie in enumerate(filtered_movies, start=1):
        html_content += f"""
            <tr>
                <td>{idx}</td>
                <td>{movie['title']}</td>
                <td>{movie['year']}</td>
                <td>{movie['rating']}</td>
            </tr>
        """
    html_content += """
        </table>
    </body>
    </html>
    """
    return html_content

# ----------- CRUD -----------

@app.get("/movies", response_model=List[MovieResponse])
def get_movies(min_rating: float = Query(0, ge=0, le=10)):
    return [m for m in movies_db if m["rating"] >= min_rating]

@app.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: str):
    for movie in movies_db:
        if movie["id"] == movie_id:
            return movie
    raise HTTPException(status_code=404, detail="Movie not found")

@app.post("/movies", response_model=MovieResponse)
def create_movie(movie: Movie):
    new_movie = movie.dict()
    new_movie["id"] = str(uuid4())
    movies_db.append(new_movie)
    return new_movie



@app.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: str, updated: Movie):
    for movie in movies_db:
        if movie["id"] == movie_id:
            movie.update(updated.dict())
            return movie
    raise HTTPException(status_code=404, detail="Movie not found")

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: str):
    for i, movie in enumerate(movies_db):
        if movie["id"] == movie_id:
            movies_db.pop(i)
            return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Movie not found")

# uvicorn server:app --reload