function _init()
    circleY = 200
    rectY = 100
    lineY = 300
    load_sprite("player", "C:/Users/Owner/Desktop/Projects/Lua_Playground/assets/status_light/Sprite_test.png")
    frames = {
        "C:/Users/Owner/Desktop/Projects/Lua_Playground/assets/status_light/Sprite_test.png",
        "C:/Users/Owner/Desktop/Projects/Lua_Playground/assets/status_light/Sprite_test2.png"
    }
    load_anim("player_anim", frames, 8) -- 8FPS
end

function _update()
    circleY = circleY + 2
    rectY = rectY + 2
    lineY = lineY + 2
    if circleY > 400 then
        circleY = 200
    end
    if rectY > 400 then
        rectY = 200
    end
    if lineY > 400 then
        lineY = 200
    end
end

function _draw()
    rect(200, rectY)
    rectfill(300, rectY)
    circle(10, circleY)
    circlefill(100, circleY)
    line(400,200,500,lineY)
    print("hello world")
    sprite("player", 500, 100)
    sprite("player_anim", 500, 300)
end
