-- Shader_test.lua -----------------

function _update()
    if btnp("space") then
        flash(1.0, 0.5)
    end
end

function _draw()
    rectfill(100, 100, 200, 200, {255, 0, 0}) -- Red Rectangle

    --shader("darken", 0.2)

    --if btnp("space") then
        --flash(1.0, duration=0.5)
    --end
end
