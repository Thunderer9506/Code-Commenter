from fastapi import FastAPI, File, HTTPException, BackgroundTasks, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from Agent.main import Agent
from uuid import uuid1
import os
from typing import Literal,Annotated



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#------------ Utils ------------
def inputFile(content: str | bytes, id: str, folder: Literal["input", "output"] = "input"):
    try:
        folder_name = f'./backend/temp/{folder}'
        os.makedirs(folder_name, exist_ok=True)
        full_path = os.path.join(folder_name, f"{id}.py")
        if isinstance(content, (bytes, bytearray)):
            mode = "wb"
        else:
            mode = "w"
        with open(full_path, mode) as file:
            file.write(content)
    except Exception as e:
        print(f"An Exception Occured {e}")
        return False
    return True

def write_code(file_content, id: str, style:str):
    try:
        init_agent = Agent()
        # If generateCode is synchronous:
        refactored_code = init_agent.generateCode(file_content.decode('utf-8')+f"\n\n write in {style} and do not make any mistake")
        # If generateCode is async, change this function to async and await it instead.
        success = inputFile(refactored_code, id, "output")  # type: ignore
        if not success:
            print("Failed to write output file")
    except Exception as e:
        print("write_code failed:", e)
    
@app.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(py_file: Annotated[UploadFile, File(...)], background_tasks: BackgroundTasks, style:str = "Google Style"):
    if not py_file:
        raise HTTPException(400, "File not uploaded")
    if py_file.content_type != 'text/x-python':
        raise HTTPException(400, "File is not a Python File")

    id = str(uuid1())
    file_content = await py_file.read()
    inputFile(file_content, id, "input")  # type: ignore

    background_tasks.add_task(write_code, file_content, id, style)  # use instance
    return {"message": "Processing started", "task_id": id}

@app.get("/status/{task_id}",status_code=status.HTTP_200_OK)
def check_status(task_id:str|None):
    if not task_id:
        raise HTTPException(400,"Task Id not provided")
    
    if os.path.exists(f'./backend/temp/input/{task_id}.py') and os.path.exists(f'./backend/temp/output/{task_id}.py'):
        return {"Message":"File has been processed","Success": True}
    else:
        return {"Message":"File has not been processed","Success": False}

@app.get("/download/{task_id}",status_code=status.HTTP_200_OK)
def send_file(task_id:str|None):
    if not task_id:
        raise HTTPException(400,"Task Id not provided")
    full_path = f'./backend/temp/output/{task_id}.py'
    if not os.path.exists(full_path):
        return {"Message":"File has not been processed","Success": False}
    
    return FileResponse(
        path=full_path,
        media_type='text/x-python',
        filename="main.py"
    )