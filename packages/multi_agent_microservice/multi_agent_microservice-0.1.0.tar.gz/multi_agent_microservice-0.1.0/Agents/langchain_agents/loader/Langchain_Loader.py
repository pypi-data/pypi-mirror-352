from langchain_community.document_loaders import TextLoader


def text_file_loader():
    loader = TextLoader("input.txt")
    text_documents = loader.load()
    print(text_documents)
    print(type(text_documents))


def pdf_file_loader():
    pass


def web_loader():
    pass


def axis_loader():
    from langchain_community.document_loaders import ArxivLoader
    arix_loader = ArxivLoader(query="1706.03762", load_max_docs=2).load()
    return arix_loader


response = axis_loader()
print(response)
