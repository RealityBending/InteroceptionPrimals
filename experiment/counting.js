// Instructions
var HBC_instructions = {
    type: jsPsychHtmlButtonResponse,
    stimulus:
        "<h2>Heartbeat Counting Task</h2>" +
        "<p><b>Instructions</b></p>" +
        // Don't give exact time so that participants don't count
        "<p>In the following task, you will need to count and report the number of heartbeats during several intervals.</p>" +
        "<p>Simply <b>relax</b> and remain seated quietly while <b>counting your heartbeat without physically measuring it</b>.</p> " +
        "<p>The interval will start with a '3-2-1' signal, after which you need to count your heartbeats until you hear a beep.</p> " +
        "<p>Questions will then be displayed for you to answer.</p>",
    choices: ["I am ready"],
}

function HBC() {
    // Create an array to store the trial order
    var trialOrder = []

    // Populate the trial order array
    for (let i = 0; i < duration.length; i++) {
        trialOrder.push(i)
    }

    // Shuffle the trial order
    var shuffledTrialOrder =
        jsPsych.randomization.shuffle(trialOrder)

    // Define the pause duration (in milliseconds)
    var pauseDuration = 3000 // 3 seconds

    // Iterate through the shuffled trial order
    for (let i = 0; i < shuffledTrialOrder.length; i++) {
        var trialIndex = shuffledTrialOrder[i]

        // Create blank grey screen with countdown just before each trial
        var buffer = {
            type: jsPsychHtmlKeyboardResponse,
            on_start: function () {
                document.body.style.backgroundColor = "#808080"
                document.body.style.cursor = "none"
                create_marker(marker1, (color = "white"))
            },
            on_finish: function () {
                document.querySelector("#marker1").remove()
                jsPsych.finishTrial() // Explicitly advance to the next trial
            },
            stimulus: function () {
                var count = 3
                var countdownHTML =
                    '<p style="font-size: 100px; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">' +
                    count +
                    "</p>"
                var countdownInterval = setInterval(function () {
                    count--
                    if (count > 0) {
                        document.querySelector(
                            "#countdown"
                        ).innerHTML = count
                    } else {
                        clearInterval(countdownInterval)
                    }
                }, 1000) // Update countdown every second
                return (
                    '<div id="countdown" style="font-size: 100px;">' +
                    count +
                    "</div>"
                )
            },
            choices: "NO_KEYS",
            trial_duration: pauseDuration, // Pause duration before the trial starts
            css_classes: ["fixation"],
        }
        timeline.push(buffer)

        timeline.push({
            type: jsPsychHtmlKeyboardResponse,
            extensions: extensions,
            on_load: function () {
                create_marker(marker1)
            },
            stimulus: "<p style='font-size:150px;'>+</p>",
            choices: ["s"],
            trial_duration: duration[trialIndex] * 1000,
            css_classes: ["fixation"],
            data: {
                screen: "hct_interval",
                time_start: function () {
                    return performance.now()
                },
            },
            on_finish: function (data) {
                document.querySelector("#marker1").remove()
                data.duration =
                    (performance.now() - data.time_start) /
                    1000 /
                    60
            },
        })

        // Beep after each trial
        var audio_trigger = {
            type: jsPsychAudioButtonResponse,
            on_start: function () {
                document.body.style.backgroundColor = "#FFFFFF"
                document.body.style.cursor = "auto"
            },
            stimulus: beep,
            prompt: "<p>This trial is over, please press continue.</p>",
            choices: ["Continue"],
        }
        timeline.push(audio_trigger)

        // Add the first question
        timeline.push({
            type: jsPsychSurveyText,
            questions: [
                {
                    prompt: "<b>How many heartbeats did you count?</b>",
                    placeholder: "Enter number",
                    name: "hct_count",
                },
            ],
            data: {
                screen: "hct_count",
            },
        })

        // Add the second question as jsPsychMultipleSlider
        timeline.push({
            type: jsPsychMultipleSlider,
            questions: [
                {
                    prompt: "<b>How confident are you that this number is correct?</b>",
                    name: "hct_confidence",
                    min: 0,
                    max: 1,
                    step: 0.01,
                    slider_start: 0.5,
                    ticks: ["Not confident", "Very confident"],
                    required: true,
                },
            ],
            data: {
                screen: "hct_confidence",
            },
        })
    }
}