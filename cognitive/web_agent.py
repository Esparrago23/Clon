try:
    from ddgs import DDGS
    ddg_available = True
except ImportError:
    ddg_available = False

def buscar_en_internet(query: str, max_resultados: int = 3) -> str:
    """
    Realiza una búsqueda silenciosa en internet usando DuckDuckGo.
    Devuelve un texto formateado con los resultados para inyectarlos en el prompt del LLM.
    """
    print(f" 🔍 [WEB_AGENT] Investigando en internet: '{query}'...")
    
    if not ddg_available:
        print(" [WEB-WARNING] Librería 'ddgs' no detectada. Retornando vacío.")
        return "No pude buscar en internet porque falta la librería (pip install ddgs)"

    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=max_resultados))
            
        if not resultados:
            return f"Búsqueda web sin resultados para: {query}"
            
        contexto_web = "Resultados de búsqueda web en tiempo real:\n"
        for i, res in enumerate(resultados):
            contexto_web += f"[{i+1}] {res.get('title', '')}: {res.get('body', '')}\n"
            
        print(" 🌐 [WEB_AGENT] Información encontrada y lista para inyectar.")
        return contexto_web
        
    except Exception as e:
        print(f" ❌ [WEB-ERROR] Falló la búsqueda: {str(e)}")
        return "Error al conectarse a internet."
