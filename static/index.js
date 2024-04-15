const nav = document.querySelector('.nav')
window.addEventListener('scroll', fixNav)

function fixNav() {
  if(window.scrollY > nav.offsetHeight + 150) {
    nav.classList.add('active')
  } else {
    nav.classList.remove('active')
  }
}

function loadTaskProgress() {
  var container = document.getElementById("container");
  taskObjs.forEach(function(task_obj) {

    var taskTrackDiv = document.createElement("div");
    taskTrackDiv.classList.add("task-track");

    var taskTitleDiv = document.createElement("div");
    taskTitleDiv.classList.add("task-title");
    taskTitleDiv.textContent = task_obj.title;

    var progressBarDiv = document.createElement("div");
    progressBarDiv.classList.add("progress-bar");
    var progressBarInnerDiv = document.createElement("div");
    progressBarInnerDiv.classList.add("progress-bar-inner");
    progressBarInnerDiv.style.width = (task_obj.progress * 100) + '%'; 
    progressBarDiv.appendChild(progressBarInnerDiv);

    var deadlineDiv = document.createElement("div");
    deadlineDiv.classList.add("deadline");
    deadlineDiv.textContent = task_obj.due;

    taskTrackDiv.appendChild(taskTitleDiv);
    taskTrackDiv.appendChild(progressBarDiv);
    taskTrackDiv.appendChild(deadlineDiv);

    // Append hero div to the container
    container.appendChild(taskTrackDiv);

  });
}
