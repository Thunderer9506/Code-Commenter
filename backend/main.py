from fastapi import FastAPI, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid1
import os


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#------------ Utils ------------
def inputFile(content:str|bytes,filename:str,id:str):
    try:
        folder_name = './backend/temp/input'
        os.makedirs(folder_name, exist_ok=True)
        full_path = os.path.join(folder_name, f"{filename}_{id}.py")
        if isinstance(content, (bytes, bytearray)):
            mode = "wb"
        else:
            mode = "w"
        with open(full_path,mode) as file:
            file.write(content)
    except Exception as e:
        print(f"An Exception Occured {e}")
        return False
    return True

@app.post("/upload")
async def upload_file(py_file: UploadFile):
    if not py_file:
        return HTTPException(400, "File not uploaded")
    if py_file.content_type != 'text/x-python':
        return HTTPException(400, "File is not a Python File")
    
    id = str(uuid1())
    file_content = await py_file.read()
    write_file = inputFile(file_content,py_file.filename,id) #type: ignore
    
    if not write_file:
        return HTTPException(500, "Internal Server Error Occured")
    return {"message": "Processing started", "task_id": id}

@app.get("/status/{task_id}")
def check_status():
    pass

@app.get("/result/{task_id}")
def check_result():
    pass