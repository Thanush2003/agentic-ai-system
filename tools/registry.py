from tools.rag_tool_wrapper import (
    rag_tool
)

from tools.calculator_tool import (
    calculator_tool
)

from tools.web_search_tool import (
    web_search_tool
)

from tools.summarize_tool import (
    summarize_tool
)


TOOLS = [
    rag_tool,
    calculator_tool,
    web_search_tool,
    summarize_tool
]