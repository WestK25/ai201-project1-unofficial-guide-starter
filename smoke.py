"""Integration checks against a built index and a local Gradio server."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen
from pipeline import Retriever, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate', action='store_true', help='Test real cited answers and session memory through HTTP')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'evidence')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    r = Retriever(); r.check_index()
    first = r.collection.count(); second = r.build()
    assert first == second == r.collection.count()
    results['idempotent_rebuild'] = f'passed: {first} chunks'
    for kind in ['official','student']:
        rows = r.search('Howard housing', source_type=kind)
        assert rows and all(row['metadata']['source_type'] == kind for row in rows)
    results['metadata_filter'] = 'passed'
    for query in ['', '  ']:
        try:
            r.search(query)
            raise AssertionError('Empty question accepted')
        except ValueError:
            pass
    results['empty_query'] = 'passed'
    from app import create_app, respond
    state, chat, message, details = respond('', [], 'hybrid', 'all')
    assert not state and 'Enter a question' in message
    results['interface_empty_query'] = 'passed'
    demo = create_app()
    try:
        _, url, _ = demo.launch(server_name='127.0.0.1', server_port=7861,
                               prevent_thread_lock=True, share=False, quiet=True)
        with urlopen(url, timeout=15) as response:
            assert response.status == 200
        results['gradio_http'] = 'passed: HTTP 200 on localhost'
        from gradio_client import Client
        client = Client(url, verbose=False)
        config = client.config
        assert any(c['type'] == 'textbox' for c in config['components'])
        results['gradio_client_config'] = 'passed'
        response = client.predict('', 'hybrid', 'all', api_name='/ask')
        assert 'Enter a question' in str(response)
        results['gradio_callback'] = 'passed: empty-question validation through HTTP API'
        if args.generate:
            transcript = []
            for question in ['What do students say about College Hall South?', 'How does that compare with Drew?']:
                import time
                time.sleep(15)
                chat, sources, details = client.predict(question, 'hybrid', 'student', api_name='/ask')
                assert chat and chat[-1]['role'] == 'assistant'
                content = chat[-1]['content']
                # Gradio 6 serializes message content as structured blocks.
                rendered = content if isinstance(content, str) else str(content)
                assert '[S' in rendered and 'Generation unavailable' not in rendered
                assert 'student' in sources
                if len(transcript):
                    assert 'College Hall South' in details and 'Drew' in details
                    assert len(chat) == 4
                transcript.append({'question': question, 'conversation': chat,
                                   'sources': sources, 'retrieval_details': details})
            (args.output_dir/'interface.json').write_text(json.dumps(transcript, indent=2))
            results['gradio_generation_and_memory'] = 'passed: two cited answers, student filter, four-message session, contextual follow-up through HTTP API'
    finally:
        demo.close()
    (args.output_dir/'smoke.json').write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
