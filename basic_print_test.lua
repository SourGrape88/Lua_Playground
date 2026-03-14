-- Run in your Neovim editor
x = 100
y = 150

function _init()
    print("Game started!")
end

function _update()
    x = x + 2
    if x > 400 then
        x = 0
    end
end

function _draw()
    cls()              -- Clear the canvas each frame
    circle(x, 200, 50) -- Draw a circle
    rect(50, 50, 100, 100)
end