param (
    [string]$computer
)

try {
    $build = Invoke-Command -ComputerName $computer -ScriptBlock {Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\"} | Select-Object -Property ProductName, LCUVer
    Write-Output ($build.ProductName + " " + $build.LCUVer)
} catch {
    Write-Output ("[ERROR] Failed to retreive OS build: " + $_.Exception.Message)
}
