// Initialize variables
let currentQuestionIndex = 0;
const answers = [];

// Constants for classes
const LIST_GROUP_ITEM_CLASSES = 'list-group-item list-group-item-action d-flex align-items-center';
// Constants for selecting elements
const QUESTION_TEXT_ELEMENT = document.getElementById('question-text');
const ANSWERS_ELEMENT = document.getElementById('answers');

// Function to update the step indicator
function updateStepIndicator(currentStep) {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        step.classList.toggle('completed', index < currentStep);
        step.classList.toggle('active', index === currentStep);
    });
}

// Function to create an answer button
function createAnswerButton({ answerText, icon }) {
    const button = document.createElement('button');
    button.className = LIST_GROUP_ITEM_CLASSES;
    button.innerHTML = `<i class="${icon} mr-2"></i> ${answerText}`;
    button.onclick = () => handleAnswerSelection(answerText);
    return button;
}

// Function to load a question
function loadQuestion(index) {
    const { question, options } = quizData.questions[index];

    QUESTION_TEXT_ELEMENT.textContent = question;
    // Clear previous answers
    ANSWERS_ELEMENT.innerHTML = ''; 

    // Load answers as buttons
    options.forEach( ({text, icon}) => {
        ANSWERS_ELEMENT.appendChild(createAnswerButton({answerText: text, icon}));
    });
}

// Function to handle answer selection
function handleAnswerSelection(selectedText) {
    answers[currentQuestionIndex] = selectedText;
    updateHiddenInputWithAnswer(selectedText, currentQuestionIndex);

    if (currentQuestionIndex < quizData.questions.length - 1) {
        currentQuestionIndex++;
        updateStepIndicator(currentQuestionIndex);
        loadQuestion(currentQuestionIndex);
    } else {
        submitQuizForm();
    }
}

// Function to update the hidden input
function updateHiddenInputWithAnswer(answer, index) {
    document.getElementById(`answer${index + 1}`).value = answer;
}

// Handle form submission
function submitQuizForm() {
    document.getElementById('quiz-form').submit();
}

// Initialize the quiz
updateStepIndicator(0);
loadQuestion(currentQuestionIndex);
