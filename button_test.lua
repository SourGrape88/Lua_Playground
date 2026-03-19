require("entities")

print(spawn)

function _update()
    if btn("a") then
        print("holding A")
    end

    if btnp("d") then
        print("Pressed D Once")
    else
        print("idle")
    end

end
