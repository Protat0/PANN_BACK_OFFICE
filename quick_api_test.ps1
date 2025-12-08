Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "API PERFORMANCE TEST - Measuring Load Times" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000/api/v1"

function Test-ApiEndpoint {
    param([string]$Name, [string]$Url)
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    Write-Host "URL: $Url" -ForegroundColor Gray
    
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri "$baseUrl$Url" -Method GET -TimeoutSec 60 -ErrorAction Stop
        $sw.Stop()
        
        $duration = $sw.Elapsed.TotalSeconds
        $sizeKB = [math]::Round($response.Content.Length / 1024, 2)
        $sizeMB = [math]::Round($sizeKB / 1024, 2)
        
        $timeColor = if ($duration -gt 10) { "Red" } elseif ($duration -gt 5) { "Yellow" } else { "Green" }
        $timeIcon = if ($duration -gt 10) { "❌" } elseif ($duration -gt 5) { "⚠️" } else { "✅" }
        
        Write-Host "  Status: $($response.StatusCode) ✅" -ForegroundColor Green
        Write-Host "  Duration: $timeIcon $([math]::Round($duration, 2))s" -ForegroundColor $timeColor
        if ($sizeMB -gt 1) {
            Write-Host "  Size: $sizeMB MB" -ForegroundColor Gray
        } else {
            Write-Host "  Size: $sizeKB KB" -ForegroundColor Gray
        }
        Write-Host ""
        
        return @{Success=$true; Duration=$duration; Size=$response.Content.Length}
    }
    catch {
        $sw.Stop()
        Write-Host "  ERROR: $($_.Exception.Message) ❌" -ForegroundColor Red
        Write-Host "  Time before error: $([math]::Round($sw.Elapsed.TotalSeconds, 2))s" -ForegroundColor Yellow
        Write-Host ""
        return @{Success=$false; Duration=$sw.Elapsed.TotalSeconds; Error=$_.Exception.Message}
    }
}

Write-Host "1. PRODUCTS API TESTS" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------" -ForegroundColor Gray
$test1 = Test-ApiEndpoint "Products (limit=10)" "/products/?limit=10"
$test2 = Test-ApiEndpoint "Products (limit=100)" "/products/?limit=100"
$test3 = Test-ApiEndpoint "Products (ALL - no limit)" "/products/"

Write-Host "`n2. SALES/DASHBOARD API TESTS" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------" -ForegroundColor Gray
$test4 = Test-ApiEndpoint "Sales by Item (no date filter)" "/sales-display/by-item/"
$test5 = Test-ApiEndpoint "Sales by Item (last month)" "/sales-display/by-item/?start_date=2025-11-01&end_date=2025-11-30"
$test6 = Test-ApiEndpoint "Recent Sales (limit=20)" "/sales/recent/?limit=20"
$test7 = Test-ApiEndpoint "Invoice Stats" "/invoices/stats/?start_date=2025-11-01&end_date=2025-11-30"

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

$allTests = @($test1, $test2, $test3, $test4, $test5, $test6, $test7)
$successful = ($allTests | Where-Object { $_.Success }).Count
$failed = ($allTests | Where-Object { -not $_.Success }).Count
$slow = ($allTests | Where-Object { $_.Success -and $_.Duration -gt 5 }).Count
$critical = ($allTests | Where-Object { $_.Success -and $_.Duration -gt 10 }).Count

Write-Host "Total Tests: $($allTests.Count)" -ForegroundColor White
Write-Host "Successful: $successful" -ForegroundColor Green
Write-Host "Failed/Timeout: $failed" -ForegroundColor $(if($failed -gt 0){"Red"}else{"Green"})
Write-Host "Slow (>5s): $slow" -ForegroundColor $(if($slow -gt 0){"Yellow"}else{"Green"})
Write-Host "Critical (>10s): $critical" -ForegroundColor $(if($critical -gt 0){"Red"}else{"Green"})

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "KEY FINDINGS" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

if ($critical -gt 0) {
    Write-Host "🔥 CRITICAL: $critical endpoint(s) taking >10 seconds!" -ForegroundColor Red
    Write-Host "   This will cause frontend timeouts (30s limit)" -ForegroundColor Red
}

if ($test3.Success -and $test1.Success) {
    $improvement = [math]::Round((($test3.Duration - $test1.Duration) / $test3.Duration) * 100, 1)
    Write-Host "`n📊 Pagination Impact:" -ForegroundColor Yellow
    Write-Host "   Products (all): $([math]::Round($test3.Duration, 1))s" -ForegroundColor White
    Write-Host "   Products (limit=10): $([math]::Round($test1.Duration, 1))s" -ForegroundColor White
    Write-Host "   Improvement: $improvement% faster" -ForegroundColor Green
}

if ($test4.Success -eq $false -or $test4.Duration -gt 10) {
    Write-Host "`n❌ Sales Display API is the BOTTLENECK!" -ForegroundColor Red
    Write-Host "   This endpoint is causing your Dashboard timeouts" -ForegroundColor Red
    Write-Host "   Needs: Database indexes + query optimization" -ForegroundColor Yellow
}

Write-Host "`n======================================================================" -ForegroundColor Cyan

