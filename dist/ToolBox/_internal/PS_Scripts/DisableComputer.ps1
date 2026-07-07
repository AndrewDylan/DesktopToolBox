param(
    [string]$computer
)

$computer = $computer.Trim()

# Retrieve the PC's current bill number in case it needs to be reverted back due to command failure.
try {
    $oldBilling = Get-ADComputer -Identity $computer -Property departmentNumber -ErrorAction Stop
}
catch {
    Write-Output ("[ERROR] Unable to retrieve PC's current billing number - " + $_.Exception.Message)
}

# Set the departmentNumber to PCR and company to DELETEME
try {
    Set-ADComputer -Identity $computer -Replace @{departmentNumber ="PCR"; company = "DELETEME"} -Credential $GLOBAL:creds -ErrorAction Stop
    Write-Output ("Successfully set departmentNumber(billing) to PCR and company to 'DELETEME' for computer $computer!")
}
catch {
    Write-Output ("[ERROR] Failed to set PCR and DELETEME - " + $_.Exception.Message)
}

# Disable the computer. If failed revert previous change.
try {
    Set-ADComputer -Identity $computer -Enabled $false -Credential $GLOBAL:creds -ErrorAction Stop
    Write-Output ("Successfully disable PC $computer!")
}
catch {
    Set-ADComputer -Identity $computer -Replace @{departmentNumber = $oldBilling.departmentNumber; company = "IOT"} -Credential $GLOBAL:creds -ErrorAction Stop
    Write-Output ("[ERROR] Failed to disable computer - " + $_.Exception.Message)
}