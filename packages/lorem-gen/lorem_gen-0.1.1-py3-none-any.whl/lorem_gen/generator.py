"""
generator.py

Generate Lorem Ipsum text based on user-specified amounts.
"""
import argparse
import random
import textwrap

# A basic Lorem Ipsum word list to sample from
LOREM_WORDS = ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua".split())

# A basic Lorem Ipsum sentence template
BASE_SENTENCES = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
]

class LoremGenerator:
    """Generate Lorem Ipsum text."""
    def __init__(self, words: int = 0, sentences: int = 0, paragraphs: int = 0):
        self.words = words
        self.sentences = sentences
        self.paragraphs = paragraphs

    def generate_words(self, count: int) -> str:
        """Generate a string containing `count` Lorem Ipsum words."""
        result = []
        for i in range(count):
            word = random.choice(LOREM_WORDS)
            # Capitalize the first word
            if i == 0:
                word = word.capitalize()
            result.append(word)
        text = " ".join(result) + "."
        return text

    def generate_sentences(self, count: int) -> str:
        """Generate a string containing `count` Lorem Ipsum sentences."""
        # Cycle through the base sentences, randomizing order
        sentences = []
        for i in range(count):
            sentence = random.choice(BASE_SENTENCES)
            sentences.append(sentence)
        return " ".join(sentences)

    def generate_paragraphs(self, count: int) -> str:
        """Generate a string containing `count` Lorem Ipsum paragraphs."""
        paragraphs = []
        for _ in range(count):
            # Each paragraph consists of a random number of sentences (3 to 6)
            num_sentences = random.randint(3, 6)
            paragraph = self.generate_sentences(num_sentences)
            paragraphs.append(paragraph)
        return "\n\n".join(paragraphs)

    def generate(self) -> str:
        """Generate text based on initialization parameters."""
        if self.paragraphs > 0:
            return self.generate_paragraphs(self.paragraphs)
        elif self.sentences > 0:
            return self.generate_sentences(self.sentences)
        elif self.words > 0:
            return self.generate_words(self.words)
        else:
            # Default: generate one paragraph
            return self.generate_paragraphs(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Lorem Ipsum text."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--words", 
        type=int, 
        help="Number of words to generate (e.g., --words 50)."
    )
    group.add_argument(
        "--sentences", 
        type=int, 
        help="Number of sentences to generate (e.g., --sentences 5)."
    )
    group.add_argument(
        "--paragraphs", 
        type=int, 
        help="Number of paragraphs to generate (e.g., --paragraphs 2)."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    words = args.words or 0
    sentences = args.sentences or 0
    paragraphs = args.paragraphs or 0

    generator = LoremGenerator(words=words, sentences=sentences, paragraphs=paragraphs)
    generated_text = generator.generate()

    # Wrap paragraphs at 80 characters for readability
    if paragraphs > 0:
        for para in generated_text.split("\n\n"):
            print(textwrap.fill(para, width=80))
            print()
    else:
        print(textwrap.fill(generated_text, width=80))


if __name__ == "__main__":
    main()
