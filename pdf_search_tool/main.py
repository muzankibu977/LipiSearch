import streamlit as st
from utils import load_index, search_line, ocr_from_image
import json
from extract_texts import build_index
import os

st.title("📚 Multilingual PDF Search Engine")
st.write("Search your PDF library using text or image line input.")

import time

def is_reindex_needed(index_file='indexed_texts.json', pdf_dir='pdfs'):
    if not os.path.exists(index_file):
        return True
    index_time = os.path.getmtime(index_file)
    for fname in os.listdir(pdf_dir):
        fpath = os.path.join(pdf_dir, fname)
        if os.path.getmtime(fpath) > index_time:
            return True
    return False

if is_reindex_needed():
    with st.spinner("Indexing PDFs..."):
        build_index()


index = load_index()

option = st.radio("Choose Input Type", ["Text", "Image"])

if option == "Text":
    user_input = st.text_area("Enter a line of text:")
    if st.button("Search"):
        if user_input.strip():
            results = search_line(user_input.strip(), index)
            if results:
                for res in results:
                    st.success(f"📄 {res['pdf']} | Page {res['page']} | Line {res['line_number']}")
                    st.code(res['line'])
            else:
                st.warning("No matches found.")
elif option == "Image":
    uploaded_file = st.file_uploader("Upload an image of text", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        text = ocr_from_image(uploaded_file)
        st.text_area("Extracted Text", text)
        if st.button("Search"):
            results = search_line(text.strip(), index)
            if results:
                for res in results:
                    st.success(f"📄 {res['pdf']} | Page {res['page']} | Line {res['line_number']}")
                    st.code(res['line'])
            else:
                st.warning("No matches found.")