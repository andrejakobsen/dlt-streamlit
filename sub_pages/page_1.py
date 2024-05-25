import streamlit as st

from ._page_base import BasePageLayout

class Page1(BasePageLayout):

    def __init__(self):
        super().__init__()

    def page_content(self):
        st.title("Page 1")
        st.markdown("* * *")