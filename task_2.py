import string

from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

import matplotlib.pyplot as plt
import requests


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return None


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text, search_words=None):
    text = remove_punctuation(text)
    words = text.split()

    if search_words:
        words = [word for word in words if word in search_words]

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(result, n=10):
    top_words = sorted(result.items(), key=lambda x: x[1], reverse=True)[:n]
    plt.figure(figsize=(10, 6))
    plt.barh(
        [word[0] for word in top_words],
        [word[1] for word in top_words],
        color="skyblue",
    )
    plt.xlabel("Frequency")
    plt.ylabel("Word")
    plt.title(f"Top {n} Most Frequent Words")
    plt.gca().invert_yaxis()
    plt.show()


if __name__ == "__main__":
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    text = get_text(url)

    if text:
        result = map_reduce(text)
        print("Text is successfully loaded from url: ", url)
        visualize_top_words(result)

    else:
        print("Failed to get text from url: ", url)
