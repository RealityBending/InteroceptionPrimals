var TAP_instructions = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus:
        "<p><b>Instructions</b></p>" +
        "<p>In the following task, you will need to tap the spacebar with any rhythm you prefer.</p>" +
        "<p>Please <b>maintain the speed of tapping</b> until the first trial is over.</p>" +
        "<p>Press the space bar to begin.</p>",
}

var TAP_break1 = {
    type: jsPsychHtmlButtonResponse,
    stimulus:
        "<p>Well done! Now tap with a <b>slower</b> rhythm.</p>" +
        "<p>Please <b>maintain the speed of tapping</b> until the second trial is over.</p>" +
        "<p>Press the button below to begin.</p>",
    choices: ["I'm ready"],
}

var TAP_break2 = {
    type: jsPsychHtmlButtonResponse,
    stimulus:
        "<p>Well done! This time tap with a <b>faster</b> rhythm than the first time.</p>" +
        "<p>Please <b>maintain the speed of tapping</b> until the third trial is over.</p>" +
        "<p>Press the button below to begin.</p>",
    choices: ["I'm ready"],
}

var TAP_influenced = {
    type: jsPsychMultipleSlider,
    questions: [
        {
            prompt: "<b>To what extent do you think your tapping rhythm was influenced by other things than your own will?</b>",
            name: "tap_influenced",
            min: 0,
            max: 1,
            step: 0.01,
            slider_start: 0.5,
            ticks: ["Not influenced", "Totally influenced"],
            required: true,
        },
    ],
    data: {
        screen: "TAP_influenced",
    },
}

var TAP_strategy = {
    type: jsPsychSurveyText,
    questions: [
        {
            prompt: "<b>Have you followed or been influenced by anything in particular while tapping (music, surrounding noise, internal sensations...)?</b>",
            placeholder: "Enter your answer here",
            name: "tap_strategy",
        },
    ],
    data: {
        screen: "TAP_strategy",
    },
}

function create_TAP_trial_1() {
    timeline.push({
        type: jsPsychHtmlKeyboardResponse,
        extensions: extensions,
        on_load: function () {
            create_marker(marker1, (color = "white"))
            create_marker_2(marker2);
        },
        stimulus: "Please continue tapping...",
        choices: [" "],
        css_classes: ["fixation"],
        data: {
            screen: "TAP_waiting_1",
            time_start: function () {
                return performance.now()
            },
        },
        on_finish: function (data) {
            document.querySelector("#marker1").remove()
            document.querySelector("#marker2").remove()
            data.duration =
                (performance.now() - data.time_start) /
                1000 /
                60
        },
    })

    timeline.push({
        type: jsPsychHtmlKeyboardResponse,
        extensions: extensions,
        on_load: function () {
            create_marker(marker1)
            create_marker_2(marker2);
        },
        stimulus: "",
        choices: "NO_KEYS",
        trial_duration: 50,
        css_classes: ["fixation"],
        data: {
            screen: "TAP_tapped_1",
            time_start: function () {
                return performance.now()
            },
        },
        on_finish: function (data) {
            document.querySelector("#marker1").remove()
            document.querySelector("#marker2").remove()
            data.duration =
                (performance.now() - data.time_start) /
                1000 /
                60
        },
    })
}

function create_TAP_trial_2() {
    timeline.push({
        type: jsPsychHtmlKeyboardResponse,
        extensions: extensions,
        on_load: function () {
            create_marker(marker1, (color = "white"))
            create_marker_2(marker2);
        },
        stimulus: "Please continue tapping...",
        choices: [" "],
        css_classes: ["fixation"],
        data: {
            screen: "TAP_waiting_2",
            time_start: function () {
                return performance.now()
            },
        },
        on_finish: function (data) {
            document.querySelector("#marker1").remove()
            document.querySelector("#marker2").remove()
            data.duration =
                (performance.now() - data.time_start) /
                1000 /
                60
        },
    })

    timeline.push({
        type: jsPsychHtmlKeyboardResponse,
        extensions: extensions,
        on_load: function () {
            create_marker(marker1)
            create_marker_2(marker2);
        },
        stimulus: "",
        choices: "NO_KEYS",
        trial_duration: 50,
        css_classes: ["fixation"],
        data: {
            screen: "TAP_tapped_2",
            time_start: function () {
                return performance.now()
            },
        },
        on_finish: function (data) {
            document.querySelector("#marker1").remove()
            document.querySelector("#marker2").remove()
            data.duration =
                (performance.now() - data.time_start) /
                1000 /
                60
        },
    })
}

function create_TAP_trial_3() {
    timeline.push({
        type: jsPsychHtmlKeyboardResponse,
        extensions: extensions,
        on_load: function () {
            create_marker(marker1, (color = "white"))
            create_marker_2(marker2);
        },
        stimulus: "Please continue tapping...",
        choices: [" "],
        css_classes: ["fixation"],
        data: {
            screen: "TAP_waiting_3",
            time_start: function () {
                return performance.now()
            },
        },
        on_finish: function (data) {
            document.querySelector("#marker1").remove()
            document.querySelector("#marker2").remove()
            data.duration =
                (performance.now() - data.time_start) /
                1000 /
                60
        },
    })

    timeline.push({
        type: jsPsychHtmlKeyboardResponse,
        extensions: extensions,
        on_load: function () {
            create_marker(marker1)
            create_marker_2(marker2);
        },
        stimulus: "",
        choices: "NO_KEYS",
        trial_duration: 50,
        css_classes: ["fixation"],
        data: {
            screen: "TAP_tapped_3",
            time_start: function () {
                return performance.now()
            },
        },
        on_finish: function (data) {
            document.querySelector("#marker1").remove()
            document.querySelector("#marker2").remove()
            data.duration =
                (performance.now() - data.time_start) /
                1000 /
                60
        },
    })
}
