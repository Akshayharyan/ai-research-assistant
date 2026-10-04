
import re


def chunk_pages(pages, chunk_size=1000, overlap=200):
    chunks = []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    def split_long_text(text):
        # Split long text into sentences first.
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        pieces = []
        current = ""

        for sentence in sentences:
            if len(sentence) > chunk_size:
                if current:
                    pieces.append(current)
                    current = ""

                # Split exceptionally long sentences at word boundaries.
                words = sentence.split()
                part = ""

                for word in words:
                    candidate = part + " " + word if part else word

                    if len(candidate) <= chunk_size:
                        part = candidate
                    else:
                        if part:
                            pieces.append(part)

                        # A single word longer than the limit is rare.
                        if len(word) > chunk_size:
                            for i in range(0, len(word), chunk_size):
                                pieces.append(word[i:i + chunk_size])
                            part = ""
                        else:
                            part = word

                if part:
                    pieces.append(part)

                continue

            candidate = current + " " + sentence if current else sentence

            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    pieces.append(current)
                current = sentence

        if current:
            pieces.append(current)

        return pieces

    for page in pages:
        text = page["text"].strip()
        page_number = page["page"]

        if not text:
            continue

        # Separate paragraphs using blank lines.
        paragraphs = re.split(r"\n\s*\n", text)
        units = []

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            if len(paragraph) <= chunk_size:
                units.append(paragraph)
            else:
                units.extend(split_long_text(paragraph))

        current_units = []

        def join_units(items):
            return "\n\n".join(items)

        for unit in units:
            candidate_units = current_units + [unit]
            candidate = join_units(candidate_units)

            if len(candidate) <= chunk_size:
                current_units = candidate_units
                continue

            # Save the current chunk before starting another.
            if current_units:
                chunks.append({
                    "page": page_number,
                    "text": join_units(current_units)
                })

            # Reuse complete trailing units for overlap.
            carry = []
            carry_length = 0

            for previous_unit in reversed(current_units):
                extra_length = len(previous_unit) + (2 if carry else 0)

                if carry_length + extra_length > overlap:
                    break

                carry.insert(0, previous_unit)
                carry_length += extra_length

            # Never let overlap make the new chunk exceed the limit.
            while carry and len(join_units(carry + [unit])) > chunk_size:
                carry.pop(0)

            current_units = carry + [unit]

        if current_units:
            chunks.append({
                "page": page_number,
                "text": join_units(current_units)
            })

    return chunks