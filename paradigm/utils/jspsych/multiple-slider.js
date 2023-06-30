var jsPsychMultipleSlider = (function(jspsych) {
  'use strict';

  const info = {
    name: 'multiple-slider',
    description: '',
    parameters: {
      questions: {
        type: jspsych.ParameterType.COMPLEX,
        array: true,
        pretty_name: 'Questions',
        nested: {
          /** The HTML string to be displayed */
          stimulus: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Stimulus",
              default: "",
          },
          prompt: {
            type: jspsych.ParameterType.STRING,
            pretty_name: 'Prompt',
            default: undefined,
            description: 'Content to be displayed below the stimulus and above the slider'
          },
          // Labels to appear to the left of each slider, one in line with the top row ticks and one in line with the bottom
          labels: {
            type: jspsych.ParameterType.STRING,
            pretty_name:'Labels',
            default: [],
            array: true,
            description: 'Labels of the sliders.',
          },
          /** Array containing the ticks to show along the slider. Ticks will be displayed at equidistant locations along the slider. Note this parameter is called Labels in the original plugin.*/
          ticks: {
            type: jspsych.ParameterType.HTML_STRING,
            pretty_name:'Ticks',
            default: [],
            array: true,
            description: 'Ticks of the sliders.',
          },
          name: {
            type: jspsych.ParameterType.STRING,
            pretty_name: 'Question Name',
            default: '',
            description: 'Controls the name of data values associated with this question'
          },
          min: {
            type: jspsych.ParameterType.INT,
            pretty_name: 'Min slider',
            default: 0,
            description: 'Sets the minimum value of the slider.'
          },
          max: {
            type: jspsych.ParameterType.INT,
            pretty_name: 'Max slider',
            default: 100,
            description: 'Sets the maximum value of the slider',
          },
          slider_start: {
            type: jspsych.ParameterType.INT,
            pretty_name: 'Slider starting value',
            default: 50,
            description: 'Sets the starting value of the slider',
          },
          step: {
            type: jspsych.ParameterType.INT,
            pretty_name: 'Step',
            default: 1,
            description: 'Sets the step of the slider'
          },
        },
      },
      randomize_question_order: {
        type: jspsych.ParameterType.BOOL,
        pretty_name: 'Randomize Question Order',
        default: false,
        description: 'If true, the order of the questions will be randomized'
      },
      preamble: {
        type: jspsych.ParameterType.HTML_STRING,
        pretty_name: 'Preamble',
        default: null,
        description: 'String to display at top of the page.'
      },
      button_label: {
        type: jspsych.ParameterType.STRING,
        pretty_name: 'Button label',
        default:  'Continue',
        description: 'Label of the button.'
      },
      autocomplete: {
        type: jspsych.ParameterType.BOOL,
        pretty_name: 'Allow autocomplete',
        default: false,
        description: "Setting this to true will enable browser auto-complete or auto-fill for the form."
      },
      require_movement: {
        type: jspsych.ParameterType.BOOL,
        pretty_name: 'Require movement',
        default: false,
        description: 'If true, the participant will have to move the slider before continuing.'
      },
      slider_width: {
        type: jspsych.ParameterType.INT,
        pretty_name:'Slider width',
        default: 500,
        description: 'Width of the slider in pixels.'
      },
    },
  }

  class MultipleSliderPlugin {
    constructor(jsPsych) {
      this.jsPsych = jsPsych;
    }

  trial(display_element, trial) {

    // half of the thumb width value from jspsych.css, used to adjust the label positions
    var half_thumb_width = 7.5;

    var html = '<div id="jspsych-html-slider-response-wrapper" style="margin: 100px 0px;">';

    html += '<div class="jspsych-html-slider-response-container" style="position:relative; margin: 0 auto 3em auto; ';
    if(trial.slider_width !== null){
      html += 'width:'+trial.slider_width+'px;';
    } else {
      html += 'width:auto;';
    }
    html += '">';

    // show preamble text
    if(trial.preamble !== null){
      // html += '<div style="position: relative; left: calc(-20%); width:130%" id="jspsych-multiple-slider-preamble" class="jspsych-multiple-slider-preamble">'+trial.preamble+'</div><br>';
      html += '<div style="position: relative; width:100%" id="jspsych-multiple-slider-preamble" class="jspsych-multiple-slider-preamble">'+trial.preamble+'</div><br>';
    }

    if (trial.autocomplete) {
      html += '<form id="jspsych-multiple-slider-form">';
    } else {
      html += '<form id="jspsych-multiple-slider-form" autocomplete="off">';
    }

    // add sliders questions ///
    // generate question order. this is randomized here as opposed to randomizing the order of trial.questions
    // so that the data are always associated with the same question regardless of order
    var question_order = [];
    for(var i=0; i<trial.questions.length; i++){
      question_order.push(i);
    }
    if(trial.randomize_question_order){
      // const shuffle = () => {
      //   question_order = this.jsPsych.randomization.shuffle(question_order);
      // }
      question_order = this.jsPsych.randomization.shuffle(question_order);
    }

    for (var i = 0; i < trial.questions.length; i++) {
      var question = trial.questions[question_order[i]];

      // Add stimulus
      html += '<div id="jspsych-html-slider-response-stimulus">' + question.stimulus + '</div>';

      // add prompt
      html += '<label class="jspsych-multiple-slider-statement">' + question.prompt + '</label><br>';

      // add top left label
      if (question.labels.length > 0) {
      html += '<div style="font-size: 100%; font-weight: bold; position: absolute; left: calc(-15%)">' + question.labels[0] + '</div>'}
      // html += '<div style="font-size: 100%; font-weight: bold; position: absolute; right: calc(-25%)">' + question.labels[1] + '</div>'

      // Add top row ticks in ascending order
      // for(var j=0; j < question.ticks.length; j++){
      //   var label_width_perc = 95/(question.ticks.length-1);
      //   var percent_of_range = 5 + j * (95/(question.ticks.length - 1));
      //   var percent_dist_from_center = ((percent_of_range-50)/50)*100;
      //   var offset = (percent_dist_from_center * half_thumb_width)/100;
      //   html += '<div style="border: 1px solid transparent; position: absolute; '+
      //   'left:calc('+percent_of_range+'% - ('+label_width_perc+'% / 2) - '+offset+'px); text-align: center; width: '+label_width_perc+'%;">';
      //   html += '<span style="text-align: center; font-size: 100%;">'+question.ticks[j]+'</span>';
      //   html += '</div>'
      // }
      // html += '<br>'

      // add sliders
      // html += '<input style="width: 95%; float: right" type="range" class="jspsych-slider" value="'+(question.slider_start)+'" min="'+question.min+'" max="'+question.max+'" step="'+question.step+'" id="jspsych-html-slider-response-response-'+i+'" name="Q'+i+'" data-name="'+question.name+'"></input><br>';
      html += '<input style="width: 100%" type="range" class="jspsych-slider" value="'+(question.slider_start)+'" min="'+question.min+'" max="'+question.max+'" step="'+question.step+'" id="jspsych-html-slider-response-response-'+i+'" name="Q'+i+'" data-name="'+question.name+'"></input><br>';

      // add bottom left label
      if (question.labels.length > 0) {
      html += '<div style="font-size: 100%; font-weight: bold; position: absolute; left: calc(-15%)">' + question.labels[1] + '</div>'}

      // Bottom row ticks - reverse the ticks list and then do the same thing as before
      // var reversed_ticks = question.ticks.reverse()
      // for(var j=0; j < question.ticks.length; j++){
      //   var label_width_perc = 95/(question.ticks.length-1);
      //   var percent_of_range = 5 + j * (95/(question.ticks.length - 1));
      //   var percent_dist_from_center = ((percent_of_range-50)/50)*100;
      //   var offset = (percent_dist_from_center * half_thumb_width)/100;
      //   html += '<div style="border: 1px solid transparent; display: inline-block; position: absolute; '+
      //   'left:calc('+percent_of_range+'% - ('+label_width_perc+'% / 2) - '+offset+'px); text-align: center; width: '+label_width_perc+'%;">';
      //   html += '<span style="text-align: center; font-size: 80%;">'+reversed_ticks[j]+'</span>';
      //   html += '</div>'
      // }

      for(var j=0; j < question.ticks.length; j++){
        var label_width_perc = 100/(question.ticks.length-1);
        var percent_of_range = j * (100/(question.ticks.length - 1));
        var percent_dist_from_center = ((percent_of_range-50)/50)*100;
        var offset = (percent_dist_from_center * half_thumb_width)/100;
        html += '<div style="border: 1px solid transparent; position: absolute; '+
        'left:calc('+percent_of_range+'% - ('+label_width_perc+'% / 2) - '+offset+'px); text-align: center; width: '+label_width_perc+'%;">';
        html += '<span style="text-align: center; font-size: 100%;">'+question.ticks[j]+'</span>';
        html += '</div>'
      }

      // add some space between the sliders
      html += '<br/><br/>';
    }

    // add some space before the next button
    html += '<br/>'

    // add submit button
    html += '<input type="submit" id="jspsych-multiple-slider-next" class="jspsych-multiple-slider jspsych-btn" value="'+trial.button_label+'"></input>';

    html += '</form>'

    html += '</div>';
    html += '</div>';

    display_element.innerHTML = html;

    // require responses
    if (trial.require_movement) {
      // disable by default the next button
      document.getElementById('jspsych-multiple-slider-next').disabled = true;

      // check whether all sliders have been clicked
      function check_reponses() {
        var all_sliders = document.querySelectorAll('.jspsych-slider');
        var all_clicked = true;
        for (var i=0; i<all_sliders.length; i++) {
            if (!all_sliders[i].classList.contains("clicked")) {
                // if any one slider doesn't have the 'clicked' class, then we know that they haven't all been clicked
                all_clicked = false;
                break;
            }
        }
        if (all_clicked) {
          // if they have been clicked then enable the next button
          document.getElementById('jspsych-multiple-slider-next').disabled = false;
        }
      }

      var all_sliders = document.querySelectorAll('.jspsych-slider');
      all_sliders.forEach(function(slider) {
          slider.addEventListener('click', function() {
            slider.classList.add("clicked"); // record the fact that this slider has been clicked
            check_reponses(); // each time a slider is clicked, check to see if they've all been clicked
          });
          slider.addEventListener('change', function() {
            slider.classList.add("clicked"); // record the fact that this slider has been clicked
            check_reponses(); // each time a slider is clicked, check to see if they've all been clicked
          });
      });
    }

    // display_element.querySelector('#jspsych-multiple-slider-form').addEventListener('submit', function(e){
    // Josh de Leeuw responded to my post in the support thread and told me to replace the line above with the line below but
    // I still have the same error message as I did before
    display_element.querySelector('#jspsych-multiple-slider-form').addEventListener('submit', (e) => {
      e.preventDefault();
      // measure response time
      var endTime = performance.now();
      var response_time = endTime - startTime;

      // create object to hold responses
      var question_data = {};

      // hold responses
      var matches = display_element.querySelectorAll('input[type="range"]');

      // store responses
      for(var index = 0; index < matches.length; index++){
        var id = matches[index].name;
        var response = matches[index].valueAsNumber;
        var obje = {};
        if(matches[index].attributes['data-name'].value !== ''){
          var name = matches[index].attributes['data-name'].value;
        } else {
          var name = id;
        }
        obje[name] = response;
        Object.assign(question_data, obje);
      }

      // save data
      var trial_data = {
        rt: response_time,
        response: JSON.stringify(question_data),
        question_order: JSON.stringify(question_order)
      };

      display_element.innerHTML = '';

      // next trial
      this.jsPsych.finishTrial(trial_data);
    });

    var startTime = performance.now();
  };
}

MultipleSliderPlugin.info = info;

return MultipleSliderPlugin;

})(jsPsychModule);
