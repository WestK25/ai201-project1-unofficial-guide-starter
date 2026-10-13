"""Local ingestion, stable character chunks, Chroma vectors, and hybrid retrieval."""
from pathlib import Path
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parent
os.environ.setdefault('HF_HOME', str(ROOT / '.cache' / 'huggingface'))
os.environ.setdefault('ANONYMIZED_TELEMETRY', 'False')
MODEL = 'sentence-transformers/all-MiniLM-L6-v2'


def load_documents(directory=ROOT / 'documents'):
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f'Document directory missing: {directory}')
    documents = []
    for path in sorted(directory.glob('*.txt')):
        if path.name.startswith(('.', '_')):
            continue
        raw = path.read_text(encoding='utf-8-sig').strip()
        if not raw:
            continue
        if '\nCONTENT:\n' not in raw:
            raise ValueError(f'{path.name}: expected metadata followed by CONTENT:')
        header, body = raw.split('\nCONTENT:\n', 1)
        metadata = {'filename': path.name}
        for line in header.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.lower().replace(' ', '_')] = value.strip()
        if metadata.get('status') in {'todo', 'unverified', 'placeholder'}:
            continue
        for key in ['source', 'accessed', 'source_type', 'topic']:
            if not metadata.get(key):
                raise ValueError(f'{path.name}: missing {key}')
        if metadata['source_type'] not in {'official', 'student'}:
            raise ValueError(f'{path.name}: invalid source type')
        metadata.setdefault('source_url', '')
        body = re.sub(r'\s+', ' ', body).strip()
        if body:
            documents.append({'text': body, 'metadata': metadata})
    if not documents:
        raise ValueError('No usable documents. Add verified .txt files with metadata and CONTENT:.')
    return documents


def chunk_documents(documents, size=800, overlap=150):
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError('Require size > 0 and 0 <= overlap < size.')
    chunks = []
    for doc in documents:
        body = doc['text']
        seen = set()
        for start in range(0, len(body), size - overlap):
            end = min(start + size, len(body))
            text = body[start:end]
            if text.strip() and text not in seen:
                seen.add(text)
                metadata = {**doc['metadata'], 'start': start, 'end': end,
                            'chunk_size': size, 'overlap': overlap}
                identity = json.dumps([metadata, text], sort_keys=True)
                chunks.append({'id': hashlib.sha256(identity.encode()).hexdigest()[:24],
                               'text': text, 'metadata': metadata})
            if end == len(body):
                break
    return chunks


def fingerprint(chunks):
    return hashlib.sha256(json.dumps([MODEL, chunks], sort_keys=True).encode()).hexdigest()


def tokens(text):
    return re.findall(r'[a-z0-9]+', text.lower())


class Retriever:
    def __init__(self, directory=ROOT / 'documents', database=ROOT / 'chroma_db',
                 size=800, overlap=150):
        import chromadb
        from chromadb.config import Settings
        self.chunks = chunk_documents(load_documents(directory), size, overlap)
        self.signature = fingerprint(self.chunks)
        self.client = chromadb.PersistentClient(path=str(database), settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(
            f'howard_{size}_{overlap}', metadata={'hnsw:space': 'cosine'}, embedding_function=None)
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(MODEL, device='cpu')
        return self._model

    def build(self):
        vectors = self.model.encode([c['text'] for c in self.chunks],
                                    normalize_embeddings=True, show_progress_bar=False).tolist()
        # Upsert before removing obsolete IDs; a successful rebuild reflects changed/deleted files.
        self.collection.upsert(ids=[c['id'] for c in self.chunks], embeddings=vectors,
                               documents=[c['text'] for c in self.chunks],
                               metadatas=[c['metadata'] for c in self.chunks])
        current = {c['id'] for c in self.chunks}
        stale = [i for i in self.collection.get()['ids'] if i not in current]
        if stale:
            self.collection.delete(ids=stale)
        self.collection.modify(metadata={'signature': self.signature, 'model': MODEL})
        return len(self.chunks)

    def check_index(self):
        if (self.collection.metadata or {}).get('signature') != self.signature:
            raise ValueError('Index missing or stale. Run: python cli.py build')

    def search(self, query, mode='hybrid', source_type='all', k=4):
        query = query.strip()
        if not query:
            raise ValueError('Enter a question.')
        if mode not in {'semantic', 'bm25', 'hybrid'}:
            raise ValueError('Unknown retrieval mode.')
        if source_type not in {'all', 'official', 'student'}:
            raise ValueError('Unknown source filter.')
        if k < 1:
            raise ValueError('k must be positive.')
        self.check_index()
        candidates = [c for c in self.chunks if source_type == 'all' or c['metadata']['source_type'] == source_type]
        if not candidates:
            return []
        limit = min(max(12, k), len(candidates))
        vector, keyword = [], []
        distances, bm_scores = {}, {}
        if mode != 'bm25':
            args = {} if source_type == 'all' else {'where': {'source_type': source_type}}
            result = self.collection.query(query_embeddings=self.model.encode([query], normalize_embeddings=True).tolist(),
                                           n_results=limit, include=['distances'], **args)
            vector = result['ids'][0]
            distances = dict(zip(vector, result['distances'][0]))
        if mode != 'semantic':
            from rank_bm25 import BM25Okapi
            scores = BM25Okapi([tokens(c['text']) for c in candidates]).get_scores(tokens(query))
            bm_scores = {c['id']: float(s) for c, s in zip(candidates, scores)}
            keyword = sorted((i for i, s in bm_scores.items() if s > 0), key=lambda i: (-bm_scores[i], i))[:limit]
        scores = {}
        if mode == 'semantic':
            scores = {i: 1 - distances[i] for i in vector}
        elif mode == 'bm25':
            scores = {i: bm_scores[i] for i in keyword}
        else:
            for ranking in [vector, keyword]:
                for rank, i in enumerate(ranking, 1):
                    scores[i] = scores.get(i, 0) + 1 / (60 + rank)
        by_id = {c['id']: c for c in candidates}
        ranked = sorted(scores, key=lambda i: (-scores[i], i))[:k]
        return [{**by_id[i], 'score': scores[i], 'cosine_distance': distances.get(i),
                 'bm25_score': bm_scores.get(i), 'mode': mode} for i in ranked]
