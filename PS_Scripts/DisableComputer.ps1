param(
    [string]$computer
)

Set-ADComputer -Identity $computer -Replace @{departmentNumber ="PCR"; company = "DELETEME"} -Credential $creds
Set-ADComputer -Identity $computer -Enabled $false -Credential $creds