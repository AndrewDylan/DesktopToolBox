param(
    [Parameter(Mandatory)][string]$username,
    [Parameter(Mandatory)][string]$pswd
)

Add-Type -AssemblyName System.DirectoryServices.AccountManagement

$domain = "isd-nt"
$username = $username.Trim()
$password = $pswd.Trim()

$context = New-Object System.DirectoryServices.AccountManagement.PrincipalContext(

    [System.DirectoryServices.AccountManagement.ContextType]::Domain, $domain
)

$context.ValidateCredentials($username, $password)