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

-- (Check Collision)
-- Move entity and resolve collision against a Map
function Physics.move(entity, map)
    local new_x = entity.x + entity.vx
    local new_y = entity.y + entity.vy
    local w = entity.hit_w or entity.width 
    local h = entity.hit_h or entity.height
    local ox = entity.hit_offset_x or 0
    local oy = entity.hit_offset_y or 0

    -- X-axis (Can I Move Horizontally?)
    if not map:check_collision(new_x + ox, entity.y + oy, w, h) then
        -- Yes -> Move
        entity.x = new_x
    else
        if entity.bouncy then
            -- No -> Stop Horizontal Velocity
            Physics.bounce(entity, "x", 0.7)
        else
            entity.vx = 0
        end
    end

    if not map:check_collision(entity.x + ox, new_y + oy, w, h) then
        entity.y = new_y
    else
        if entity.bouncy then
            Physics.bounce(entity, "y", 0.7)
        else
            entity.vy = 0
        end
    end

end

function Physics.check_aabb(a, b)
    local ax = a.x + (a.hit_offset_x or 0)
    local ay = a.y + (a.hit_offset_y or 0)
    local aw = a.hit_w or a.width
    local ah = a.hit_h or a.height

    local bx = b.x + (b.hit_offset_x or 0)
    local by = b.y + (b.hit_offset_y or 0)
    local bw = b.hit_w or b.width
    local bh = b.hit_h or b.height

    return ax < bx + bw and
           ax + aw > bx and
           ay < by + bh and
           ay + ah > by
end

function Physics.resolve_aabb(a, b)
    -- Calculate Centers
    local aw = a.hit_w or a.width
    local ah = a.hit_h or a.height
    local bw = b.hit_w or b.width
    local bh = b.hit_h or b.height

    local ax = a.x + (a.hit_offset_x or 0) + aw/2
    local ay = a.y + (a.hit_offset_y or 0) + ah/2
    local bx = b.x + (b.hit_offset_x or 0) + bw/2
    local by = b.y + (b.hit_offset_y or 0) + bh/2

    -- Distance between Centers
    local dx = ax - bx
    local dy = ay - by

    -- Overlap Amount
    local overlap_x = ((aw/2) + (bw/2)) - math.abs(dx)
    local overlap_y = ((ah/2) + (bh/2)) - math.abs(dy)

    -- Resolve the Smaller Axis
    if overlap_x < overlap_y then
        -- Push on X axis
        if dx > 0 then
            a.x = a.x + overlap_x
        else
            a.x = a.x - overlap_x
        end
        a.vx = 0
    else
        -- Push on Y Axis
        if dy > 0 then
            a.y = a.y + overlap_y
        else
            a.y = a.y - overlap_y
        end

        a.y = math.floor(a.y + 0.01)

        -- Only bounce if Moving Downward
        if a.vy > 0 then
            a.vy = -a.vy * 0.8
        else
            a.vy = 0
        end
    end
end

function Physics.bounce(entity, axis, strength)
    strength = strength or 1
    if axis == "x" then
        entity.vx = -entity.vx * strength
    elseif axis == "y" then
        entity.vy = -entity.vy * strength
    end
end

return Physics


