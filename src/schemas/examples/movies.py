genre_schema_example = {
    "id": 1,
    "genre": "Comedy"
}

star_schema_example = {
    "id": 1,
    "name": "JimmyFallon"
}

star_detail_schema_example = {
    "id": 1,
    "name": "JimmyFallon",
    "movies": ["Die Hard", "Pulp Fiction"]
}

director_schema_example = {
    "id": 1,
    "name": "Christopher Nolan"
}

director_detail_schema_example = {
    "id": 1,
    "name": "Christopher Nolan",
    "movies": ["Pulp Fiction", "Kill Bill"]
}

certification_schema_example = {
    "id": 1,
    "name": "NC-17"
}

movie_schema_example = {
    "id": 1,
    "name": "Inception",
    "year": 1999,
    "imdb": 8.8,
    "price": "12.99",
    "genres": [
        {
            "id": 1,
            "name": "Sci-Fi"
        },
        {
            "id": 2,
            "name": "Action"
        }
    ]
}

movie_detail_schema_example = {
    "id": 1,
    "name": "Inception",
    "year": 2010,
    "imdb": 8.8,
    "price": "12.99",
    "description": "A mind-bending thriller by Christopher Nolan.",
    "certification": {
        "id": 1,
        "name": "PG-13"
    },
    "genres": [
        {
            "id": 1,
            "name": "Sci-Fi"
        },
        {
            "id": 2,
            "name": "Action"
        }
    ],
    "stars": [
        {
            "id": 1,
            "name": "Leonardo DiCaprio"
        }
    ],
    "directors": [
        {
            "id": 1, "name": "Christopher Nolan"
        }
    ]
}

movie_create_schema_example = {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Inception",
    "year": 2010,
    "time": 65,
    "imdb": 8.8,
    "votes": 2300000,
    "meta_score": 74.0,
    "gross": 836.8,
    "description": "A mind-bending thriller by Christopher Nolan.",
    "price": "12.99",
    "certification_id": "2",
    "genres": ["Sci-Fi", "Action"],
    "stars": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"],
    "directors": ["Christopher Nolan", "Quentin Tarantino"]
}

movie_update_schema_example = {
    "name": "Inception",
    "year": 2012,
    "imdb": 8.8,
    "price": "12.99",
    "certification_id": "2",
}
