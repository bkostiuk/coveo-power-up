import json
import os
# import requests

from coveopush import CoveoPush
from coveopush import Document

# Map JSON key to Coveo Source's field name
KEY_MAP = {
    'uri': 'uri',
    'movieTitle': 'movietitle',
    'year': 'releaseyear',
    'rated': 'rated',
    'runtimeStr': 'runtimestr',
    'runtime': 'runtime',
    'genre': 'genre',
    'rating': 'rating',
    'posterUri': 'posteruri',
    'summary': 'summary',
    'synopsis': 'synopsis',
    'director': 'director',
    'writer': 'writers',
    'stars': 'stars',
    'trivia': 'trivia',
    'budget': 'productionbudget',
    'languages': 'language'
}

SRC_ID = 'bkostiukcoveocomromantictyrannosaurus17d2itb9-uqftl4i53w5ixsp6pjkshrsfjm'
ORG_ID = 'bkostiukcoveocomromantictyrannosaurus17d2itb9'
API_KEY = os.environ['IMDB_SOURCE_API_KEY']
DATASET_PATH = '../dataset/'  # Path to movie JSON objects


# Generator of movie JSON objects (stored in DATASET_PATH)
def get_dataset_files():
    for filename in os.listdir(DATASET_PATH):
        if filename.endswith('.json'):
            with open(os.path.join(DATASET_PATH, filename)) as f:
                movie = json.load(f)
                yield movie


def main():
    push = CoveoPush.Push(SRC_ID, ORG_ID, API_KEY)
    push.Start()

    failed_movies = []
    success_count = 0

    # Iterate though movies
    for movie_json in get_dataset_files():
        print("Pushing movie:", movie_json['movieTitle'])
        doc = Document(movie_json["uri"])  # use uri as document ID
        doc.SetData(movie_json["summary"])
        for key, val in movie_json.items():
            if key in KEY_MAP:
                doc.AddMetadata(KEY_MAP[key], val)
            else:
                print(f"\tKey {key} is not associated to a valid field.")
        try:
            push.Add(doc)
            print("\tSuccess")
            success_count += 1
        except:
            print("\tFailed")
            failed_movies.append(movie_json['movieTitle'])
    push.End()

    print(f"\nPushed: {success_count}")
    print(f"Failed: {len(failed_movies)}")
    for m in failed_movies:
        print(f"\t{m}")


if __name__ == '__main__':
    main()
