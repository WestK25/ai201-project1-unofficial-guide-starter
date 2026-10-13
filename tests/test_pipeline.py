import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pipeline import chunk_documents, load_documents
from generation import contextual_query, answer, REFUSAL


class PipelineTests(unittest.TestCase):
    def test_boundaries_coverage_and_stability(self):
        text = ''.join(chr(0x400 + i) for i in range(2001))
        doc = {'text': text, 'metadata': {'filename': 'example.txt'}}
        chunks = chunk_documents([doc])
        self.assertEqual(chunks, chunk_documents([doc]))
        self.assertEqual(chunks[0]['text'][-150:], chunks[1]['text'][:150])
        self.assertEqual(chunks[0]['text'] + ''.join(c['text'][150:] for c in chunks[1:]), text)
        self.assertEqual(len({c['id'] for c in chunks}), len(chunks))
        self.assertTrue(all(len(c['text']) <= 800 for c in chunks))
        self.assertEqual(len(chunk_documents([{'text': 'x'*800, 'metadata': {}}])), 1)
        for size, overlap in [(0, 0), (100, 100), (100, -1)]:
            with self.assertRaises(ValueError):
                chunk_documents([doc], size, overlap)

    def test_ingestion_and_placeholders(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p/'.hidden.txt').write_text('ignored')
            (p/'empty.txt').write_text('')
            (p/'todo.txt').write_text('STATUS: todo\nCONTENT:\nNot verified')
            with self.assertRaises(ValueError):
                load_documents(p)
            (p/'real.txt').write_text('SOURCE: Test\nACCESSED: 2026-09-29\nSOURCE TYPE: official\nTOPIC: housing\nCONTENT:\nHello   world\n next line')
            docs = load_documents(p)
            self.assertEqual(len(docs), 1)
            self.assertEqual(docs[0]['text'], 'Hello world next line')
            self.assertEqual(docs[0]['metadata']['source_url'], '')

    def test_real_corpus(self):
        docs = load_documents()
        self.assertGreaterEqual(len(docs), 10)
        self.assertEqual({d['metadata']['source_type'] for d in docs}, {'official', 'student'})
        self.assertTrue(all(d['metadata']['source_url'].startswith('https://') for d in docs))

    def test_memory_does_not_use_old_generated_facts(self):
        history = [{'question': 'What do students say about College Hall South?', 'answer': 'Invented fact'}]
        query = contextual_query('How does that compare with Drew?', history)
        self.assertIn('College Hall South', query)
        self.assertIn('Drew', query)
        self.assertNotIn('Invented fact', query)
        self.assertEqual(contextual_query('How often do shuttles arrive?', history), 'How often do shuttles arrive?')

    def test_empty_query_and_empty_results(self):
        class Empty:
            def search(self, *args):
                return []
        with self.assertRaises(ValueError):
            answer(Empty(), ' ')
        self.assertEqual(answer(Empty(), 'Question')['answer'], REFUSAL)

    def test_missing_key(self):
        class Found:
            def search(self, *args):
                return [{'text': 'something'}]
        with patch.dict(os.environ, {}, clear=True), patch('generation.load_dotenv'):
            self.assertEqual(answer(Found(), 'Question')['status'], 'unavailable')

class GenerationValidationTests(unittest.TestCase):
    def test_invalid_citation_rejected_and_valid_citation_retained(self):
        from types import SimpleNamespace
        row = {'text': 'A sourced claim.', 'metadata': {'source': 'Example', 'source_type': 'official'}}
        class Found:
            def search(self, *args):
                return [row]
        for text, expected in [('Claim [S99]', 'citation_rejected'), ('Uncited claim', 'citation_rejected'),
                               ('A sourced claim [S1]', 'ok'), ('Grouped [S1, S99]', 'citation_rejected'),
                               ('Grouped [S1, S1]', 'ok'), (REFUSAL, 'ok')]:
            completion = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])
            with patch.dict(os.environ, {'GROQ_API_KEY': 'unit-test-placeholder'}), patch('generation.load_dotenv'), patch('groq.Groq') as client:
                client.return_value.chat.completions.create.return_value = completion
                result = answer(Found(), 'Question')
                self.assertEqual(result['status'], expected)
                self.assertEqual(result['answer'], REFUSAL if expected == 'citation_rejected' else text)


if __name__ == '__main__':
    unittest.main()
