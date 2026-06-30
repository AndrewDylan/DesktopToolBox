param(
    [string]$computer
)

$computer = $computer.Trim()

try {
    Get-ADComputer -Identity $computer -Properties departmentNumber, company
}
catch {
    Write-Output ("[ERROR] Unable to retrieve PC information - " + $_.Exception.Message)
}
