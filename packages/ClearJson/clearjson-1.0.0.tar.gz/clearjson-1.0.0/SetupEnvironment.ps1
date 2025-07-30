[String] $VEnvPath = [IO.Path]::Combine([IO.Path]::GetDirectoryName($PSCommandPath), ".venv")
[String] $SourcePath =  [IO.Path]::GetDirectoryName($PSCommandPath)
$SourcePath += "\."

& "C:/Program Files/Python312/python.exe" -m venv $VEnvPath

[String] $VEnvPythonPath = [IO.Path]::Combine([IO.Path]::GetDirectoryName($PSCommandPath), ".venv", "Scripts/python.exe")
& $VEnvPythonPath -m pip install --upgrade pip
& $VEnvPythonPath -m pip install --upgrade build
& $VEnvPythonPath -m pip install --upgrade twine

#& $VEnvPythonPath -m pip install $SourcePath
