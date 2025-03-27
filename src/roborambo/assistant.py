import os

from .chains import RamboChain

from nothingburger.model_loader import initializeModel

import roborambo.tools as tools
import nothingburger.templates as templates

from . import DEFAULTS

templates.templates.update({
    'rambo_instruct_chat':
"""{% extends \"alpaca_instruct_input\" %}
{% block input %}{% for message in memory.messages %}{{message.role}}: {{message.content}}
{% endfor %}{{user_prefix}}: {{inp}}{% endblock %}
{% block response %}{{assistant_prefix}}: {% endblock %}""",
    'rambo_instruct_chat_timestamped':
"""{% extends \"alpaca_instruct_chat\" %}
{% block input %}{% for message in memory.messages %}[{{message.timestamp.strftime('%a %d %b %Y, %Ih%Mm%Ss')}}] {{message.role}}: {{message.content}}
{% endfor %}[Now] {{user_prefix}}: {{inp}}{% endblock %}
{% block response %}[Now] {{assistant_prefix}}: {% endblock %}""",
})

class Assistant:
    def __init__(self, conf, **kwargs):
        tools_concat = ""

        self.active_tools = {}
    
        for tool in conf['tools']['enabled']:
            self.active_tools[tool] = tools.available_tools[tool]()

            funcs_concat = ""
            for func in self.active_tools[tool].methods: # functions are required
                args_concat = ""
                for arg in self.active_tools[tool].methods[func].get('arguments', {}): # arguments are optional
                    args_concat = "{}\n{}".format(args_concat, conf['instructions']['args_entry_template'].format(
                        arg_slug = arg,
                        arg_type = self.active_tools[tool].methods[func]['arguments'][arg]['type'],
                        arg_desc = self.active_tools[tool].methods[func]['arguments'][arg]['description'],
                    ))
                funcs_concat = "{}{}".format(funcs_concat, conf['instructions']['func_entry_template'].format(
                    func_slug = func,
                    func_desc = self.active_tools[tool].methods[func]['description'],
                    tool_slug = tool,
                    #arg_entries = args_concat,
                    arg_entries = "",
                ))
            tools_concat = "{}{}".format(tools_concat, conf['instructions']['tool_entry_template'].format(
                tool_name = self.active_tools[tool].name,
                tool_desc = self.active_tools[tool].description,
                func_entries = funcs_concat,
                #func_entries = "",
            ))

        self.chain = RamboChain(
            model               = initializeModel(os.path.expandvars("{}/{}".format(
                conf.get('tunables', {}).get('model_library', DEFAULTS["MODEL_LIBRARY"]),
                conf.get('tunables', {}).get('model_file', DEFAULTS["MODEL_FILE"]),
            ))),
            instruction         = conf['instructions']['instruction'].format(**(conf['instructions']) | {
                'scene_instructions'    : conf['instructions']['scene_instructions'].format(**conf['instructions']),
                'timestamp_instructions': conf['instructions']['timestamp_instructions'].format(**conf['instructions']),
                'tool_instructions'     : conf['instructions']['tool_instructions'].format(tools = tools_concat),
                'name'                  : conf['name'],
                'persona'               : conf['instructions']['persona'].format(name = conf['name'], **conf['instructions']),
            }),
            template            = templates.getTemplate("rambo_instruct_chat"),
            debug               = kwargs.get('debug', False),
            stream              = False,
            assistant_prefix    = conf['name'],
            cutoff              = conf['cutoff'],
        )