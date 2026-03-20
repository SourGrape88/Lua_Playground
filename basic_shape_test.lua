-- Basic_shape_test.lua

require("entities")
camera = require("camera"):new()
print(spawn)

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

    player = spawn({
        name = "player_anim",
        x = 400,
        y = 400,
        speed = 2,

        update = function(self)
            if btn("a") then self.x = self.x - self.speed end
            if btn("d") then self.x = self.x + self.speed end
            if btn("w") then self.y = self.y - self.speed end
            if btn("s") then self.y = self.y + self.speed end
        end,

        draw = function(self)
            sprite(self.name, self.x, self.y)
        end

    })
    spawn_enemy(player.x + 100, 100, true)
    spawn_enemy(250, 120)
    spawn_enemy(350, 120)
    camera:follow(player)
end



function spawn_enemy(x, y, follow_player)
    spawn({
        x = x,
        y = y,
        dx = -1,
        follow = follow_player or false,

        update = function(self)
            if self.follow then
                -- Move with Player Input
                if player.x > self.x then self.x = self.x + 1  end
                if player.x < self.x then self.x = self.x - 1 end
            else
                self.x = self.x + self.dx
            end
        end,

        draw = function(self)
            rect(self.x, self.y, 10, 10)
        end
    })
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

      update_entities()
      camera:update()

end

function _draw()
    rect(200, rectY)
    rectfill(300, rectY)
    circle(10, circleY)
    circlefill(100, circleY)
    line(398,200,500,lineY)
    print("hello world")
    print(spawn, 300, 50)
    sprite("player", 500, 100)
    draw_entities()
end
