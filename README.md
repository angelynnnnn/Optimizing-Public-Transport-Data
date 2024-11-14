# Optimizing-Public-Transport-Data

To run the Streamlit app, you will need your own Mapbox API key.

1. **Get an API Key**
* Go to [Mapbox](https://www.mapbox.com) and create an account (if you don't have one).
* Generate an API key from your account settings.
2. **Set up the Environment**
* Copy the provided `.env.example` file to `.env`:

  ```bash
  cp .env.example .env
  ```
* Replace `your_api_key_here` in the `.env` file with your actual API key:

  ```plaintext
  MAPBOX_API = your_actual_api_key
  ```
3. **Install Dependencies** and **Run the Application**
  ```bash
  pip install -r requirements.txt
  python main.py 
  ```
