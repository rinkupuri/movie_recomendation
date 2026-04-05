@echo off
echo ================================
echo   Movie Recommendation Setup
echo ================================
echo.

echo [1/3] Installing dependencies...
pip install streamlit pandas scikit-learn requests python-dotenv
echo.

echo [2/3] Setting up API key...
set /p API_KEY="Enter your TMDB API key: "
echo TMDB_API_KEY=%API_KEY%> .env
echo .env file created.
echo.

echo [3/3] Launching the app...
echo.
echo App is starting at http://localhost:8501
echo Press Ctrl+C to stop the app.
echo.
python -m streamlit run main.py
