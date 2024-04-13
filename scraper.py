import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("USER")
PASS = os.getenv("PASS")


def iniciar_sesion(user, password):
    base_url = "https://upsite.up.edu.mx/psp/CAMPUS/EMPLOYEE/SA/s"
    url = base_url + "?&cmd=login&languageCd=ENG"
    html = requests.get(url)

    # Crear sesión
    session = requests.Session()

    # Obtener la página de login
    html = session.get(url)

    # Analizar la página con BeautifulSoup
    soup = BeautifulSoup(html.content, "html.parser")

    # Buscar los elementos del formulario de inicio de sesión
    userid_field = soup.find("input", {"id": "userid"})
    pwd_field = soup.find("input", {"id": "pwd"})
    submit_button = soup.find("input", {"name": "Submit"})

    # Preparar los datos a enviar
    form_data = {}
    for input_field in soup.find_all("input"):
        if input_field.get("name"):
            form_data[input_field.get("name")] = input_field.get("value", "")
    form_data[userid_field["name"]] = user
    form_data[pwd_field["name"]] = password

    # Obtener el botón de inicio de sesión
    action_url = base_url + submit_button.find_parent("form")["action"]

    # Enviar formulario con los datos
    session.post(action_url, data=form_data)

    return session


def obtener_calificacion(session, id_alumno, ciclo):
    next_url = f"https://upsite.up.edu.mx/psc/CAMPUS/EMPLOYEE/SA/c/UP_SA_LEARNER_SERVICES.UP_GRD_ATT_LIST_SS.GBL?Page=UP_GRD_ATT_LIST_SS&Action=U&EMPLID={id_alumno}&STRM={ciclo}"

    # Usar el mismo objeto de sesión para navegar a la siguiente URL (mantener sesión iniciada)
    next_page = session.get(next_url)

    # Analizar la página a la que has navegado
    next_page_soup = BeautifulSoup(next_page.text, "html.parser")

    # Definir funciones para hacer coincidir elementos 'span'
    def has_descr_id(tag):
        return tag.name == "span" and tag.get("id", "").startswith(
            "UP_STDNTGRADSSV_DESCR"
        )

    def has_final_id(tag):
        return tag.name == "span" and tag.get("id", "").startswith("CAL_FINAL")

    # Buscar nombre del alumno
    stud_name = next_page_soup.find("span", id="PERSONAL_DATA_NAME")

    # Buscar elementos HTML con las materias y calificaciones finales
    descr_spans = next_page_soup.find_all(has_descr_id)
    final_spans = next_page_soup.find_all(has_final_id)

    materia = []
    calificacion = []

    for span in descr_spans[0:-1]:
        materia.append(span.text)

    for span in final_spans[0:-1]:
        calificacion.append(span.text)

    # Crear dataframe
    df = pd.DataFrame({"materia": materia, "calificacion": calificacion})

    df["ciclo"] = ciclo

    return [stud_name.text, df]


def generar_semestres(start, end):
    semestres = []

    while start <= end:
        semestres.append(str(start))
        if start % 10 == 2:
            start += 2
        elif start % 10 == 8 or start % 10 == 4:
            start += 4

    return semestres


def obtener_calificaciones(id_alumno, ciclo_inicio, ciclo_fin):
    print(USER)
    print(PASS)
    session = iniciar_sesion(user=USER, password=PASS)

    ciclo_fin = 1242 if ciclo_fin > 1242 else ciclo_fin
    semestres = generar_semestres(ciclo_inicio, ciclo_fin)

    df_full = pd.DataFrame()

    alumno_anterior = obtener_calificacion(
        session=session, id_alumno=id_alumno, ciclo=semestres[0]
    )[0]

    for semestre in semestres:
        try:
            alumno, df_alumnos = obtener_calificacion(session, id_alumno, semestre)
            if alumno_anterior == alumno:
                df_full = pd.concat([df_full, df_alumnos], ignore_index=True)
                alumno_anterior = alumno
        except:
            continue

    # Castear a número las calificaciones
    df_full["calificacion"] = pd.to_numeric(df_full["calificacion"], errors="coerce")

    # Eliminar valores nulos
    df_full = df_full.dropna(subset=["calificacion"])

    return [alumno_anterior, df_full]
