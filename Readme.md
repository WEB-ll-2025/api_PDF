### Goals
Create API-Rest to read a PDF file and return the data in JSON format.
Using FastAPI and PyPDF2 and multipart/form-data to capture the file 
and others student data.

### Create virtual environment
```bash
python -m venv venv
```

### Activate virtual environment on linux
```bash 
source venv/bin/activate
```

### Activate virtual environment on windows
```bash
.\venv\Scripts\activate
```

### Update pip
```bash 
python -m pip install --upgrade pip
```

### Install libraries
```bash
pip install pypdf2 fastapi uvicorn python-multipart
```

### Run
```bash
uvicorn main:app --host='0.0.0.0' --port='5025' --reload
```

### Test
```bash
http://localhost:5025/docs

Press button Try it out and select a PDF file and fill the form with student data.
```
[Enlace a la documentación de FastAPI](https://fastapi.tiangolo.com/es/)
