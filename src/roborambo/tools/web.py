import json
import requests
import pandoc
from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name="Web Engine", desc="Enables you to search and navigate the web")
class WebTool(Tool):
    search_endpoint = 'https://stract.com/beta/api/search'
    headers = {'Content-type': 'application/json'}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc='Search the web', enabled=True)
    @method_arg(name='query', type='str', desc='Query to pass to the web search engine')
    def search(self, query, **kwargs):
        data = json.dumps({"query": query})
        response = requests.post(self.search_endpoint, headers=self.headers, data=data).json()
        
        results = []
        for webpage in response["webpages"]:
            content = ""
            for fragment in webpage['snippet']['text']['fragments']:
                content += fragment['text']
            results.append({"title": webpage['title'], "snippet": content})
        
        return results

    @tool_method(desc='Read the text content of a webpage', enabled=True)
    @method_arg(name='site_uri', type='str', desc='URL of the webpage that should be rendered')
    def read(self, site_uri, **kwargs):
        response = requests.get(site_uri, headers=self.headers)
        doc = pandoc.read(response.text, format="html")
        md = f'```{pandoc.write(doc, format="markdown")}```'
        return md