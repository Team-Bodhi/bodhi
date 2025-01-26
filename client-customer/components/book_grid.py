import streamlit as st

from services.api import fetch_books
from utils.cart import add_to_cart
from utils.helpers import navigate_to


def render_main_page():
    """Render the main page with book grid"""
    st.title("Welcome to Bodhi Bookstore 📚")
    
    # Search and Filter Section
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("Search books by title or author")
    with col2:
        genre_filter = st.selectbox("Filter by genre", 
                                  ["All", "Fiction", "Non-Fiction", "Science", "History"])
    
    # Display Books
    books = fetch_books()
    filtered_books = books
    
    if search_query:
        filtered_books = [book for book in filtered_books 
                         if search_query.lower() in book.get('title', '').lower() 
                         or search_query.lower() in book.get('author', '').lower()]
    
    if genre_filter != "All":
        filtered_books = [book for book in filtered_books 
                         if book.get('genre') == genre_filter]
    
    # Display books in a grid
    cols = st.columns(3)
    for idx, book in enumerate(filtered_books):
        with cols[idx % 3]:
            st.write("---")
            with st.container():
                st.image(book.get('coverImageUrl', 'http://dummyimage.com/180x100.png/dddddd/000000'),
                        use_container_width=True)
                st.subheader(book.get('title', 'Untitled'))
                st.write(f"By {book.get('author', 'Unknown Author')}")
                st.write(f"**${book.get('price', 0):.2f}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Details 📖", key=f"details_{idx}"):
                        navigate_to('details', book)
                with col2:
                    if book.get('quantity', 0) > 0:
                        if st.button("Add to Cart 🛒", key=f"add_{idx}"):
                            add_to_cart(book)
                            st.rerun()
                    else:
                        st.write("Out of Stock") 