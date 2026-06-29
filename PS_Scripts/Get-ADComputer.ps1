param(
    [string]$computer
)

Get-ADComputer -Identity $computer -Properties departmentNumber, company