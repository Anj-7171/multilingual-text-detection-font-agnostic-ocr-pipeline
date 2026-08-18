def identify_script(text):
    """
    Identify the dominant writing script in a text string
    using Unicode character ranges.
    """

    counts = {
        "english": 0,
        "hindi": 0,
        "tamil": 0,
        "other": 0,
    }

    for char in text:
        code = ord(char)

        # Basic Latin
        if 0x0041 <= code <= 0x007A:
            counts["english"] += 1

        # Devanagari
        elif 0x0900 <= code <= 0x097F:
            counts["hindi"] += 1

        # Tamil
        elif 0x0B80 <= code <= 0x0BFF:
            counts["tamil"] += 1

        elif char.isalpha():
            counts["other"] += 1

    if not any(counts.values()):
        return "unknown"

    return max(counts, key=counts.get)


if __name__ == "__main__":
    examples = [
        "Hello World",
        "नमस्ते दुनिया",
        "வணக்கம் உலகம்",
    ]

    for text in examples:
        script = identify_script(text)
        print(f"{text} -> {script}")