document.addEventListener('DOMContentLoaded', (event) => {
    // Function to show or hide sections
    function toggleSection(sectionToShow) {
        const gameSection = document.getElementById('game-section');
        const quizSection = document.getElementById('quiz-section');
        const gameBoard = document.querySelector('.game-board');
        const quizBoard = document.querySelector('.quiz-board');

        // Hide both sections first
        gameSection.style.display = 'none';
        quizSection.style.display = 'none';

        // Reset the styles for both boards
        gameBoard.style.backgroundColor = '';
        quizBoard.style.backgroundColor = '';
        gameBoard.style.zIndex = '0';
        quizBoard.style.zIndex = '0';

        // Show the selected section and highlight the board
        if (sectionToShow === 'game') {
            gameSection.style.display = 'block';
            gameBoard.style.backgroundColor = '#C8D1D2'; // Active color
            gameBoard.style.zIndex = '10';
        } else if (sectionToShow === 'quiz') {
            quizSection.style.display = 'block';
            quizBoard.style.backgroundColor = '#C8D1D2'; // Active color
            quizBoard.style.zIndex = '10';
        }
    }

    // Event listeners for the leaderboard options
    document.querySelector('.game-board').addEventListener('click', function () {
        toggleSection('game');
    });

    document.querySelector('.quiz-board').addEventListener('click', function () {
        toggleSection('quiz');
    });

    // Initialize with the game-board section visible and highlighted
    toggleSection('game');
});
