-- Entities.lua 
entities = {}

function spawn(e)
    table.insert(entities, e)
    return e
end

function update_entities()
    for _,e in ipairs(entities) do
        if e.update then
            e:update()
        end
    end
end

function draw_entities()
    for _, e in ipairs(entities) do
        if e.draw then
            e:draw()
        end
    end
end

function clear_entities()
    entities = {}
end
