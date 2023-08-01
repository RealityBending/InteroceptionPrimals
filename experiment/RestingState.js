// Resting state questionnaire
var items = [
    "I had busy thoughts",
    "I had rapidly switching thoughts",
    "I had difficulty holding onto my thoughts",
    "I thought about others",
    "I thought about people I like",
    "I placed myself in other people's shoes",
    "I thought about my feelings",
    "I thought about my behaviour",
    "I thought about myself",
    "I thought about things I need to do",
    "I thought about solving problems",
    "I thought about the future",
    "I felt sleepy",
    "I felt tired",
    "I had difficulty staying awake",
    "I felt comfortable",
    "I felt happy",
    "I felt relaxed",
    "I was conscious of my body",
    "I thought about my heartbeat",
    "I thought about my breathing",
]
var dimensions = [
    "DoM_1",
    "DoM_2",
    "DoM_3",
    "ToM_1",
    "ToM_2",
    "ToM_3",
    "Self_1",
    "Self_2",
    "Self_3",
    "Plan_1",
    "Plan_2",
    "Plan_3",
    "Sleep_1",
    "Sleep_2",
    "Sleep_3",
    "Comfort_1",
    "Comfort_2",
    "Comfort_3",
    "SomA_1",
    "SomA_2",
    "SomA_3",
]
var check_items = [
    "I had my eyes closed",
    "I was able to rate the statements above",
]

var RS_instructions = {
    type: jsPsychHtmlButtonResponse,
    stimulus:
        "<p><b>Instructions</b></p>" +
        // Don't give exact time so that participants don't count
        "<p>A rest period of about 8 minutes is about to start.</p>" +
        "<p>Simply <b>relax</b> and remain seated quietly with your eyes closed. Please try <b>not to fall asleep</b>.</p> " +
        "<p>Once the resting period is over, you will hear a beep. You can then open your eyes and proceed.</p>" +
        "<p>Once you are ready, close your eyes. The rest period will shortly begin.</p>",
    choices: ["Continue"],
}

// Tasks ======================================================================
// Create blank grey screen just before rest period
var RS_buffer = {
    type: jsPsychHtmlKeyboardResponse,
    on_start: function () {
        document.body.style.backgroundColor = "#808080"
        document.body.style.cursor = "none"
        create_marker(marker1, (color = "white"))
    },
    on_finish: function () {
        document.querySelector("#marker1").remove()
    },
    stimulus: "",
    choices: ["s"],
    trial_duration: 1000, // 1 second
    css_classes: ["RS_fixation"],
}

// Create blank grey screen for resting state
var RS_task = {
    type: jsPsychHtmlKeyboardResponse,
    on_load: function () {
        create_marker(marker1)
        create_marker_2(marker2)
    },
    stimulus: "<p style='font-size:150px;'>+</p>",
    choices: ["s"],
    trial_duration: 8 * 60 * 1000,
    css_classes: ["fixation"],
    data: {
        screen: "RS_resting",
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

// Play beep
var RS_beep = {
    type: jsPsychAudioButtonResponse,
    on_start: function () {
        document.body.style.backgroundColor = "#FFFFFF"
        document.body.style.cursor = "auto"
    },
    stimulus: ["utils/beep.mp3"],
    prompt: "<p>It's over! Please press continue.</p>",
    choices: ["Continue"],
}
// Debriefing Questionnaire ========================================================================

var scale = ["Completely Disagree", "Completely Agree"]

// Create list of formatted questions into the list
var questions = []
for (const [index, element] of items.entries()) {
    questions.push({
        prompt: "<b>" + element + "</b>",
        name: dimensions[index],
        ticks: scale,
        required: false,
        min: 0,
        max: 1,
        step: 0.01,
        slider_start: 0.5,
    })
}
// Randomize order (comment this out to deactivate the randomization)
questions = questions.sort(() => Math.random() - 0.5)

// Do the same for validation items to add them at the end (not randomized)
for (const [index, element] of check_items.entries()) {
    questions.push({
        prompt: "<b>" + element + "</b>",
        name: "Check_" + (index + 1),
        ticks: scale,
        required: false,
        min: 0,
        max: 1,
        step: 0.01,
        slider_start: 0.5,
    })
}

// Make questionnaire task
var RS_questionnaire = {
    type: jsPsychMultipleSlider, // this is a custom plugin in utils
    questions: questions,
    randomize_question_order: false,
    preamble:
        "<p>We are interested in the potential feelings and thoughts you may have experienced during the resting period.</p>" +
        "<p>Please indicate the extent to which you agree with each statement.</p><br /><br/> ",
    require_movement: false,
    slider_width: null,
    data: {
        screen: "RS_assessment",
    },
}
