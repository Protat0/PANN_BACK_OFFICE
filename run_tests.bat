@echo off
echo ====================================================================
echo RUNNING COMPREHENSIVE PERFORMANCE TESTS
echo ====================================================================
echo.

echo [1/4] Testing Database Performance...
echo --------------------------------------------------------------------
cd backend
python simple_db_test.py > ..\test_results_db.txt 2>&1
cd ..
echo Done! Results saved to test_results_db.txt
echo.

echo [2/4] Creating Database Indexes...
echo --------------------------------------------------------------------
cd backend
python create_indexes.py > ..\test_results_indexes.txt 2>&1
cd ..
echo Done! Results saved to test_results_indexes.txt
echo.

echo [3/4] Testing API Performance...
echo --------------------------------------------------------------------
python test_performance.py > test_results_api.txt 2>&1
echo Done! Results saved to test_results_api.txt
echo.

echo [4/4] Displaying Results Summary...
echo ====================================================================
echo.

echo DATABASE TEST RESULTS:
echo --------------------------------------------------------------------
type test_results_db.txt
echo.
echo.

echo INDEX CREATION RESULTS:
echo --------------------------------------------------------------------
type test_results_indexes.txt
echo.
echo.

echo API PERFORMANCE RESULTS:
echo --------------------------------------------------------------------
type test_results_api.txt
echo.

echo ====================================================================
echo ALL TESTS COMPLETED!
echo Results saved to:
echo   - test_results_db.txt
echo   - test_results_indexes.txt
echo   - test_results_api.txt
echo ====================================================================

