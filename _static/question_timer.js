function time_response(question_id, button_id) {
    let question = document.getElementById(question_id);
    let button = document.getElementById(button_id);
    console.log('hi');

    // This creates the variable that marks the start time
    let pageTimerID = -1;

    // This function automatically starts the timer when the page loads. 
    window.onload = function () {
        if (pageTimerID == -1) {
            pageTimerID = (new Date()).getTime();
            console.log(pageTimerID);
        }
    }

    // Stop timer when next button clicked
    button.onclick = function () {
        console.log('click!');
        // When finalize purchase clicked, current time recorded
        let currentTime = (new Date()).getTime();
        console.log(currentTime);
        // Timer start time then subtracted from current time 
        question.value = currentTime - pageTimerID;
        console.log(question.value);
    }
}