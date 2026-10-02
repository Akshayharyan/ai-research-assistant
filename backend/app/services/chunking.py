
def chunk_pages(pages, chunk_size=1000, overlap=200):
    chunks = []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    for page in pages:
        text = page["text"]
        page_number = page["page"]

        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            chunk_text = text[start:end]

            chunks.append({
                "page": page_number,
                "text": chunk_text
            })

            start += chunk_size - overlap

    return chunks