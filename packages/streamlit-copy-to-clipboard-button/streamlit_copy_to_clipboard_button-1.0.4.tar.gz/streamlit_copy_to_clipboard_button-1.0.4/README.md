# streamlit-copy-to-clipboard-button

A Streamlit copy-to-clipboard button component that respects the streamlit page styles.

![Demo](https://raw.githubusercontent.com/samsze0/streamlit-copy-to-clipboard-button/main/assets/demo-1.png)

## Installation instructions

```sh
pip install streamlit-copy-to-clipboard-button
```

## Usage instructions

```python
import streamlit as st

from streamlit_copy_to_clipboard_button import copy_to_clipboard

copy_to_clipboard(
    "Text to copy",
    label="Copy to clipboard",  # Optional
    label_after_copy="Copied!"  # Optional
)
```
