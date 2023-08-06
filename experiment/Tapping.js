var TAP_instructions1 = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus:
        "<p><b>Instructions</b></p>" +
        "<p>In the following task, you will need to tap the spacebar with any rhythm you prefer.</p>" +
        "<p>Please <b>maintain the speed of tapping</b> until the trial is over.</p>" +
        "<p>Press the space bar to begin.</p>",
}

var TAP_instructions2 = {
    type: jsPsychHtmlButtonResponse,
    stimulus:
        "<p>Well done! Now tap with a different, but <b>slower</b> rhythm.</p>" +
        "<p>Please <b>maintain the speed of tapping</b> until the trial is over.</p>" +
        "<p>Press the button below to begin.</p>",
    choices: ["I'm ready"],
}

var TAP_instructions3 = {
    type: jsPsychHtmlButtonResponse,
    stimulus:
        "<p>Well done! This time tap with a different, but <b>faster</b> rhythm than the first time.</p>" +
        "<p>Please <b>maintain the speed of tapping</b> until the trial is over.</p>" +
        "<p>Press the button below to begin.</p>",
    choices: ["I'm ready"],
}

var TAP_instructions4 = {
    type: jsPsychHtmlButtonResponse,
    stimulus:
        "<p>Well done! For the final run, try to tap <b>arhythmically</b> by changing the timing between the presses and making it as much 'unpredictable' and 'random' as you can.</p>" +
        "<p>Do continue making new presses until the trial is over.</p>" +
        "<p>Press the button below to begin.</p>",
    choices: ["I'm ready"],
}

var TAP_influenced = {
    type: jsPsychMultipleSlider,
    questions: [
        {
            prompt: "To what extent do you think your tapping rhythm was influenced by other things (e.g., music, surrounding noise, internal sensations...) than your own will?",
            name: "TAP_influence",
            min: 0,
            max: 1,
            step: 0.01,
            slider_start: 0.5,
            ticks: ["Not influenced", "Totally influenced"],
            required: true,
        },
    ],
    data: {
        screen: "TAP_influence",
    },
}

var TAP_strategy = {
    type: jsPsychSurveyText,
    questions: [
        {
            prompt:
                "Please indicate if you followed or have been influenced by anything in particular while tapping (e.g., music, surrounding noise, internal sensations...)" +
                '<p><i>(e.g., "music in my head", "my breathing", "I was counting time in my head", ...)</i></p>',
            placeholder: "Please type here...",
            name: "TAP_strategy",
        },
    ],
    data: {
        screen: "TAP_strategy",
    },
}

function create_TAP_trial(
    screen = "TAP1_waiting",
    trial_duration = null,
    marker = "white"
) {
    return {
        type: jsPsychHtmlKeyboardResponse,
        extensions: extensions,
        on_load: function () {
            create_marker(marker1, (color = marker))
            create_marker_2(marker2)
        },
        stimulus: "Please continue tapping...",
        choices: [" "],
        trial_duration: trial_duration,
        css_classes: ["fixation"],
        data: {
            screen: screen,
            time_start: function () {
                return performance.now()
            },
        },
        on_finish: function (data) {
            document.querySelector("#marker1").remove()
            document.querySelector("#marker2").remove()
            data.duration = (performance.now() - data.time_start) / 1000 / 60
        },
    }
}
