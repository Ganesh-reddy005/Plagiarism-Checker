from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import uuid
import io
import pypdf

from app.database import index_document
from app.preprocessor import split_into_sentences

router = APIRouter()

class DocumentResponse(BaseModel):
    success: bool
    document_id: str
    sentences_indexed: int

class ExtractResponse(BaseModel):
    success: bool
    text: str

async def extract_text_from_file(file: UploadFile) -> str:
    content = await file.read()
    if file.filename.lower().endswith(".pdf"):
        # Use pypdf to parse the PDF bytes
        pdf_file = io.BytesIO(content)
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        
        # Normalize whitespace (replace multiple spaces/newlines with a single space)
        # to ensure the content behaves exactly like manual copy-paste.
        import re
        text = re.sub(r"\s+", " ", text).strip()
        return text
    else:
        # Assume UTF-8 text file as fallback
        return content.decode("utf-8")

@router.post("/extract-text", response_model=ExtractResponse)
async def extract_text_endpoint(file: UploadFile = File(...)):
    """
    Extract raw text from an uploaded PDF or TXT file for the frontend to display.
    """
    if not (file.filename.lower().endswith(".pdf") or file.filename.lower().endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")
    try:
        text = await extract_text_from_file(file)
        return ExtractResponse(success=True, text=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a document (PDF or TXT) to be indexed in the internal database.
    """
    if not (file.filename.lower().endswith(".pdf") or file.filename.lower().endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported for now.")
        
    try:
        text = await extract_text_from_file(file)
        
        # Split into sentences for fine-grained search
        sentences = split_into_sentences(text)
        
        doc_id = str(uuid.uuid4())
        
        # Index in Qdrant
        index_document(doc_id, title, sentences)
        
        return DocumentResponse(
            success=True,
            document_id=doc_id,
            sentences_indexed=len(sentences)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
