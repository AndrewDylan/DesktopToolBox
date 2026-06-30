param (
    [string]$username,
    [string]$pswd
)

$username = $username.Trim()
$pswd = $pswd.Trim()


if ([string]::IsNullOrWhiteSpace($UserName)) {
    Write-Output "[ERROR] Empty UserName after trim."
    return
}
if ([string]::IsNullOrWhiteSpace($pswd)) {
    Write-Output "[ERROR] Empty Password after trim."
    return
}

# Try to import the Security module
try {
    Import-Module Microsoft.PowerShell.Security -ErrorAction Stop
    $sec = ConvertTo-SecureString -String $pswd -AsPlainText -Force -ErrorAction Stop
}
catch {
    # Fallback that avoids the Security module entirely
    try {
        $sec = [System.Net.NetworkCredential]::new("", $pswd).SecurePassword
    }
    catch {
        Write-Output ("[ERROR] SecureString creation failed: " + $_.Exception.Message)
        return
    }
}

# Build PSCredential (works in all modes)
try {
    $GLOBAL:creds = [System.Management.Automation.PSCredential]::new($UserName, $sec)
    Write-Output "[IOT] creds initialized for $($GLOBAL:creds.UserName)"
}
catch {
    Write-Output ("[ERROR] PSCredential construction failed: " + $_.Exception.Message)
}

