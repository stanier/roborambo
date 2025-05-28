import os
from .chains import RamboChain
from nothingburger.model_loader import initializeModel
import roborambo.tools as tools
import nothingburger.templates as templates
from . import DEFAULTS

class Assistant:
    def __init__(self, conf, **kwargs):
        # Initialize tools
        self.active_tools = {}
        for tool in conf['tools']['enabled']:
            self.active_tools[tool] = tools.available_tools[tool]()

        # Initialize the model
        model = initializeModel(os.path.expandvars("{}/{}".format(
            conf.get('tunables', {}).get('model_library', DEFAULTS["MODEL_LIBRARY"]),
            conf.get('tunables', {}).get('model_file', DEFAULTS["MODEL_FILE"]),
        )))

        # Use simple chat template - no need for tool instructions since we use function calling
        template = templates.getTemplate("chat_with_context")
        
        # Simple system instruction without tool-specific text
        instruction_text = conf['instructions']['persona'].format(
            name=conf['name'], 
            **conf['instructions']
        )

        self.chain = RamboChain(
            model=model,
            instruction=instruction_text,
            template=template,
            debug=kwargs.get('debug', False),
            stream=False,
            assistant_prefix=conf['name'],
            cutoff=conf['cutoff'],
            active_tools=self.active_tools,
        )