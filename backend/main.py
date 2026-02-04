from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from Agent.main import Agent
from uuid import uuid1
import os
from typing import Optional, Literal, List


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#------------ Utils ------------
def inputFile(content: str | bytes, filename: str, id: str, folder: Literal["input", "output"] = "input"):
    try:
        folder_name = f'./backend/temp/{folder}'
        os.makedirs(folder_name, exist_ok=True)
        full_path = os.path.join(folder_name, f"{filename}_{id}.py")
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

def write_code(filename, file_content, id: str):
    try:
        init_agent = Agent()
        # If generateCode is synchronous:
        refactored_code = init_agent.generateCode(file_content.decode('utf-8'))
        # If generateCode is async, change this function to async and await it instead.
        success = inputFile(refactored_code, filename, id, "output")  # type: ignore
        if not success:
            print("Failed to write output file")
    except Exception as e:
        print("write_code failed:", e)
    
@app.post("/upload")
async def upload_file(py_file: UploadFile, background_tasks: BackgroundTasks):
    if not py_file:
        raise HTTPException(400, "File not uploaded")
    if py_file.content_type != 'text/x-python':
        raise HTTPException(400, "File is not a Python File")

    id = str(uuid1())
    file_content = await py_file.read()
    inputFile(file_content, py_file.filename, id, "input")  # type: ignore

    background_tasks.add_task(write_code, py_file.filename, file_content, id)  # use instance
    return {"message": "Processing started", "task_id": id}

@app.get("/status/{task_id}")
def check_status():
    pass

@app.get("/result/{task_id}")
def check_result():
    pass