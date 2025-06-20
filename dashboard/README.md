# Dashboard

A dashboard can be run to view visualisations of minute by minute data on football matches.

## Overview

### `streamlit_app.py`
- Dashboard run script to set the page config and run the match selector to create the sidebar.

### `data.py`
- Script for all queries interacting with the database.

### `fixtures.py`
- Script fto make the pictures page

### `home.py`
- Script to create the home page

### `selector.py`
- All the functionality behind creating the drop down selector in the side bar

### `subscription.py`
- Script to create the subscription page

### `timeline.py`
- Script to create the timeline and for functionality of the slider


## Required Dependencies
- Create a virtual environment
    - `python -m venv .venv`
- Activate venv
    - On Mac/Linux
        - `source .venv/bin/activate`
    - On Windows
        - `.\.venv\Scripts\activate.bat`
- Install dependencies
    - `pip3 install -r requirements.txt`


## Environment Variables

Create a `.env` file or set the following environment variables:

```
DATABASE_USERNAME=<DATABASE_USERNAME>
DATABASE_NAME=<DATABASE_NAME>
DATABASE_PASSWORD=<DATABASE_PASSWORD>
HOST=<DATABASE_HOST>
PORT=<DATABASE_PORT>
```

