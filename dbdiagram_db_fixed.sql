// ENUMS: використовуємо varchar, можливі значення вказані в коментарях

Table user_groups {
  id int [pk, increment, not null]
  name varchar(50) [not null, unique] // 'user', 'moderator', 'admin'
}

Table users {
  id int [pk, increment, not null]
  email varchar(255) [not null, unique]
  hashed_password varchar(255) [not null]
  is_active boolean [not null, default: false]
  created_at timestamp [not null, default: `now()`]
  updated_at timestamp [not null, default: `now()`]
  group_id int [not null, ref: > user_groups.id]
}

Table user_profiles {
  id int [pk, increment, not null]
  user_id int [not null, unique, ref: - users.id]
  first_name varchar(100)
  last_name varchar(100)
  avatar varchar(255)
  gender varchar(10) // 'man', 'woman'
  date_of_birth date
  info text
}

Table activation_tokens {
  id int [pk, increment, not null]
  user_id int [not null, ref: - users.id]
  token varchar(255) [not null, unique]
  expires_at timestamp [not null]
}

Table password_reset_tokens {
  id int [pk, increment, not null]
  user_id int [not null, ref: - users.id]
  token varchar(255) [not null, unique]
  expires_at timestamp [not null]
}

Table refresh_tokens {
  id int [pk, increment, not null]
  user_id int [not null, ref: > users.id]
  token varchar(255) [not null, unique]
  expires_at timestamp [not null]
}

Table genres {
  id int [pk, increment, not null]
  name varchar(100) [unique, not null]
}

Table stars {
  id int [pk, increment, not null]
  name varchar(100) [unique, not null]
}

Table directors {
  id int [pk, increment, not null]
  name varchar(100) [unique, not null]
}

Table certifications {
  id int [pk, increment, not null]
  name varchar(100) [unique, not null]
}

Table movies {
  id int [pk, increment, not null]
  uuid uuid [not null, unique]
  name varchar(250) [not null]
  year int [not null]
  time int [not null]
  imdb float [not null]
  votes int [not null]
  meta_score float
  gross float
  description text [not null]
  price decimal(10,2)
  certification_id int [not null, ref: > certifications.id]
  // UNIQUE (name, year, time)
}

Table movie_genres {
  movie_id int [pk, not null, ref: > movies.id]
  genre_id int [pk, not null, ref: > genres.id]
}

Table movie_directors {
  movie_id int [pk, not null, ref: > movies.id]
  director_id int [pk, not null, ref: > directors.id]
}

Table movie_stars {
  movie_id int [pk, not null, ref: > movies.id]
  star_id int [pk, not null, ref: > stars.id]
}

Table carts {
  id int [pk, increment, not null]
  user_id int [not null, unique, ref: > users.id]
}

Table cart_items {
  id int [pk, increment, not null]
  cart_id int [not null, ref: > carts.id]
  movie_id int [not null, ref: > movies.id]
  added_at timestamp [not null, default: `now()`]
}

Table orders {
  id int [pk, increment, not null]
  user_id int [not null, ref: > users.id]
  created_at timestamp [not null, default: `now()`]
  status varchar(50) [not null, default: "pending"] // "pending", "paid", "canceled"
  total_amount decimal(10,2)
}

Table order_items {
  id int [pk, increment, not null]
  order_id int [not null, ref: > orders.id]
  movie_id int [not null, ref: > movies.id]
  price_at_order decimal(10,2) [not null]
}

Table payments {
  id int [pk, increment, not null]
  user_id int [not null, ref: > users.id]
  order_id int [not null, ref: > orders.id]
  created_at timestamp [not null, default: `now()`]
  status varchar(50) [not null, default: "successful"] // "successful", "canceled", "refunded"
  amount decimal(10,2) [not null]
  external_payment_id varchar(255)
}

Table payment_items {
  id int [pk, increment, not null]
  payment_id int [not null, ref: > payments.id]
  order_item_id int [not null, ref: > order_items.id]
  price_at_payment decimal(10,2) [not null]
}