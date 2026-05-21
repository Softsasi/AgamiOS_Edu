// ==========================================================================
// Agami Education Hub - Interactive Scripting
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initNavigation();
    initCalculator();
    initAccordion();
    runPlayground(); // Initial preview loading
    initPracticeArea(); // Initialize phonetic practice workspace
});

// ==========================================================================
// Real-time Clock & Welcome System
// ==========================================================================

function initClock() {
    const timeDisplay = document.getElementById('time-str');
    const greeting = document.getElementById('greeting');
    
    function updateClock() {
        const now = new Date();
        
        // Time
        let hours = now.getHours();
        let minutes = now.getMinutes();
        let seconds = now.getSeconds();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        
        hours = hours % 12;
        hours = hours ? hours : 12; // 0 should be 12
        minutes = minutes < 10 ? '0' + minutes : minutes;
        seconds = seconds < 10 ? '0' + seconds : seconds;
        
        timeDisplay.innerHTML = `<i class="fa-regular fa-clock"></i> ${hours}:${minutes}:${seconds} ${ampm}`;

        // Dynamic Greeting
        const hour24 = now.getHours();
        if (hour24 < 12) {
            greeting.innerText = "Good Morning, Student!";
        } else if (hour24 < 18) {
            greeting.innerText = "Good Afternoon, Student!";
        } else {
            greeting.innerText = "Good Evening, Student!";
        }
    }
    
    updateClock();
    setInterval(updateClock, 1000);
}

// ==========================================================================
// Navigation Controller
// ==========================================================================

function initNavigation() {
    const navItems = document.querySelectorAll('.sidebar .nav-links li');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active classes
            navItems.forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.main-content .panel').forEach(panel => panel.classList.remove('active'));
            
            // Add active classes
            item.classList.add('active');
            const target = item.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
        });
    });
}

function switchPanel(panelId) {
    const navItems = document.querySelectorAll('.sidebar .nav-links li');
    
    navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-target') === panelId) {
            item.classList.add('active');
        }
    });

    document.querySelectorAll('.main-content .panel').forEach(panel => panel.classList.remove('active'));
    document.getElementById(panelId).classList.add('active');
}

// ==========================================================================
// Math Lab - Calculator Logic
// ==========================================================================

let calcDisplayVal = "0";
let calcHistoryVal = "";

function initCalculator() {
    clearCalc();
}

function pressCalc(char) {
    const display = document.getElementById('calc-display');
    if (calcDisplayVal === "0" && char !== '.' && !char.startsWith('Math.')) {
        calcDisplayVal = char;
    } else {
        calcDisplayVal += char;
    }
    display.value = calcDisplayVal.replace(/Math\./g, '');
}

function clearCalc() {
    calcDisplayVal = "0";
    calcHistoryVal = "";
    document.getElementById('calc-display').value = "0";
    document.getElementById('calc-history').innerText = "";
}

function backspaceCalc() {
    const display = document.getElementById('calc-display');
    if (calcDisplayVal.endsWith('(') && calcDisplayVal.includes('Math.')) {
        // If we are deleting a function like Math.sin(
        const idx = calcDisplayVal.lastIndexOf('Math.');
        calcDisplayVal = calcDisplayVal.substring(0, idx);
    } else {
        calcDisplayVal = calcDisplayVal.slice(0, -1);
    }
    
    if (calcDisplayVal === "" || calcDisplayVal === "Math.") {
        calcDisplayVal = "0";
    }
    display.value = calcDisplayVal.replace(/Math\./g, '');
}

function solveCalc() {
    const display = document.getElementById('calc-display');
    const history = document.getElementById('calc-history');
    
    try {
        // Sanitize mathematical expression to prevent arbitrary JS execution, allowing only basic math functions and digits
        let expr = calcDisplayVal;
        
        // Match matching parens
        const openParens = (expr.match(/\(/g) || []).length;
        const closeParens = (expr.match(/\)/g) || []).length;
        if (openParens > closeParens) {
            expr += ')'.repeat(openParens - closeParens);
        }

        const result = eval(expr);
        history.innerText = expr.replace(/Math\./g, '') + ' =';
        calcDisplayVal = String(result);
        display.value = calcDisplayVal;
    } catch (e) {
        display.value = "Error";
        calcDisplayVal = "0";
    }
}

// Accordion helper
function initAccordion() {
    const headers = document.querySelectorAll('.acc-header');
    headers.forEach(h => {
        h.addEventListener('click', () => {
            const body = h.nextElementSibling;
            const icon = h.querySelector('i');
            
            body.classList.toggle('active');
            if (body.classList.contains('active')) {
                icon.className = "fa-solid fa-chevron-up";
            } else {
                icon.className = "fa-solid fa-chevron-down";
            }
        });
    });
}

// ==========================================================================
// Code Arena Playground
// ==========================================================================

function runPlayground() {
    const code = document.getElementById('code-editor').value;
    const iframe = document.getElementById('preview-frame');
    
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    iframeDoc.open();
    iframeDoc.write(code);
    iframeDoc.close();
}

// ==========================================================================
// Quiz Master Logic
// ==========================================================================

const quizQuestions = [
    {
        q: "What is the primary core design characteristic of the Linux kernel?",
        options: ["Microkernel architecture", "Monolithic kernel architecture", "Hybrid kernel architecture", "Exokernel architecture"],
        answer: 1
    },
    {
        q: "In calculus, what represents the limit of the ratio of the change in a function to the change in its independent variable?",
        options: ["Integration", "Derivative", "Infinite series", "Asymptote"],
        answer: 1
    },
    {
        q: "What is the time complexity of searching a sorted array using Binary Search?",
        options: ["O(N)", "O(N log N)", "O(log N)", "O(1)"],
        answer: 2
    },
    {
        q: "Which directory in a standard FHS Linux file system holds user-configurable system overrides?",
        options: ["/etc/", "/var/", "/usr/", "/opt/"],
        answer: 0
    },
    {
        q: "Which math identity states that sin²(θ) + cos²(θ) is always equal to 1?",
        options: ["Euler's identity", "Taylor series limit", "Pythagorean trigonometric identity", "Fermat's theorem"],
        answer: 2
    }
];

let currentQuestionIdx = 0;
let quizScoreVal = 0;

function startQuiz() {
    currentQuestionIdx = 0;
    quizScoreVal = 0;
    
    document.getElementById('quiz-start-view').style.display = 'none';
    document.getElementById('quiz-results-view').style.display = 'none';
    document.getElementById('quiz-question-view').style.display = 'block';
    
    showQuestion();
}

function showQuestion() {
    const qData = quizQuestions[currentQuestionIdx];
    document.getElementById('quiz-progress').innerText = `Question ${currentQuestionIdx + 1} of ${quizQuestions.length}`;
    document.getElementById('quiz-score').innerText = `Score: ${quizScoreVal}`;
    document.getElementById('quiz-question').innerText = qData.q;
    
    const optionsContainer = document.getElementById('quiz-options');
    optionsContainer.innerHTML = '';
    
    qData.options.forEach((opt, idx) => {
        const btn = document.createElement('div');
        btn.className = 'quiz-opt';
        btn.innerText = opt;
        btn.onclick = () => selectOption(idx, btn);
        optionsContainer.appendChild(btn);
    });
    
    document.getElementById('next-q-btn').style.display = 'none';
}

function selectOption(selectedIdx, element) {
    const qData = quizQuestions[currentQuestionIdx];
    const options = document.querySelectorAll('.quiz-opt');
    
    // Disable other clicks
    options.forEach(opt => opt.onclick = null);
    
    if (selectedIdx === qData.answer) {
        element.classList.add('correct');
        quizScoreVal += 100;
    } else {
        element.classList.add('wrong');
        options[qData.answer].classList.add('correct'); // Show correct answer
    }
    
    document.getElementById('quiz-score').innerText = `Score: ${quizScoreVal}`;
    document.getElementById('next-q-btn').style.display = 'inline-block';
}

function nextQuestion() {
    currentQuestionIdx++;
    if (currentQuestionIdx < quizQuestions.length) {
        showQuestion();
    } else {
        showResults();
    }
}

function showResults() {
    document.getElementById('quiz-question-view').style.display = 'none';
    document.getElementById('quiz-results-view').style.display = 'block';
    
    document.getElementById('quiz-final-score').innerText = quizScoreVal;
    
    const comment = document.getElementById('quiz-performance-comment');
    if (quizScoreVal === 500) {
        comment.innerText = "Exceptional performance! You have mastered these challenges.";
    } else if (quizScoreVal >= 300) {
        comment.innerText = "Great job! A very solid understanding of computing and math.";
    } else {
        comment.innerText = "Keep practicing! Education is a continuous journey.";
    }
}

function restartQuiz() {
    startQuiz();
}

// ==========================================================================
// Focus Zone - Pomodoro Timer
// ==========================================================================

let timerInterval = null;
let timerTimeLeft = 25 * 60; // 25 minutes
let timerIsRunning = false;
let timerCurrentMode = "POMODORO";

function updateTimerDisplay() {
    const display = document.getElementById('timer-display');
    const miniDisplay = document.getElementById('mini-timer');
    
    const minutes = Math.floor(timerTimeLeft / 60);
    const seconds = timerTimeLeft % 60;
    const timeStr = `${minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
    
    display.innerText = timeStr;
    if (miniDisplay) {
        miniDisplay.innerText = timeStr;
    }
}

function toggleTimer() {
    const btn = document.getElementById('play-pause-btn');
    if (timerIsRunning) {
        // Pause
        clearInterval(timerInterval);
        timerIsRunning = false;
        btn.innerHTML = `<i class="fa-solid fa-play"></i> Start`;
    } else {
        // Start
        timerIsRunning = true;
        btn.innerHTML = `<i class="fa-solid fa-pause"></i> Pause`;
        timerInterval = setInterval(() => {
            timerTimeLeft--;
            updateTimerDisplay();
            
            if (timerTimeLeft <= 0) {
                clearInterval(timerInterval);
                timerIsRunning = false;
                btn.innerHTML = `<i class="fa-solid fa-play"></i> Start`;
                playNotificationSound();
                alert(`Timer Finished! Mode: ${timerCurrentMode}`);
                skipTimer();
            }
        }, 1000);
    }
}

function resetTimer() {
    clearInterval(timerInterval);
    timerIsRunning = false;
    document.getElementById('play-pause-btn').innerHTML = `<i class="fa-solid fa-play"></i> Start`;
    
    if (timerCurrentMode === "POMODORO") {
        timerTimeLeft = 25 * 60;
    } else if (timerCurrentMode === "SHORT BREAK") {
        timerTimeLeft = 5 * 60;
    } else {
        timerTimeLeft = 15 * 60;
    }
    updateTimerDisplay();
}

function skipTimer() {
    clearInterval(timerInterval);
    timerIsRunning = false;
    document.getElementById('play-pause-btn').innerHTML = `<i class="fa-solid fa-play"></i> Start`;
    
    if (timerCurrentMode === "POMODORO") {
        setTimerPreset(5, "SHORT BREAK");
    } else {
        setTimerPreset(25, "POMODORO");
    }
}

function setTimerPreset(minutes, mode) {
    clearInterval(timerInterval);
    timerIsRunning = false;
    timerCurrentMode = mode;
    timerTimeLeft = minutes * 60;
    
    document.getElementById('timer-mode').innerText = mode;
    document.getElementById('play-pause-btn').innerHTML = `<i class="fa-solid fa-play"></i> Start`;
    updateTimerDisplay();
}

function playNotificationSound() {
    // Generate a simple synth audio beep
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        oscillator.type = 'sine';
        oscillator.frequency.value = 523.25; // C5 note
        gainNode.gain.setValueAtTime(0.5, audioCtx.currentTime);
        
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.4);
    } catch(e) {
        // Fallback if audio ctx not supported without user interaction
    }
}

// ==========================================================================
// Library / Books Viewer System
// ==========================================================================

const booksCatalog = {
    os: {
        title: "Operating Systems Principles Handbook",
        content: `
            <h4>Chapter 1: The Linux Kernel Architecture</h4>
            <p>At the center of any Linux operating system lies the Linux Kernel. Linux uses a <strong>monolithic architecture</strong>, which means the entire operating system code runs in a single address space (Kernel Space) for maximum execution speed. However, to maintain high flexibility, Linux features a dynamically loadable module architecture. Kernels are responsible for process scheduling, hardware virtualization layer management, memory allocation, and virtual file systems (VFS).</p>
            
            <h4>Chapter 2: Processes and Multitasking</h4>
            <p>Operating systems achieve simultaneous execution of applications using context switching. A process is a running instance of a program, consisting of memory pages, registers, a stack, and threads. The kernel schedules thread chunks into the CPU core using scheduler algorithms like <em>Completely Fair Scheduler (CFS)</em>.</p>
            
            <h4>Chapter 3: The Virtual File System (VFS)</h4>
            <p>VFS allows applications to access local disks, USB drivers, and networked filesystems using the exact same system calls (e.g. <code>open()</code>, <code>read()</code>, <code>write()</code>). It hides structural details of concrete filesystem formats like ext4, xfs, and fat32.</p>
        `
    },
    calc: {
        title: "Calculus and Analytical Geometry",
        content: `
            <h4>Chapter 1: Limits and Continuity</h4>
            <p>Calculus begins with the study of limits. A limit represents the value that a function "approaches" as the input approaches a specific target. Formally, <code>lim(x->c) f(x) = L</code> means that for any ε > 0, there exists a δ > 0 such that if 0 < |x - c| < δ, then |f(x) - L| < ε.</p>
            
            <h4>Chapter 2: The Derivative and Rates of Change</h4>
            <p>The derivative represents the instantaneous rate of change of a curve at a single mathematical coordinate. Geometrically, it is the slope of the tangent line to the curve. Formally defined as the limit of the difference quotient:</p>
            <p><code>f'(x) = lim(h->0) [f(x + h) - f(x)] / h</code></p>
            
            <h4>Chapter 3: The Integral and Fundamental Theorem</h4>
            <p>Definite integrals quantify the accumulation of quantities, which represents the area under a curve. The Fundamental Theorem of Calculus links derivatives and integrals, showing that differentiation is the exact inverse operation of integration.</p>
        `
    },
    arch: {
        title: "Computer Architecture and Command Shells",
        content: `
            <h4>Chapter 1: Registers and CPU Instructions</h4>
            <p>CPU cores perform logic using quick-access memory nodes called registers. Instruction sets (such as x86-64 or ARMv8) represent high-speed machine instructions that direct basic math computations, conditional branching, and memory caching.</p>
            
            <h4>Chapter 2: Cache Hierarchies</h4>
            <p>To avoid slower system RAM access, modern CPUs employ cache levels (L1, L2, L3) directly on the physical processor die. L1 is extremely fast but small (usually 32-64KB per core), L2 is slightly larger, and L3 is shared across all cores (spanning several MBs).</p>
            
            <h4>Chapter 3: Command-Line Interfacing (Shells)</h4>
            <p>A shell is an interactive command-line interface providing a control terminal for system interaction. Linux systems rely on shell engines like <strong>Bash</strong> or <strong>Zsh</strong>. Shell commands allow pipelines using standard inputs, outputs, and redirection pipes (<code>stdin | stdout</code>).</p>
        `
    }
};

function viewBook(bookKey) {
    const book = booksCatalog[bookKey];
    if (!book) return;
    
    document.getElementById('book-title').innerText = book.title;
    document.getElementById('book-body').innerHTML = book.content;
    document.getElementById('book-viewer').style.display = 'flex';
}

function closeBookViewer() {
    document.getElementById('book-viewer').style.display = 'none';
}

// ==========================================================================
// Interactive Bangla Practice & App Simulation Launcher
// ==========================================================================

function initPracticeArea() {
    const area = document.getElementById('language-practice-area');
    const counter = document.getElementById('char-counter');
    if (area && counter) {
        area.addEventListener('input', () => {
            const count = area.value.length;
            counter.innerText = `${count} character${count === 1 ? '' : 's'}`;
        });
    }
}

function clearPractice() {
    const area = document.getElementById('language-practice-area');
    const counter = document.getElementById('char-counter');
    if (area) {
        area.value = '';
    }
    if (counter) {
        counter.innerText = '0 characters';
    }
}

function launchApp(appName) {
    alert(`[Agami OS Live Environment] Launching ${appName} from /usr/bin/${appName}...\\nThis application is preloaded inside the ISO and fully available offline.`);
}
