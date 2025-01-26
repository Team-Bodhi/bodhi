import streamlit as st
from utils.cart import add_to_cart
from utils.helpers import format_date, navigate_to


def render_book_details():
    """Render the book details page"""
    if not st.session_state.current_book:
        navigate_to('main')
        return
        
    book = st.session_state.current_book
    
    # Back button and title in same row
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            navigate_to('main')
    with col2:
        st.title(book.get('title', 'Untitled'))
    
    # Main content columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(book.get('coverImageUrl', 'http://dummyimage.com/180x100.png/dddddd/000000'),
                use_container_width=True)
        
        if book.get('quantity', 0) > 0:
            quantity = st.number_input("Quantity", min_value=1, 
                                     max_value=book.get('quantity'), value=1)
            if st.button("Add to Cart 🛒", type="primary", use_container_width=True):
                add_to_cart(book, quantity)
                st.rerun()
            
            if book.get('quantity') < 10:
                st.markdown(f'<div class="stock-warning">Only {book.get("quantity")} left in stock!</div>', 
                          unsafe_allow_html=True)
        else:
            st.error("Out of Stock")
    
    with col2:
        st.subheader(f"By {book.get('author', 'Unknown Author')}")
        st.markdown(f'<h2 class="price-tag">${book.get("price", 0):.2f}</h2>', 
                   unsafe_allow_html=True)
        
        # Book details in a clean grid
        details = {
            "Genre": book.get('genre', 'Uncategorized'),
            "Publisher": book.get('publisher', 'Unknown'),
            "Language": book.get('language', 'Unknown'),
            "Pages": book.get('pages', 'Unknown'),
            "ISBN": book.get('isbn', 'Unknown'),
            "Publication Date": format_date(book.get('publicationDate', '')),
            "Stock": f"{book.get('quantity', 0)} copies available"
        }
        
        col1, col2 = st.columns(2)
        for i, (key, value) in enumerate(details.items()):
            with col1 if i % 2 == 0 else col2:
                st.write(f"**{key}:** {value}")
    
    st.write("---")
    st.subheader("Summary")
    st.write(book.get('summary', 'No summary available.')) 