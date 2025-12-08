# API Performance Test Script
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "API PERFORMANCE TEST - Before vs After Optimizations" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api/v1"

function Test-Endpoint {
    param(
        [string]$name,
        [string]$url
    )
    
    Write-Host "Testing: $name" -ForegroundColor Yellow
    $fullUrl = "$baseUrl$url"
    
    $start = Get-Date
    try {
        $response = Invoke-WebRequest -Uri $fullUrl -Method GET -TimeoutSec 60 -ErrorAction Stop
        $end = Get-Date
        $duration = ($end - $start).TotalSeconds
        $sizeKB = [math]::Round($response.Content.Length / 1024, 2)
        $sizeMB = [math]::Round($sizeKB / 1024, 2)
        $sizeDisplay = if ($sizeMB -gt 1) { "$sizeMB MB" } else { "$sizeKB KB" }
        
        $statusIcon = if ($response.StatusCode -eq 200) { "✅" } else { "⚠️" }
        $timeIcon = if ($duration -gt 10) { "❌" } elseif ($duration -gt 5) { "⚠️" } else { "✅" }
        
        Write-Host "  $statusIcon Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "  $timeIcon Duration: $([math]::Round($duration, 3)) seconds" -ForegroundColor $(if ($duration -gt 10) { "Red" } elseif ($duration -gt 5) { "Yellow" } else { "Green" })
        Write-Host "  📦 Size: $sizeDisplay" -ForegroundColor Gray
        
        return @{
            Success = $true
            Duration = $duration
            Size = $response.Content.Length
            StatusCode = $response.StatusCode
        }
    }
    catch {
        $end = Get-Date
        $duration = ($end - $start).TotalSeconds
        Write-Host "  ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  ⏱️  Time before error: $([math]::Round($duration, 3)) seconds" -ForegroundColor Yellow
        
        return @{
            Success = $false
            Duration = $duration
            Error = $_.Exception.Message
        }
    }
    
    Write-Host ""
}

Write-Host "1. Products API with Pagination (NEW - OPTIMIZED)" -ForegroundColor Cyan
Write-Host "---------------------------------------------------------------------" -ForegroundColor Gray
$test1 = Test-Endpoint -name "Products API (limit=10)" -url "/products/?limit=10"
$test2 = Test-Endpoint -name "Products API (limit=50)" -url "/products/?limit=50"
$test3 = Test-Endpoint -name "Products API (limit=100)" -url "/products/?limit=100"

Write-Host ""
Write-Host "2. Products API without Pagination (OLD - SLOW)" -ForegroundColor Cyan
Write-Host "---------------------------------------------------------------------" -ForegroundColor Gray
$test4 = Test-Endpoint -name "Products API (all products)" -url "/products/"

Write-Host ""
Write-Host "3. Other Dashboard APIs" -ForegroundColor Cyan
Write-Host "---------------------------------------------------------------------" -ForegroundColor Gray
$test5 = Test-Endpoint -name "Recent Sales (limit=20)" -url "/sales/recent/?limit=20"
$test6 = Test-Endpoint -name "Invoice Stats (last month)" -url "/invoices/stats/?start_date=2025-11-01&end_date=2025-11-30"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "SUMMARY & ANALYSIS" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Calculate improvements
if ($test4.Success -and $test1.Success) {
    $improvement = [math]::Round((($test4.Duration - $test1.Duration) / $test4.Duration) * 100, 1)
    $speedup = [math]::Round($test4.Duration / $test1.Duration, 1)
    
    Write-Host "📊 Performance Improvement:" -ForegroundColor Green
    Write-Host "  Old (all products): $([math]::Round($test4.Duration, 2))s @ $([math]::Round($test4.Size/1024/1024, 2)) MB"
    Write-Host "  New (limit=10):     $([math]::Round($test1.Duration, 2))s @ $([math]::Round($test1.Size/1024, 2)) KB"
    Write-Host "  Improvement:        $improvement% faster ($speedup x speedup)" -ForegroundColor Yellow
    Write-Host ""
}

# Check for timeouts
$allTests = @($test1, $test2, $test3, $test4, $test5, $test6)
$slowTests = $allTests | Where-Object { $_.Duration -gt 5 }
$criticalTests = $allTests | Where-Object { $_.Duration -gt 10 }

if ($criticalTests.Count -gt 0) {
    Write-Host "❌ CRITICAL: $($criticalTests.Count) endpoint(s) took > 10 seconds" -ForegroundColor Red
}
elseif ($slowTests.Count -gt 0) {
    Write-Host "⚠️  WARNING: $($slowTests.Count) endpoint(s) took > 5 seconds" -ForegroundColor Yellow
}
else {
    Write-Host "✅ All endpoints completed in < 5 seconds!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "RECOMMENDATIONS" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ DONE: Added pagination to Products API" -ForegroundColor Green
Write-Host "✅ DONE: API is backwards compatible (works with and without limit)" -ForegroundColor Green
Write-Host ""
Write-Host "📝 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Update frontend Dashboard to use ?limit=50 for products" -ForegroundColor White
Write-Host "  2. Add database indexes (run: py backend\create_indexes.py)" -ForegroundColor White
Write-Host "  3. Consider implementing Redis caching for frequently accessed data" -ForegroundColor White
Write-Host ""
Write-Host "💡 TIP: Use ?limit=X&page=Y for pagination in frontend" -ForegroundColor Cyan
Write-Host "   Example: /api/v1/products/?limit=50&page=1" -ForegroundColor Gray
Write-Host ""
