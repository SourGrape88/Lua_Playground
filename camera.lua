-- Camera.lua (Camera System)

local Camera = {}
Camera.__index = Camera

function Camera:new(x, y)
    return setmetatable({
        x = x or 0,
        y = y or 0,
        zoom = 1,
        target = nil}, self)
end

function Camera:set(x, y)
    self.x = x or self.x
    self.y = y or self.y
end

function Camera:move(dx, dy)
    self.x = self.x + (dx or 0)
    self.y = self.y + (dy or 0)
end

function Camera:follow(target)
    self.target = target
end

function Camera:clamp(min_x, min_y, max_x, max_y)
    self.min_x = min_x
    self.min_y = min_y
    self.max_x = max_x
    self.max_y = max_y
end

function Camera:update()
    if self.target then
        -- Center Camera on target
        self.x = self.target.x - 400 -- Half of Viewport
        self.y = self.target.y - 300 -- Half of Viewport

        -- Clamp
        if self.min_x then
            self.x = math.max(self.min_x, math.min(self.x, self.max_x))
            self.y = math.max(self.min_y, math.min(self.y, self.max_y))
        end
    end
end

function Camera:apply(x, y)
    return (x - self.x) * self.zoom, (y - self.y) * self.zoom
end

function Camera:apply_w(obj)
    obj.x, obj.y = self:apply(obj.x, obj.y)
end

return Camera
