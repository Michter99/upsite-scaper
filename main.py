from fastapi import FastAPI
from fastapi import Query
from fastapi import HTTPException
from scraper import obtener_calificaciones
from dotenv import load_dotenv

load_dotenv()

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
    try:
        alumno, df_alumnos = obtener_calificaciones(id_alumno, ciclo_inicio, ciclo_fin)
        calificaciones = df_alumnos.to_dict(orient="records")
        return {"alumno": alumno, "calificaciones": calificaciones}
    except Exception as e:
        # Log the error for debugging (you can integrate logging for better tracking)
        print(str(e))
        # Return a generic error to the client
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching data."
        )
