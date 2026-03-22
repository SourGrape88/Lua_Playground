-- map_test.lua
map = require("map"):new(32)
Physics = require("physics")
require("entities")
camera = require("camera"):new()

function _init()

    -- Simple map (26x20)
    map:load({
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
        {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
        {0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0},
        {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
    })

    player = spawn({
        x = 400,
        y = 300,
        width = 64,
        height = 64,
        vx = 0,
        vy = 0,
        speed = 14,
        bouncy = false,

        update = function(self)

            -- Check Ground (for jumps)
            -- If the Player Moves Down 1 Pixel
            -- Would They Collide with the Ground?
            -- If Yes, "on_ground" = True
            local on_ground = self.vy == 0 and map:check_collision(
                self.x,
                self.y + 1,
                self.width,
                self.height)

            -- Horizontal Movement
            if btn("a") then self.vx = self.vx - 0.5 end
            if btn("d") then self.vx = self.vx + 0.5 end

            -- Jump
            if btnp("w") and on_ground then 
                self.vy = -15 
            end

            Physics.apply_gravity(self)
            Physics.apply_friction(self, 0.03)
            Physics.move(self, map)

        if Physics.check_aabb(self, ball) then
            local player_bottom = self.y + self.height
            local ball_top = ball.y

            local standing_on_ball = player_bottom <= ball_top + 10 and self.vy >= 0

            if standing_on_ball then
                -- Place player on Top
                self.y = ball.y - self.height
                self.vy = 0
                local kick_strength = 8
                if self.x < ball.x then ball.vx = kick_strength else ball.vx = -kick_strength end
                ball.vy = -5
                ball.vx = ball.vx + (self.vx * 0.3)
            else
                local push = self.vx * 0.5
                ball.vx = ball.vx + push

                if self.y < ball.y then
                    ball.vy = ball.vy - math.abs(self.vy * 0.2)
                end
            end
        end
    end,

              
        draw = function(self)
            rect(math.floor(self.x), math.floor(self.y), self.width, self.height, {0, 200, 60})
        end
    })

    local map_width = 26 * 32
    local map_height = 20 * 32

    camera:clamp(
        0, 0,
        map_width - 1000,
        map_height - 800
    )

    camera:follow(player)

    -- Ball Entity
    ball = spawn({
        x = 500,
        y = 200,
        r = 32,
        width = 64,
        height = 64,
        hit_w = 32,
        hit_h = 32,
        hit_offset_x = 16,
        hit_offset_y = 16,
        vx = 0,
        vy = 0,
        bouncy = true,

        update = function(self)
            Physics.apply_gravity(self, 0.4)
            Physics.apply_friction(self, 0.01)
            Physics.move(self, map)

            -- Bounce off walls
            if math.abs(self.vx) < 0.1 then
                self.vx = 0 -- Reverse Direction
            end
            if math.abs(self.vy) < 0.01 then
                self.vy = 0 -- Reverse Direction
            end

        end,
        
        draw = function(self)
        -- Center the circle on the hitbox
        local cx = math.floor((self.x - 16) + (self.hit_offset_x or 0) + (self.hit_w or self.width)/2)
        local cy = math.floor((self.y - 16) + (self.hit_offset_y or 0) + (self.hit_h or self.height)/2)
        circle(cx, cy, self.r, {200, 50, 50})

        -- Hitbox rectangle
        rect(
            math.floor(self.x + (self.hit_offset_x or 0)),
            math.floor(self.y + (self.hit_offset_y or 0)),
            self.hit_w or self.width,
            self.hit_h or self.height,
            {10, 0, 255})
         end   
     })

end

function _update()
    update_entities()
    camera:update()
end

function _draw()
    map:draw()
    draw_entities()
end
