#!/usr/bin/env python3

# Standard libraries
from re import sub

# Namespaces class
class Namespaces:

    # Capitalize
    @staticmethod
    def capitalize(text: str, words: bool = False) -> str:

        # Capitalize words
        if words:
            return ' '.join(
                Namespaces.capitalize(word, words=False) for word in text.split())

        # Capitalize text
        return f'{text[:1].capitalize()}{text[1:]}'

    # Describe
    @staticmethod
    def describe(
        name: str,
        description: str = '',
    ) -> str:

        # Use description
        if description:
            return description

        # Adapt name
        return Namespaces.capitalize(sub(r'[-_]', ' ', name), words=True)
