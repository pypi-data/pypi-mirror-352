import re

from markdownify import markdownify


def remove_attributes(html_string: str):
    def remove_attrs(match):
        tag_name = match.group(1)
        return f"<{tag_name}>"

    pattern = r"<([^>\s]+)[^>]*>"
    return re.sub(pattern, remove_attrs, html_string)


def html_to_markdown(html_string: str):
    md = markdownify(html_string)

    # the replace stuff we don't want
    if "Back To TOC" in md:
        md = md.split("Back To TOC")[1]

    md = md.replace("![]()", "")

    md = md.replace("\n---\n", "\n")

    md = re.sub(r"\n{3,}", "\n\n", md)

    return md


async def remove_boilerplate(markdown: str):
    from lm_deluge import LLMClient

    prompt = (
        "Below is some Markdown/text saved from a webpage. "
        "Make your best attempt at removing any boilerplate, leaving only the text "
        "that you think is the main content area. Boilerplate includes navigation menus, "
        "copyright notices, privacy policy links, stuff like that. Everything but the main content. "
        "If there doesn't appear to be any main content or the page is empty / all boilerplace, "
        "you may return an empty string. Do not add any prelude or commentary, just return the cleaned page.\n\n"
    )

    client = LLMClient(max_new_tokens=10_000)
    res = await client.process_prompts_async([prompt + markdown], show_progress=False)

    return res[0].completion  # type: ignore


async def read_html(html_string: str):
    return await remove_boilerplate(markdownify(html_string))
