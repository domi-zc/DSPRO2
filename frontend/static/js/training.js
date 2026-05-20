const modeRadios = document.querySelectorAll('.tvc-mode-radio');
const diffRadios = document.querySelectorAll('.tvc-diff-radio');

const workoutGrid = document.querySelector('.tvc-training-workout-grid');
const exerciseGrid = document.querySelector('.tvc-training-exercise-grid');
const diffControlWrapper = document.querySelector('.tvc-training-workout-diff');
const workoutCards = document.querySelectorAll('.tvc-training-workout-grid .tvc-training-grid-card');

/**
 * Toggles visibility of grids and workout cards based on the currently selected 
 * mode (Workout vs Exercise) and difficulty toggles.
 */
function updateView() {
    const selectedMode = document.querySelector('.tvc-mode-radio:checked').value; 
    const selectedDiff = document.querySelector('.tvc-diff-radio:checked').value;

    if (selectedMode === 'workouts') {
        workoutGrid.style.display = 'flex'; 
        exerciseGrid.style.display = 'none';
        diffControlWrapper.style.display = 'flex';

        workoutCards.forEach(card => {
            card.style.display = (card.dataset.difficulty === selectedDiff) ? 'flex' : 'none';
        });
    } else {
        workoutGrid.style.display = 'none';
        exerciseGrid.style.display = 'flex'; 
        diffControlWrapper.style.display = 'none';
    }
}

/**
 * Updates the URL hash to reflect the current UI state for easy sharing or refreshing.
 */
function updateHash() {
    const selectedMode = document.querySelector('.tvc-mode-radio:checked').value;
    const selectedDiff = document.querySelector('.tvc-diff-radio:checked').value;

    window.location.hash = (selectedMode === 'workouts') ? `workout-${selectedDiff}` : `exercise`;
}

/**
 * Parses the URL hash on load/navigation to restore the correct UI state.
 */
function parseHash() {
    const hash = window.location.hash.substring(1); 
    if (!hash) return;

    if (hash === 'exercise') {
        document.querySelector('.tvc-radio-exercises').checked = true;
    } else if (hash.startsWith('workout')) {
        document.querySelector('.tvc-radio-workouts').checked = true;
        
        const diff = hash.split('-')[1];
        const validDiffs = ['easy', 'intermediate', 'hard', 'impossible'];
        
        if (validDiffs.includes(diff)) {
            document.querySelector(`.tvc-radio-${diff}`).checked = true;
        }
    }
}

modeRadios.forEach(radio => radio.addEventListener('change', () => { updateView(); updateHash(); }));
diffRadios.forEach(radio => radio.addEventListener('change', () => { updateView(); updateHash(); }));
window.addEventListener('hashchange', () => { parseHash(); updateView(); });

parseHash();
updateView();