import streamlit as st
from streamlit_copy_to_clipboard_button import copy_to_clipboard

copy_to_clipboard(
    "Hello, world!", label="Copy to clipboard", label_after_copy="Copied!"
)
copy_to_clipboard(
    "Hello, world!",
    disabled=True,
    label="Copy to clipboard (disabled)",
    label_after_copy="Copied!",
)

# Mimic these button
st.button("Native button", key="k1")
st.button("Native button (disabled)", disabled=True, key="k2")
