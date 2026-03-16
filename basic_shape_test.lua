function _init()
    circleY = 200
    rectY = 100
    lineY = 300
end

function _update()
    circleY = circleY + 2
    rectY = rectY + 2
    lineY = lineY + 2
    if circleY > 400 then
        circleY = 200
    end
    if rectY > 400 then
        rectY = 200
    end
    if lineY > 400 then
        lineY = 200
    end
end

function _draw()
    print("Hello Byron")
    circle(100, circleY)
    rect(200, rectY)
    line(300, 300, 400, lineY)
end
