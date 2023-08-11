from fastapi import FastAPI
from fastapi import Query
from scraper import obtener_calificaciones

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI"}


@app.get("/calificaciones/")
def get_calificaciones(
    id_alumno: str = Query(...),
    ciclo_inicio: int = Query(...),
    ciclo_fin: int = Query(...),
):
    alumno, df_alumnos = obtener_calificaciones(id_alumno, ciclo_inicio, ciclo_fin)
    # Convert the DataFrame to a dictionary for JSON serialization
    calificaciones = df_alumnos.to_dict(orient="records")
    return {"alumno": alumno, "calificaciones": calificaciones}
