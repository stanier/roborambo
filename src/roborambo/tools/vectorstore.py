from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

import chromadb

@tool_class(name = "Vector Store", desc = "")
class VectorStoreTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.client = chromadb.Client()
    
    @tool_method(desc = 'Search the vector store for a given query')
    @method_arg(name = 'query', type = str, desc = 'Query to search for')
    def search(self, **kwargs):
        results = collection.query(
            query_texts = [kwargs['query']],
            n_results = kwargs['results'],
        )

        return results

    @tool_method(desc = 'Embed a piece of information into the vector store')
    @method_arg(name = 'content', type = str, desc = 'Text content that should be embedded in the vector store')
    @method_arg(name = 'results', type = int, desc = 'Number of results to give back')
    def embed_note(self, **kwargs):
        collection.add(
            documents = [kwargs['content']],
            metadatas = [{"source": options["NAME"], "timestamp": datetime.now()}],
            ids = [f"note{int(time.time())}"],
        )
