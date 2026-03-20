-- Physics.lua


local Physics = {}

-- Apply Gravity
function Physics.apply_gravity(entity, gravity)
    entity.vy = entity.vy + (gravity or 0.5)
end

-- Apply Friction
function Physics.apply_friction(entity, friction)
    entity.vx = entity.vx * (1 - (friction or 0.1))
    entity.vy = entity.vy * (1 - (friction or 0.1))
end

-- Move entity and resolve collision against a Map
function Physics.move(entity, map)
    local new_x = entity.x + entity.vx
    local new_y = entity.y + entity.vy
    local w, h = entity.width, entity.height

    -- X-axis
    if not map:check_collision(new_x, entity.y, w, h) then
        entity.x = new_x
    else
        entity.vx = 0 -- Or Bounce
    end

    if not map:check_collision(entity.x, new_y, w, h) then
        entity.y = new_y
    else
        entity.vy = 0 -- Or Bounce
    end

end

return Physics


