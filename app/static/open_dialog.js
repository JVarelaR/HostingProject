const dialog = document.getElementById('createProjectDialog');
const openBtn = document.getElementById('openProjectDialog');
const closeBtn = document.getElementById('closeProjectDialog');

openBtn.addEventListener('click', () => {
    dialog.showModal(); 
});

closeBtn.addEventListener('click', () => {
    dialog.close();
});
