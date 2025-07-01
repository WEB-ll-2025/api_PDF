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
import logging
from typing import Annotated
from fastapi import FastAPI, UploadFile, File, Response, Form
from PyPDF2 import PdfReader
from os import getcwd, remove, makedirs
from os.path import exists, join

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# create a FastAPI instance
app = FastAPI()


# create a post method to upload the file
@app.post("/boletamatricula")
async def upload_BoleMatri(cedula: Annotated[str,  Form()], periodo: Annotated[str,  Form()], file: UploadFile = File(...)):
    logger.info(f"Recibida petición - Cédula: {cedula}, Período: {periodo}, Archivo: {file.filename}")
    
    # declare the path of your temporal file
    temp_dir = join(getcwd(), 'temp')
    
    # create temp directory if it doesn't exist
    if not exists(temp_dir):
        makedirs(temp_dir)
    
    ruta = join(temp_dir, cedula + file.filename)
    logger.info(f"Ruta del archivo: {ruta}")

    # write the file in the temporal path
    try:
        with open(ruta, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        logger.info(f"Archivo guardado exitosamente en: {ruta}")
    except Exception as e:
        logger.error(f"Error al guardar archivo: {e}")
        return Response(content=f'{{"error": "Error al guardar el archivo: {str(e)}"}}', 
                       media_type="application/json", status_code=500)

    # validate if the file is a PDF
    if not valiArchi(ruta):
        logger.error(f"El archivo no es un PDF: {file.filename}")
        borArchi(ruta)
        return Response(content='{"error": "El archivo no es un PDF"}', media_type="application/json", status_code=400)

    # read the file and return the dictionary data and convert it to json
    resultado = lectura(ruta)
    logger.info(f"Resultado de lectura: {resultado}")
    
    # validate if the file is a boleta de matricula
    if resultado is None:
        logger.error("El archivo no es una boleta de matrícula válida")
        borArchi(ruta)
        return Response(content='{"error": "El archivo no es una boleta de matricula"}', media_type="application/json", status_code=400)

    data = json.JSONEncoder(indent=4).encode(resultado)

    # validate if the file is from the student
    resultado_cedula = resultado.get('cedula', '')
    resultado_periodo = resultado.get('periodo', '')
    logger.info(f"Validación - PDF Cédula: {resultado_cedula}, Enviada: {cedula}")
    logger.info(f"Validación - PDF Período: {resultado_periodo}, Enviado: {periodo}")
    
    # Validación flexible del período - acepta tanto "2025" como "I-2025"
    periodo_valido = (resultado_periodo == periodo) or (resultado_periodo.endswith(f"-{periodo}"))
    
    if (resultado_cedula != cedula) or not periodo_valido:
        logger.error(f"Mismatch - Cédula PDF: {resultado_cedula} vs Enviada: {cedula}, Período PDF: {resultado_periodo} vs Enviado: {periodo}")
        borArchi(ruta)
        return Response(content='{"error": "El archivo no pertenece al estudiante o el periodo es incorrecto"}', media_type="application/json", status_code=400)

    # delete the temporal file
    borArchi(ruta)
    logger.info("Procesamiento exitoso")
    return Response(content=data, media_type="application/json", status_code=200)


def valiArchi(ruta):
    """Valida si el archivo es un PDF basándose en su extensión"""
    try:
        extension = ruta.split('.')[-1].lower()  # Usa [-1] para obtener la última parte después del punto
        return extension == 'pdf'
    except:
        return False


def borArchi(ruta):
    """Borra el archivo temporal de forma segura"""
    try:
        if exists(ruta):
            remove(ruta)
    except Exception as e:
        print(f"Error al borrar archivo: {e}")


def lectura(ruta):
    """Lee el PDF y extrae la información de la boleta de matrícula"""
    try:
        # open the file using open() function
        with open(ruta, 'rb') as pdfFileObj:
            # create a pdf reader object
            documento = PdfReader(pdfFileObj)

            # read all the pages of pdf file using read() function
            pagina = documento.pages[0]
            contenido = pagina.extract_text()

        logger.info(f"Contenido extraído del PDF:\n{contenido}")
        
        # separte the content by lines
        separado = contenido.split('\n')
        logger.info(f"Líneas separadas: {len(separado)} líneas")
        
        for i, linea in enumerate(separado):
            logger.info(f"Línea {i}: {linea}")

        # Verificar que tenemos suficientes líneas
        if len(separado) < 5:
            logger.error(f"PDF no tiene suficientes líneas. Líneas encontradas: {len(separado)}")
            return None

        # retrieves the data from the line #3
        linea3 = separado[2].split(' ')
        logger.info(f"Línea 3 separada: {linea3}")
        
        if len(linea3) < 4:
            logger.error(f"Línea 3 no tiene suficientes elementos: {linea3}")
            return None
            
        cedula = linea3[0]
        apell1 = linea3[1]
        apell2 = linea3[2]
        nombre = linea3[3]
        periodo = linea3[-1]

        # retrieves the data from the line #4
        linea4 = separado[3].split(' ')
        logger.info(f"Línea 4 separada: {linea4}")
        
        if len(linea4) < 1:
            logger.error(f"Línea 4 no tiene elementos: {linea4}")
            return None
            
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
                    cursos.append(curso.strip())  # Quitar espacios extra
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
                'horario': horarios[i] if i < len(horarios) else '',
                'ubicacion': ubicacion[i] if i < len(ubicacion) else ''
            })

        salida = {
            'cedula': cedula,
            'nombre': apell1 + ' ' + apell2 + ' ' + nombre,
            'periodo': periodo,
            'boleta': boleta,
            'cursos': matriculados
        }
        
        logger.info(f"Datos extraídos exitosamente: {salida}")
        return salida
        
    except Exception as e:
        logger.error(f"Error en lectura del PDF: {e}")
        return None