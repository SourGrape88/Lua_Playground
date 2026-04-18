-- Shader_test.lua -----------------

function _draw()
    rectfill(100, 100, 200, 200, {255, 0, 0}) -- Red Rectangle

    shader("darken", 0.5)
    print(shader)
end
