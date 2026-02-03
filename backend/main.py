from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.route("/upload")
def upload_file(py_file: UploadFile):
    if not py_file:
        return HTTPException(400, "File not uploaded")
    pass

@app.route("/status/{task_id}")
def check_status():
    pass

@app.route("/result/{task_id}")
def check_result():
    pass