"""================================================================================================
Institute....: Universidad Técnica Nacional
Headquarters.: Pacífico
Career.......: Tecnologías de la Información
Period.......: II-2025
Document.....: apiPDF.main.py
Goals........: Create API-Rest to read a PDF file and return the data in JSON format
Professor....: Jorge Ruiz (york)
Student......:
================================================================================================"""

# import required modules or libraries
import json
from typing import Annotated
from fastapi import FastAPI, UploadFile, File, Response, Form
from PyPDF2 import PdfReader
from os import getcwd, remove


# create a FastAPI instance
app = FastAPI()


# create a post method to upload the file
@app.post("/boletamatricula")
async def upload_BoleMatri(cedula: Annotated[str,  Form()], periodo: Annotated[str,  Form()], file: UploadFile = File(...)):
    # declare the path of your temporal file
    ruta = getcwd() + '/temp/' + cedula + file.filename

    # write the file in the temporal path
    with open(ruta, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        buffer.close()

    # validate if the file is a PDF
    if not valiArchi(ruta):
        borArchi(ruta)
        return Response(content='{"error": "El archivo no es un PDF"}', media_type="application/json", status_code=400)

    # read the file and return the dictionary data and convert it to json
    data = json.JSONEncoder(indent=4).encode(lectura(ruta))

    # validate if the file is a boleta de matricula
    if data == 'null':
        borArchi(ruta)
        return Response(content='{"error": "El archivo no es una boleta de matricula"}', media_type="application/json", status_code=400)

    # validate if the file is from the student
    if (json.JSONDecoder().decode(data)['cedula'] != cedula) or (json.JSONDecoder().decode(data)['periodo'] != periodo):
        borArchi(ruta)
        return Response(content='{"error": "El archivo no pertenece al estudiante o el periodo es incorrecto"}', media_type="application/json", status_code=400)

    # delete the temporal file
    borArchi(ruta)
    return Response(content=data, media_type="application/json", status_code=200)


def valiArchi(ruta):
    if ruta.split('.')[1].lower() == 'pdf':
        return True
    else:
        return False


def borArchi(ruta):
    remove(ruta)


def lectura(ruta):
    try:
        # open the file using open() function
        pdfFileObj = open(ruta, 'rb')

        # create a pdf reader object
        documento = PdfReader(pdfFileObj)

        # read all the pages of pdf file using read() function
        pagina =  documento.pages[0]
        contenido = pagina.extract_text()

        # close the pdf file object
        pdfFileObj.close()

        # separte the content by lines
        separado = contenido.split('\n')

        # retrieves the data from the line #3
        linea3 = separado[2].split(' ')
        cedula = linea3[0]
        apell1 = linea3[1]
        apell2 = linea3[2]
        nombre = linea3[3]
        periodo = linea3[-1]

        # retrieves the data from the line #4
        linea4 = separado[3].split(' ')
        boleta = linea4[-1]

        # retrieves the data from the line #5 to the end
        codigos = []
        grupos = []
        cursos = []
        creditos = []
        horarios = []
        ubicacion = []

        fila = 4
        while fila < len(separado):
            lineactual = separado[fila].split(' ')
            if lineactual[0] == 'Total':
                break

            if (len(lineactual) >= 6) and (lineactual[-1] != cedula):
                if len(lineactual[0]) > 1:
                    codigos.append(lineactual[0])
                    grp = lineactual[1][0]
                    grupos.append(grp)
                    lineactual[1] = lineactual[1].replace(grp, '')

                    curso = ''
                    posi = 1
                    while posi < len(lineactual)-3:
                        curso += lineactual[posi] + ' '
                        posi += 1
                    cursos.append(curso)
                    creditos.append(lineactual[-3].split('.')[0])
                else:
                     horarios.append(lineactual[0] + ' ' + lineactual[1] + ' a ' + lineactual[2])
                     ubicacion.append(lineactual[4] + ' ' + lineactual[5].split('.')[0])

            fila += 1

        matriculados = []

        for i in range(len(codigos)):
            matriculados.append({
                'codigo': codigos[i],
                'curso': cursos[i],
                'creditos': creditos[i],
                'grupo': grupos[i],
                'horario': horarios[i],
                'ubicacion': ubicacion[i]
            })

        salida = {
            'cedula': cedula,
            'nombre': apell1 + ' ' + apell2 + ' ' + nombre,
            'periodo': periodo,
            'boleta': boleta,
            'cursos': matriculados
        }
    except:
        salida = None

    return salida
