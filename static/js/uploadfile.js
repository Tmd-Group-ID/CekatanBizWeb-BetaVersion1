document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_user_details')
        .then(response => response.json())
        .then(data => {
            document.getElementById('userId').textContent = data.userID;
            document.getElementById('userName').textContent = data.name;
            document.getElementById('userEmail').textContent = data.email;
        })
        .catch(error => console.error('Error fetching user details:', error));
});

function logout() {
    fetch('/logout', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Logout Successful!');
                window.location.href = '/';
            } else {
                alert('Logout failed: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
}

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const fileContent = document.getElementById('fileContent');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.backgroundColor = '#f8f9fa';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.backgroundColor = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.backgroundColor = '';
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    for (let file of files) {
        if (file.type === 'text/csv' || file.name.endsWith('.csv') || file.name.endsWith('.sql')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                displayFileContent(file.name, content);
            };
            reader.readAsText(file);

            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';

            const fileIcon = document.createElement('img');
            fileIcon.src = 'https://img.icons8.com/material-outlined/24/000000/document.png';
            fileItem.appendChild(fileIcon);

            const fileName = document.createElement('span');
            fileName.className = 'file-name';
            fileName.textContent = file.name;
            fileItem.appendChild(fileName);

            const deleteButton = document.createElement('button');
            deleteButton.className = 'delete-button';
            deleteButton.innerHTML = '&times;';
            deleteButton.onclick = () => {
                fileItem.remove();
                fileContent.innerHTML = '';
            };
            fileItem.appendChild(deleteButton);

            fileList.appendChild(fileItem);
        } else {
            alert('Unsupported file type');
        }
    }
}

function showDetailPopup() {
    document.getElementById('popup-detail').style.display = 'block';
}

function hideDetailPopup() {
    document.getElementById('popup-detail').style.display = 'none';
}

fileContent.onclick = function() {
    showDetailPopup();
};

window.onclick = function(event) {
    if (event.target == document.getElementById('popup-detail')) {
        hideDetailPopup();
    }
};

function displayFileContent(fileName, content) {
    if (fileName.endsWith('.csv')) {
        const rows = content.split('\n');
        const table = document.createElement('table');
        rows.forEach((row, index) => {
            const tr = document.createElement('tr');
            const cells = row.split(',');
            cells.forEach(cell => {
                const td = index === 0 ? document.createElement('th') : document.createElement('td');
                td.textContent = cell;
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
        fileContent.innerHTML = `<h3>Contents of ${fileName}</h3>`;
        fileContent.appendChild(table);
    } else {
        fileContent.innerHTML = `<h3>Contents of ${fileName}</h3><pre>${content}</pre>`;
    }
}
