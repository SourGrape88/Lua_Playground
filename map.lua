-- map.lua

local Map = {}
Map.__index = Map

-- Constructor (Create a New Map)
function Map:new(tile_size)
    -- This is the Object
    local obj = {
        tile_size = tile_size or 32,
        data = {},
        tileset = {}
    }

    setmetatable(obj, self)
    return obj
end

-- Load map data (2D Array)
function Map:load(data)
    self.data = data
end

-- Define what each tile number means
function Map:set_tileset(tileset)
    self.tileset = tileset
end

-- Draw the Map
function Map:draw()
    for y, row in ipairs(self.data) do
        for x, tile in ipairs(row) do
            if tile ~= 0 then
                local px = (x - 1) * self.tile_size
                local py = (y - 1) * self.tile_size

                local sprite_name = self.tileset[tile]

                if sprite_name then
                    sprite(sprite_name, px, py)
                else
                    -- Fallback (debug)
                    rect(px, py, self.tile_size, self.tile_size)
                end
            end
        end
    end
end

-- Collision Check
function Map:is_solid(x, y)
    local tx = math.floor(x / self.tile_size) + 1
    local ty = math.floor(y / self.tile_size) + 1

    local row = self.data[ty]
    if not row then return false end

    local tile = row[tx]
    return tile == 1 -- 1 = solid
end

return Map
