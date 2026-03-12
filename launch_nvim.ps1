# launch_nvim.ps1
# Project-specific Neovim launcher for Lua_Playground

# Path to Neovim executable
$NVIM_EXE = "C:\Users\Owner\scoop\apps\neovim\current\bin\nvim.exe"

# Path to your project NVChad config
$NVIM_CONFIG = "$PSScriptRoot\nvim_config"

# Launch Neovim directly in the current shell
& $NVIM_EXE `
    -u "$NVIM_CONFIG\init.lua" `
    --cmd "set rtp^=$NVIM_CONFIG"