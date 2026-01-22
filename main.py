from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import cv2, numpy as np, easyocr, re

# unsafe celiac ingredients, will transition to a more compehensive database later
gluten_words = [
        "wheat", "wheat flour", "enriched wheat flour",
        "barley","rye","triticale",
        "malt","semolina","spelt","farina",
        "couscous","graham","panko","orzo",
        "brewers yeast","wheat bran","wheat germ",
        "contains: wheat"
    ]
app = FastAPI()
reader = easyocr.Reader(['en'])

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    img = cv2.resize(img, (0,0), fx=0.6, fy=0.6)

    results = reader.readtext(img, detail=0)
    text = " ".join(results).lower()

    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    if "ingredients" in text:
        text = text.split("ingredients",1)[1]

    found = []
    for word in gluten_words:
        if re.search(rf"\b{word}\b", text):
            found.append(word)

    safe = len(found) == 0
    return {"safe": safe, "found": found}

@app.get("/")
def root():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")