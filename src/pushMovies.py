import json
import os
# import requests

from coveopush import CoveoPush
from coveopush import Document

# Map JSON key to Coveo Source's field name
keyMap = {
    "movieTitle": "movietitle",
    "year": "releaseyear",
    "rated": "rated",
    "runtimeStr": "runtimestr",
    "runtime": "runtime",
    "genre": "genre",
    "rating": "rating",
    "posterUri": "posteruri",
    "summary": "summary",
    "synopsis": "synopsis",
    "director": "director",
    "writer": "writers",
    "stars": "stars",
    "trivia": "trivia",
    "budget": "productionbudget",
}


def main():
    src_id = "bkostiukcoveocomromantictyrannosaurus17d2itb9-uqftl4i53w5ixsp6pjkshrsfjm"
    org_id = "bkostiukcoveocomromantictyrannosaurus17d2itb9"
    api_key = os.environ["IMDB_SOURCE_API_KEY"]

    push = CoveoPush.Push(src_id, org_id, api_key)
    movies_file_name = "./imdb_items.json"
    push.Start()
    with open(movies_file_name) as f:
        movies_object = json.load(f)
        for movie in movies_object["movies"]:
            doc = Document(movie["documentId"])
            doc.SetData(movie["documentId"])  # TODO: use valid data here
            for key, field_name in keyMap.items():
                doc.AddMetadata(field_name, movie[key])
            push.Add(doc)
    push.End()


if __name__ == '__main__':
    main()
