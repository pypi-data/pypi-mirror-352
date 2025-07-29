import re
from typing import Mapping
import os
from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Render
from mdit_py_plugins.dollarmath import dollarmath_plugin


def update_mdit(mdit: MarkdownIt) -> None:
    mdit.use(dollarmath_plugin, double_inline=True, allow_blank_lines=True)


def format_math_block_content(content):
    # strip and remove blank lines
    content = re.sub(r"\n+", "\n", content.strip(), re.DOTALL)
    print(os.environ.get("MDFORMAT_DOLLARMATH_USE_ALIGNED", False))
    if os.environ.get("MDFORMAT_DOLLARMATH_USE_ALIGNED", False):
        # for engines that do not support aligned in math mode
        content = re.sub(r"\\(begin|end){align\*?}", r"\\\1{aligned}", content)

    # remove additional white spaces in the end of the line
    content = re.sub(r"\s+$", "", content)

    return f"\n{content}\n"


def _math_inline_renderer(node: RenderTreeNode, context: RenderContext) -> str:
    return f"${node.content}$"


def _math_block_renderer(node: RenderTreeNode, context: RenderContext) -> str:
    return f"$${format_math_block_content(node.content)}$$"


def _hardbreak_renderer(node: RenderTreeNode, context: RenderContext) -> str:
    if node.next_sibling.type == "math_inline_double":
        return "\n"
    else:
        return "\\\n"


def _math_inline_double_renderer(node: RenderTreeNode, context: RenderContext) -> str:
    # formats the inline doubles as math blocks
    prev_sib = node.previous_sibling
    prefix = ""
    if prev_sib:
        suffix = prefix = "\n"
        if prev_sib.type not in ["softbreak", "hardbreak"]:
            prefix += "\n"
            suffix += "\n"
    else:
        suffix = "\n\n"

    return f"{prefix}$${format_math_block_content(node.content.strip())}$${suffix}"


def _math_block_label_renderer(node: RenderTreeNode, context: RenderContext) -> str:
    return f"$${format_math_block_content(node.content)}$$ ({node.info})"


# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {
    "math_inline": _math_inline_renderer,
    "math_inline_double": _math_inline_double_renderer,
    "math_block_label": _math_block_label_renderer,
    "math_block": _math_block_renderer,
    "hardbreak": _hardbreak_renderer,
}
