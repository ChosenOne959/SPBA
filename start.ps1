# run at Dir "D:/schoolwork/PRP/SPBA/new_ui"

function ReadFile($path){
    return (Get-Content -Raw -Encoding "UTF8" -Path "$path")
}

function ReadJsonFile($path){
    $content = ReadFile $path
    return ConvertFrom-Json -InputObject $content
}

$is_localhost = $args[0]
echo "load path_data"

if($is_localhost)
{
    $config = (ReadJsonFile -path "D:/schoolwork/PRP/SPBA/new_ui/configuration_file.json")
}
else
{
    $config = (ReadJsonFile -path "D:/schoolwork/PRP/SPBA/new_ui/remote_configuration_file.json")

}

echo "build Airsim"
$AirsimBuildPath = $config.path.Airsim+"/build.sh"
& $AirsimBuildPath

echo "copy Plugins file"
$AirsimPluginsDir = $config.path.Airsim+"/Unreal/Plugins"
copy-Item -Path $AirsimPluginsDir -Destination $config.path.UnrealProjectDir -Force

# edit .uproject file

# generate Visual Studio project files?

# run UnrealProject
# & $config.path.UE4dir /game config.path.UnrealProject