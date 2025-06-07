movie_item_schema_example = {
    "id": 1,
    "name": "The Matrix",
    "year": 1999,
    "imdb": 8.7,
    "price": 120.0,
    "description": "A computer hacker learns about the true nature of his reality.",
}

movie_list_response_schema_example = {
    "movies": [movie_item_schema_example],
    "prev_page": None,
    "next_page": "/theater/movies/?page=2&per_page=1",
    "total_pages": 10,
    "total_items": 10,
}

movie_create_schema_example = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "name": "The Matrix",
    "year": 1999,
    "time": 136,
    "imdb": 8.7,
    "votes": 1700000,
    "meta_score": 73.0,
    "gross": 463517383.0,
    "description": "A computer hacker learns about the true nature of his reality.",
    "price": 120.0,
    "certification_id": 1,
    "genres": ["Action", "Sci-Fi"],
    "stars": ["Keanu Reeves", "Laurence Fishburne"],
    "directors": ["Lana Wachowski", "Lilly Wachowski"],
}

movie_detail_schema_example = {
    "id": 1,
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "name": "The Matrix",
    "year": 1999,
    "time": 136,
    "imdb": 8.7,
    "votes": 1700000,
    "meta_score": 73.0,
    "gross": 463517383.0,
    "description": "A computer hacker learns about the true nature of his reality.",
    "price": 120.0,
    "certification_id": 1,
    "certification": {"id": 1, "name": "R"},
    "genres": [{"id": 1, "name": "Action"}, {"id": 2, "name": "Sci-Fi"}],
    "stars": [
        {"id": 1, "name": "Keanu Reeves"},
        {"id": 2, "name": "Laurence Fishburne"},
    ],
    "directors": [
        {"id": 1, "name": "Lana Wachowski"},
        {"id": 2, "name": "Lilly Wachowski"},
    ],
}

movie_update_schema_example = {
    "name": "The Matrix Reloaded",
    "year": 2003,
    "time": 138,
    "imdb": 7.2,
    "votes": 600000,
    "meta_score": 62.0,
    "gross": 427343298.0,
    "description": "The Matrix saga continues.",
    "price": 130.0,
    "certification_id": 1,
    "genres": ["Action", "Sci-Fi"],
    "stars": ["Keanu Reeves", "Carrie-Anne Moss"],
    "directors": ["Lana Wachowski", "Lilly Wachowski"],
}
