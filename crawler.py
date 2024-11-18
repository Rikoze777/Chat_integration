from llama_index.readers.web import FireCrawlWebReader
from environs import Env


async def parse_api(api_url: str) -> str:
    env = Env()
    env.read_env()
    FIRECRAWL_TOKEN = env.str("FIRECRAWL_TOKEN")


    firecrawl_reader = FireCrawlWebReader(
        api_key=FIRECRAWL_TOKEN,
        mode="scrape",
    )

    documents = firecrawl_reader.load_data(url=api_url)
    parsed_content = []
    if isinstance(documents, list):
        for doc in documents:
            if hasattr(doc, 'text'):
                parsed_content.append(doc.text)
            else:
                print("В документе не найден атрибут «текст».")
    else:
        print("Неожиданный формат документов:", documents)
    return str(parsed_content)