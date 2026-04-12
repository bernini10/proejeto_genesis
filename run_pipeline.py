import sys, json
from agents.graph import build_graph
from core.config import DEFAULT_THESIS

def main():
    thesis = DEFAULT_THESIS if len(sys.argv) < 2 else ' '.join(sys.argv[1:])
    print(f'🔬 Iniciando R&D para: {thesis}')
    app = build_graph()
    result = app.invoke({'thesis': thesis, 'status': 'start'})
    print('\n📊 RESULTADO DA VALIDACAO:')
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
