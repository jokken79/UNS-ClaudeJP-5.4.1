@echo off
REM ========================================
REM JMeter Load Test Runner (Windows)
REM ========================================
REM
REM Purpose: Execute load tests against UNS-ClaudeJP backend
REM Usage: RUN_LOAD_TEST.bat [scenario]
REM Scenarios: light (100 users), medium (1000 users), heavy (10000 users)
REM
REM Example: RUN_LOAD_TEST.bat medium
REM
REM Author: Claude Code
REM Created: 2025-11-12
REM Version: 1.0.0
REM
REM ========================================

setlocal enabledelayedexpansion

REM Configuration
set SCENARIO=%1
if "%SCENARIO%"=="" set SCENARIO=light
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

set JMETER_MASTER=uns-jmeter-master
set BACKEND_URL=http://nginx:80

echo ========================================
echo UNS-ClaudeJP Load Testing
echo ========================================
echo Scenario: %SCENARIO%
echo Timestamp: %TIMESTAMP%
echo.

REM Set scenario parameters
if "%SCENARIO%"=="light" (
    set USERS=100
    set RAMP_UP=60
    set DURATION=300
    set TEST_PLAN=light-load.jmx
) else if "%SCENARIO%"=="medium" (
    set USERS=1000
    set RAMP_UP=120
    set DURATION=300
    set TEST_PLAN=medium-load.jmx
) else if "%SCENARIO%"=="heavy" (
    set USERS=10000
    set RAMP_UP=300
    set DURATION=300
    set TEST_PLAN=heavy-load.jmx
) else (
    echo ERROR: Invalid scenario '%SCENARIO%'
    echo Valid scenarios: light, medium, heavy
    goto :error
)

echo Configuration:
echo   Users: %USERS%
echo   Ramp-up: %RAMP_UP% seconds
echo   Duration: %DURATION% seconds
echo.

REM Check if JMeter services are running
echo [1/6] Checking JMeter services...
docker ps | findstr %JMETER_MASTER% >nul 2>&1
if errorlevel 1 (
    echo Starting JMeter services...
    docker compose -f docker-compose.yml up -d
    timeout /t 10 /nobreak >nul
)
echo [OK] JMeter services are running
echo.

REM Verify backend is accessible
echo [2/6] Verifying backend accessibility...
docker exec %JMETER_MASTER% curl -s -f "%BACKEND_URL%/api/health" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot reach backend at %BACKEND_URL%
    echo Make sure the main application is running:
    echo   docker compose --profile dev up -d
    goto :error
)
echo [OK] Backend is accessible
echo.

REM Create results directories
echo [3/6] Creating results directory...
set RESULTS_DIR=results\%SCENARIO%_%TIMESTAMP%
set REPORT_DIR=reports\%SCENARIO%_%TIMESTAMP%
mkdir %RESULTS_DIR% 2>nul
mkdir %REPORT_DIR% 2>nul
echo [OK] Results directory created
echo.

REM Generate test plan if needed
echo [4/6] Preparing test plan...
if not exist "test-plans\%TEST_PLAN%" (
    echo Generating test plan...
    bash generate-test-plan.sh %SCENARIO%
)
echo [OK] Test plan ready
echo.

REM Run JMeter test
echo [5/6] Running JMeter load test...
set /a TOTAL_TIME=%RAMP_UP%+%DURATION%
echo This will take approximately %TOTAL_TIME% seconds...
echo.

docker exec %JMETER_MASTER% jmeter ^
    -n ^
    -t /tests/%TEST_PLAN% ^
    -l /results/%SCENARIO%_%TIMESTAMP%/results.jtl ^
    -e ^
    -o /reports/%SCENARIO%_%TIMESTAMP% ^
    -Jthreads=%USERS% ^
    -Jrampup=%RAMP_UP% ^
    -Jduration=%DURATION% ^
    -Jhost=%BACKEND_URL%

if errorlevel 1 (
    echo ERROR: JMeter test failed
    goto :error
)
echo.
echo [OK] Load test completed
echo.

REM Generate summary
echo [6/6] Generating summary...

echo ======================================== > %RESULTS_DIR%\summary.txt
echo Load Test Summary >> %RESULTS_DIR%\summary.txt
echo ======================================== >> %RESULTS_DIR%\summary.txt
echo. >> %RESULTS_DIR%\summary.txt
echo Test Configuration: >> %RESULTS_DIR%\summary.txt
echo   Scenario: %SCENARIO% >> %RESULTS_DIR%\summary.txt
echo   Users: %USERS% >> %RESULTS_DIR%\summary.txt
echo   Ramp-up: %RAMP_UP% seconds >> %RESULTS_DIR%\summary.txt
echo   Duration: %DURATION% seconds >> %RESULTS_DIR%\summary.txt
echo   Timestamp: %TIMESTAMP% >> %RESULTS_DIR%\summary.txt
echo. >> %RESULTS_DIR%\summary.txt
echo Reports: >> %RESULTS_DIR%\summary.txt
echo   JTL Results: %RESULTS_DIR%\results.jtl >> %RESULTS_DIR%\summary.txt
echo   HTML Report: %REPORT_DIR%\index.html >> %RESULTS_DIR%\summary.txt
echo   Summary: %RESULTS_DIR%\summary.txt >> %RESULTS_DIR%\summary.txt
echo. >> %RESULTS_DIR%\summary.txt
echo ======================================== >> %RESULTS_DIR%\summary.txt

type %RESULTS_DIR%\summary.txt

echo.
echo ========================================
echo Load test completed successfully!
echo ========================================
echo.
echo Next steps:
echo   1. Open HTML report: %REPORT_DIR%\index.html
echo   2. View raw results: %RESULTS_DIR%\results.jtl
echo   3. Check Grafana: http://localhost:3002 (admin/admin)
echo.

goto :end

:error
echo.
echo ========================================
echo ERROR: Load test failed
echo ========================================
echo.

:end
pause >nul
