from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "Web Engine", desc = "Enables you to search and navigate the web")
class WebTool(Tool):
    search_endpoint = 'https://stract.com/beta/api/search'

    headers = {
        'Content-type': 'application/json'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = 'Search the web', enabled = True)
    @method_arg(name = 'query', type = str, desc = 'Query to pass to the web search engine')
    def search(self, query, **kwargs):
        # TODO:  Support multiple search providers
        data = json.dumps({"query": query})

        response = requests.post(self.search_endpoint, headers = self.headers, data = data).json()

        results = []

        for webpage in response["webpages"]:
            content = ""

            for fragment in webpage['snippet']['text']['fragments']:
                content += fragment['text']

            results.append({"title": webpage['title'], "snippet": content})

        return results

    @tool_method(desc = 'Render a webpage')
    @method_arg(name = 'site_uri', type = str, desc = 'URL of the webpage that should be rendered')
    @method_arg(name = 'skip_certs', type = bool, desc = 'Whether or not we should accept expired TLS certificates')
    def render(self, **kwargs): pass
        # TODO:  Render the page elements (CSS, optionally JS, etc) maybe with Selenium?

    @tool_method(desc = 'read')
    @method_arg(name = 'site_uri', type = str, desc = 'Read the text content of a webpage')
    @method_arg(name = 'skip_certs', type = bool, desc = 'Whether or not we should accept expired TLS certificates')
    def read(self, site_uri, **kwargs):
        response = requests.get(site_uri, headers = self.headers)

        doc = pandoc.read(response.text, format = "html")
        md = f'```{pandoc.write(doc, format = "markdown")}```'

        return md

    @tool_method(desc = 'Download a file from the internet')
    @method_arg(name = 'file_uri', type = str, desc = 'URL we should download a file from')
    @method_arg(name = 'file_name', type = str, desc = 'Name the downloaded file should be saved as')
    def download(self, **kwargs): pass