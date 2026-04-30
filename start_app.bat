@echo off
REM =====================================================================
REM  Digital Consulting Engineer · المستشار الهندسي الرقمي
REM  Double-click this file to start the app. No typing needed.
REM =====================================================================
title Digital Consulting Engineer
cd /d "%~dp0"
echo.
echo  =====================================================================
echo   Starting the Digital Consulting Engineer ...
echo   جارٍ تشغيل المستشار الهندسي الرقمي ...
echo  =====================================================================
echo.
echo   The browser will open automatically in a few seconds.
echo   Keep this window open while you use the app.
echo   To stop the app, press Ctrl+C or just close this window.
echo.
echo   سيُفتح المتصفح تلقائياً خلال ثوانٍ.
echo   لا تُغلق هذه النافذة أثناء استخدامك للتطبيق.
echo   لإيقاف التطبيق اضغط Ctrl+C أو أغلق النافذة.
echo.
echo  =====================================================================
echo.
python -m streamlit run app.py
pause
