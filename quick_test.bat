@echo off
echo =====================================================================
echo API PERFORMANCE TEST
echo =====================================================================
echo.

echo [TEST 1] Products API with limit=10 (OPTIMIZED)
echo ---------------------------------------------------------------------
curl -w "Time: %%{time_total}s | Size: %%{size_download} bytes\n" -o nul -s "http://localhost:8000/api/v1/products/?limit=10"
echo.

echo [TEST 2] Products API with limit=50
echo ---------------------------------------------------------------------
curl -w "Time: %%{time_total}s | Size: %%{size_download} bytes\n" -o nul -s "http://localhost:8000/api/v1/products/?limit=50"
echo.

echo [TEST 3] Products API ALL (OLD WAY - SLOW)
echo ---------------------------------------------------------------------
curl -w "Time: %%{time_total}s | Size: %%{size_download} bytes\n" -o nul -s "http://localhost:8000/api/v1/products/"
echo.

echo [TEST 4] Sales Recent (limit=20)
echo ---------------------------------------------------------------------
curl -w "Time: %%{time_total}s | Size: %%{size_download} bytes\n" -o nul -s "http://localhost:8000/api/v1/sales/recent/?limit=20"
echo.

echo =====================================================================
echo TEST COMPLETE
echo =====================================================================
pause
