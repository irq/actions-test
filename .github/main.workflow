workflow "Build and publish" {
  on = "push"
  resolves = ["Publish"]
}

action "Dotnet restore" {
  uses = "azure/github-actions/dotnetcore-cli@master"
  args = "restore -s https://api.nuget.org/v3/index.json -s %MYGET_FEED_URL%"
  secrets = ["MYGET_FEED_URL"]
}

action "Dotnet build" {
  uses = "azure/github-actions/dotnetcore-cli@master"
  args = "build -c Release"
  needs = "Dotnet restore"
}

action "Master" {
  uses = "actions/bin/filter@master"
  args = "branch master"
  needs = "Dotnet build"
}

action "Pack" {
  uses = "azure/github-actions/dotnetcore-cli@master"
  args = "pack -o ./package -c Release --include-symbols /p:Version=0.0.2"
  needs = "Master"
}

action "Publish" {
  uses = "azure/github-actions/dotnetcore-cli@master"
  args = "nuget push package/ -s https://trustpilot.myget.org/F/libraries/ -k %MYGET_KEY% -ss https://trustpilot.myget.org/F/libraries/symbols/ -sk %MYGET_KEY%"
  needs = "Pack"
  secrets = ["MYGET_KEY"]
}