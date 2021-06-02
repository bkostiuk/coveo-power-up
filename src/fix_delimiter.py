import os
import json

from push_movies import get_dataset_files
from fetch_movie_json import write_to_json_file

def fix_delimiter(old: str, new: str):
    for movie_json in get_dataset_files():
        for key in movie_json:
            if type(movie_json[key]) == str and key in ('genre', 'director', 'writer', 'stars', 'languages'):
                movie_json[key] = movie_json[key].replace(old, new)
        print("Replaced " + movie_json['movieTitle'])
        write_to_json_file(movie_json['movieTitle'], movie_json)
    
def main():
    fix_delimiter(',', ';')

if __name__ == '__main__':
    main()