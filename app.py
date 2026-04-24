from flask import Flask, render_template, request
import os
import sqlite3

app = Flask(__name__)
DATABASE = "bookstore.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # SQLite normally gives us rows as tuples, where we access values by position (row[2])
                                    # The row factory lets us access values by column name instead (row["title"] or {{ row.title }})
    return conn


# home page
@app.route("/", methods=["GET"])
def home():
    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    conn.close()

    return render_template("index.html", categories=categories)

# category page
@app.route("/category", methods=["GET"])
def category():
    category_id = request.args.get("categoryId", type=int)

    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    selected_category = conn.execute("""
        SELECT *
        FROM category
        WHERE categoryId = ?
    """, (category_id,)).fetchone()

    books = conn.execute("""
        SELECT *
        FROM book
        WHERE categoryId = ?
        ORDER BY title
    """, (category_id,)).fetchall()

    conn.close()

    return render_template(
        "category.html",
        categories=categories,
        selectedCategory=selected_category,
        books=books,
        searchTerm=None,
        nothingFound=False
    )

# search feature 
@app.route("/search", methods=["POST"])
def search():
    term = request.form.get("search", "").strip()

    conn = get_db_connection()

    categories = conn.execute("""
        SELECT *
        FROM category
        ORDER BY categoryName
    """).fetchall()

    books = conn.execute("""
        SELECT *
        FROM book
        WHERE lower(title) LIKE lower(?)
        ORDER BY title
    """, (f"%{term}%",)).fetchall()

    conn.close()

    return render_template(
        "category.html",
        categories=categories,
        selectedCategory=None,
        books=books,
        searchTerm=term,
        nothingFound=(len(books) == 0)
    )

# book detail page 
@app.route("/book", methods=["GET"])
def book_detail():
    book_id = request.args.get("bookId", type=int)

    conn = get_db_connection()

    categories = conn.execute("""
        SELECT * FROM category ORDER BY categoryName
    """).fetchall()

    book = conn.execute("""
        SELECT book.*, category.categoryName
        FROM book
        JOIN category ON book.categoryId = category.categoryId
        WHERE book.bookId = ?
    """, (book_id,)).fetchone()

    conn.close()

    return render_template(
        "book_detail.html",
        book=book,
        categories=categories
    )


@app.route("/all-books", methods=["GET"])
def all_books():
    conn = get_db_connection()

    categories = conn.execute("""
        SELECT * FROM category ORDER BY categoryName
    """).fetchall()

    books = conn.execute("""
        SELECT * FROM book
        ORDER BY title ASC
    """).fetchall()

    conn.close()

    return render_template(
        "all_books.html",
        categories=categories,
        books=books
    )


@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", error=e), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)

