from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io, re
from pypdf import PdfReader
from rank_bm25 import BM25Okapi

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

db = {'chunks': [], 'bm25': None, 'filename': None}

class QueryReq(BaseModel):
    question: str

def clean_text(text: str) -> str:
    text = re.sub(r'(?<=\b[a-zA-Z])\s+(?=[a-zA-Z]\b)', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

@app.get('/health')
def health():
    return {'status': 'online', 'pdf_loaded': db['filename'] is not None}

@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    reader = PdfReader(io.BytesIO(pdf_bytes))
    chunks = []
    
    for i, page in enumerate(reader.pages):
        raw_text = page.extract_text() or ''
        cleaned = clean_text(raw_text)
        
        # Deprioritize glossary / index pages for general queries
        is_glossary = any(k in cleaned.lower() for k in ['glossary', 'explanation of terms', 'index of terms'])
        if cleaned:
            chunks.append({
                'page': i + 1, 
                'text': cleaned,
                'is_glossary': is_glossary
            })
            
    if not chunks:
        raise HTTPException(status_code=400, detail='No readable text found in PDF.')
    
    corpus = [re.findall(r'\w+', c['text'].lower()) for c in chunks]
    db['chunks'] = chunks
    db['bm25'] = BM25Okapi(corpus)
    db['filename'] = file.filename
    return {'filename': file.filename, 'status': 'success', 'pages': len(chunks)}

@app.post('/ask')
def ask(req: QueryReq):
    if not db['chunks']:
        raise HTTPException(status_code=400, detail='Please upload a PDF first.')
    
    q_lower = req.question.lower()
    q_tokens = re.findall(r'\w+', q_lower)
    scores = db['bm25'].get_scores(q_tokens) if db['bm25'] is not None else []
    
    # Filter candidates: prioritize non-glossary pages unless user asks for definition
    asking_definition = any(k in q_lower for k in ['what is', 'define', 'meaning', 'explanation']) and not any(k in q_lower for k in ['revenue', 'profit', 'price', 'turnover', 'amount', 'total'])
    
    candidates = []
    if len(scores) > 0:
        scores_list = list(scores)
        # Apply penalty to glossary pages for numerical questions
        for idx, score in enumerate(scores_list):
            adjusted_score = score
            if db['chunks'][idx]['is_glossary'] and not asking_definition:
                adjusted_score *= 0.1
            candidates.append((idx, adjusted_score))
            
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_idx = [c[0] for c in candidates[:2]]
        matched = [db['chunks'][i] for i in top_idx]
    else:
        matched = db['chunks'][:2]
    
    # Math calculation detection
    nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', req.question)]
    calc = None
    if len(nums) >= 2 and any(k in q_lower for k in ['increase', 'change', 'percent', 'growth', 'from']):
        c, p = nums[1], nums[0]
        if p != 0:
            diff = c - p
            pct = (diff / abs(p)) * 100
            calc = {'formula': f'(({c} - {p}) / {p}) * 100', 'result': f'{pct:+.2f}%', 'diff': f'{diff:+.2f}'}

    pages = [m['page'] for m in matched]
    summary = ' '.join([m['text'] for m in matched])[:380]
    answer = f"Based on the report (Page {pages[0]}): {summary}..."

    return {
        'question': req.question, 
        'answer': answer, 
        'pages': pages, 
        'calculation': calc
    }
