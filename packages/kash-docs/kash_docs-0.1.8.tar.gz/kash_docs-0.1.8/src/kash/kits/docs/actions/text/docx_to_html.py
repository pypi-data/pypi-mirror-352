from kash.exec import kash_action
from kash.exec.preconditions import is_docx_resource
from kash.kits.docs.doc_formats import docx_convert
from kash.model import Format, Item, ItemType


@kash_action(precondition=is_docx_resource)
def docx_to_html(item: Item) -> Item:
    """
    Convert a docx file to HTML using MarkItDown/Mammoth. See
    `docx_to_md` to convert docx directly to Markdown.
    """

    result = docx_convert.docx_to_md(item.absolute_path())

    return item.derived_copy(
        type=ItemType.doc,
        format=Format.html,
        title=result.title or item.pick_title(pull_body_heading=True),
        body=result.raw_html,
    )
