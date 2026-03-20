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
    return tile ~= 0 -- Any Non-Zero tile is Solid
end

function Map:check_collision(x, y, w, h)
    local start_tx = math.floor(x / self.tile_size) + 1
    local end_tx = math.floor((x + w - 1) / self.tile_size) + 1 
    local start_ty = math.floor(y / self.tile_size) + 1
    local end_ty = math.floor((y + h - 1) / self.tile_size) + 1

    for ty = start_ty, end_ty do
        local row = self.data[ty]
        if row then
            for tx = start_tx, end_tx do
                if row[tx] ~= 0 then
                    return true
                end
            end
        end
    end
    return false
end

return Map
