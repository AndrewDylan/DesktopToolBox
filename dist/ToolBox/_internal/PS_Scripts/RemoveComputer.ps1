 param (
    [string]$computer
 )

 $computer = $computer.Trim()

 try {
    $dName = Get-ADComputer -Identity $computer | Select-Object DistinguishedName -ErrorAction Stop
 }
 catch {
    Write-Output ("[ERROR] Unable to get DistinguishedName - " + $_.Exception.Message)
 }

 try {
    Get-ADObject -SearchBase $dName.distinguishedName -Filter * | Remove-ADObject -Recursive -Confirm:$false -Credential $GLOBAL:creds
    Write-Output ("Successfully removed PC $computer from AD!")
 }
 catch {
    Write-Output ("[ERROR] Failed to remove PC - " + $_.Exception.Message)
 }