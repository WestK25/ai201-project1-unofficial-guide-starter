"""Build, inspect, retrieve, and ask without starting the interface."""
import argparse
import json
from pipeline import Retriever, load_documents, chunk_documents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'chunks', 'retrieve', 'ask'])
    parser.add_argument('question', nargs='?', default='')
    parser.add_argument('--mode', choices=['semantic', 'bm25', 'hybrid'], default='hybrid')
    parser.add_argument('--source-type', choices=['all', 'official', 'student'], default='all')
    args = parser.parse_args()
    try:
        if args.command == 'chunks':
            print(json.dumps(chunk_documents(load_documents()), indent=2, ensure_ascii=False))
            return
        retriever = Retriever()
        if args.command == 'build':
            print(f'Indexed {retriever.build()} chunks.')
        elif args.command == 'retrieve':
            print(json.dumps(retriever.search(args.question, args.mode, args.source_type), indent=2, ensure_ascii=False))
        else:
            from generation import answer, sources_markdown
            result = answer(retriever, args.question, mode=args.mode, source_type=args.source_type)
            print(result['answer'] + '\n\nRetrieved sources:\n' + sources_markdown(result['results']))
            if result['status'] != 'ok':
                raise SystemExit(1)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
