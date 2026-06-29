param(
    [string]$computer,
    [string]$billCode
)

Set-ADComputer -Identity $computer -Replace @{departmentNumber = $billCode} -Credential $creds
Write-Output "[DONE]"