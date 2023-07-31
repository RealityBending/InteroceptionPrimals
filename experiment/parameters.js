// experiment version
version = "1.0"
// Resting state duration in min
duratio = [8]
// HBC duration in sec
duration = [25, 35, 45, 20, 30, 40];
// [x, y, width, height] in pixels. Set to [0, 0, 0, 0] to disable.
marker1 = [0, 37, 100, 100]
// [x, y, width, height] in pixels. Set to [0, 0, 0, 0] to disable.
marker2 = [0, 0, 1920, 37]
// Record webcam?
record_webcam = false
// Are all the questions from the debriefing required?
questions_required = false
// Display raw data
raw_data = false

// Marker for photosensor
function create_marker(marker1, color = "black") {
    const html = `<div id="marker1" style="position: absolute; background-color: ${color};\
    left:${marker1[0]}px; top:${marker1[1]}px; \
    width:${marker1[2]}px; height:${marker1[3]}px";></div>`
    document.querySelector("body").insertAdjacentHTML("beforeend", html)
}

// Marker to cover the progress bar
function create_marker_2(marker2, color = "white") {
    const html = `<div id="marker2" style="position: absolute; background-color: ${color};\
    left:${marker2[0]}px; top:${marker2[1]}px; \
    width:${marker2[2]}px; height:${marker2[3]}px";></div>`
    document.querySelector("body").insertAdjacentHTML("beforeend", html)
}
