"""Launch with python app.py; browser-session memory is held by Gradio State."""
from functools import lru_cache
import gradio as gr
from pipeline import Retriever
from generation import answer, sources_markdown


@lru_cache(maxsize=1)
def get_retriever():
    return Retriever()


def respond(question, history, mode, source_type):
    history = history or []
    try:
        result = answer(get_retriever(), question, history, mode, source_type)
    except (ValueError, OSError) as exc:
        return history, conversation(history), str(exc), ''
    except Exception as exc:
        return history, conversation(history), f'Retrieval unavailable ({type(exc).__name__}). Run python cli.py build and check dependencies.', ''
    new_history = (history + [{'question': question, 'answer': result['answer']}])[-6:]
    details = '\n\n'.join(f"[S{i}] score={r['score']:.5f}; cosine distance={r['cosine_distance']}; BM25={r['bm25_score']}\n{r['text']}" for i, r in enumerate(result['results'], 1))
    return new_history, conversation(new_history), sources_markdown(result['results']), 'Retrieval query: ' + result['retrieval_query'] + '\n\n' + details


def conversation(history):
    return [{'role': role, 'content': turn[key]} for turn in history for role, key in [('user', 'question'), ('assistant', 'answer')]]


def create_app():
    with gr.Blocks(title='The Unofficial Guide to Howard University Student Life') as demo:
        gr.Markdown('# The Unofficial Guide to Howard University Student Life\nAsk about campus life. Official information and individual student experiences are labeled in the sources.')
        state = gr.State([])
        chat = gr.Chatbot(label='Conversation')
        question = gr.Textbox(label='Your question', placeholder='How often do Howard shuttles arrive?')
        with gr.Row():
            source_type = gr.Dropdown(['all', 'official', 'student'], value='all', label='Source type')
            mode = gr.Dropdown(['hybrid', 'semantic', 'bm25'], value='hybrid', label='Search method')
        with gr.Row():
            submit = gr.Button('Ask', variant='primary')
            clear = gr.Button('Clear conversation')
        sources = gr.Markdown(label='Retrieved sources')
        with gr.Accordion('Retrieved passages and search details', open=False):
            details = gr.Textbox(label='Evidence', lines=12)
        inputs, outputs = [question, state, mode, source_type], [state, chat, sources, details]
        submit.click(respond, inputs, outputs, api_name='ask')
        question.submit(respond, inputs, outputs)
        clear.click(lambda: ([], [], '', '', ''), outputs=[state, chat, sources, details, question])
    return demo


if __name__ == '__main__':
    create_app().launch(server_name='127.0.0.1', share=False)
