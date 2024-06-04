function createTable(tableID) {
    let table = document.getElementById(tableID).getElementsByTagName('tbody')[0];

    const additionalRemuneration = js_vars.additional_remuneration;
    const additionalRemunerationEuros = js_vars.additional_remuneration_euros;
    const tasks = Object.keys(additionalRemuneration);
    const taskNames = js_vars.tasks
    for (let i = 0; i < tasks.length; i++) {
        let task = tasks[i]
        let row = table.insertRow();
        let cell1 = document.createElement('td');
        let cell2 = document.createElement('td');
        let cell3 = document.createElement('td');

        cell1.textContent = taskNames[task];
        cell2.textContent = additionalRemuneration[task] + ' ₮';
        cell3.textContent = additionalRemunerationEuros[task] + ' €';

        row.appendChild(cell1);
        row.appendChild(cell2);
        row.appendChild(cell3);

        table.appendChild(row);
    }
}