-- Camera.lua (Camera System)

local Camera = {}
Camera.__index = Camera

function Camera:new(x, y)
    return setmetatable({x = x or 0, y = y or 0, zoom = 1, target = nil}, self)
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

function Camera:update()
    if self.target then
        -- Center Camera on target
        self.x = self.target.x - 400 -- Half of Viewport
        self.y = self.target.y - 300 -- Half of Viewport
    end
end

function Camera:apply(x, y)
    return (x - self.x) * self.zoom, (y - self.y) * self.zoom
end

function Camera:apply_w(obj)
    obj.x, obj.y = self:apply(obj.x, obj.y)
end

return Camera
