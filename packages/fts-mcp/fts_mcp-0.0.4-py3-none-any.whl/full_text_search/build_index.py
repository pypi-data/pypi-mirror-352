# this file takes jsonl of texts and turns it into "enriched" jsonl with keywords and summaries and stuff
from pathlib import Path

import dotenv
import pandas as pd
from lm_deluge import Conversation, LLMClient
from lm_deluge.util.json import try_load_json


async def enrich_texts(document_name: str, texts: list[str]):
    dotenv.load_dotenv()
    client = LLMClient.basic("gpt-4.1-mini", max_tokens_per_minute=1_000_000)

    prompt = (
        f"Given a section from the {document_name}, provide the following metadata as JSON, with "
        "`keywords` and `description` keys as follows:\n\n"
        " - `keywords` list[str]: A list of as many keywords/keyphrases as you can think of that someone "
        "might search for where the section would be relevant. The keywords/phrases do NOT have to occur "
        "in the section, they can be semantic matches, synonyms, etc. "
        "However, they should be specific to the section, not "
        f"keywords that would apply to literally any section of the {document_name}.\n"
        " - `description` str: A summary/overview of what the section says, including any key requirements or rules. "
        "Be mindful of your tendency to make overlong summaries, and remember that the goal is to provide a SHORT "
        "overview of the section. A long summary is pointless because you may as well just read the original.\n\n"
        f"Here is the {document_name} section:\n\n```\n<< SECTION >>\n```"
        "\n\nNow provide your JSON response, no prelude or commentary needed."
    )

    prompts = [
        Conversation.user(prompt.replace("<< SECTION >>", text)) for text in texts
    ]

    resps = await client.process_prompts_async(prompts)
    jsons = [try_load_json(x.completion) if x and x.completion else None for x in resps]

    return jsons


async def enrich_jsonl(document_name: str, in_file: Path | str, out_file: Path | str):
    df = pd.read_json(in_file, orient="records", lines=True)
    jsons = await enrich_texts(document_name, df["text"].to_list())
    normalized = pd.json_normalize(jsons)  # type: ignore

    combined = (
        pd.concat(
            [df.reset_index(drop=True), normalized.reset_index(drop=True)],
            ignore_index=True,
            axis=1,
        )
        .dropna()
        .reset_index(drop=True)
    )

    print("sample combined row:", combined.to_dict(orient="records")[0])
    combined.columns = ["text", "keywords", "summary"]
    combined["title"] = combined["text"].apply(lambda x: x.split("\n")[0])
    combined["id"] = combined.index.astype(str)
    combined = combined[["id", "title", "summary", "text", "keywords"]]
    combined["keywords"] = combined["keywords"].apply(lambda x: [k.lower() for k in x])  # type: ignore

    combined.to_json(str(out_file), orient="records", lines=True)
