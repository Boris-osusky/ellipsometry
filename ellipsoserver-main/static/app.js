const elInputAngle = document.getElementById('input-angle');
const elXfrom = document.getElementById('input-xfrom');
const elXto = document.getElementById('input-xto');
const elErrors = document.getElementById('errors');
const elErrorsSelected = document.getElementById('selected-errors');
const elBtnNewCauchy = document.getElementById('btn-newcauchy');
const elBtnNewConstant = document.getElementById('btn-newconstant');
const elTableSelected = document.getElementById('table-selected');


let requestBody = {
    ustart: 207,
    uend: 826,
    uangle: 70,
    uinc: 2,
    unit: 'nm',
    materials: [
        {
            'type': 'constant',
            'n' : 1,
            'k' : 0,
            'thick': 1000,
            'xmin': 0,
            'xmax': 99998
        },
        {
            'type': 'cauchy',
            'A': 1.5,
            'B': 0,
            'C': 0,
            'thick': 1000,
            'xmin': 0,
            'xmax': 99998
        },
        {
            'type': 'file',
            'path' : 'storage/newMaterials/Age_asp.json',
            'name': 'Age_asp.json',
            'xmin': 207,
            'xmax': 826,
            'thick': 1000
        }
    ],
    functions: ['delta', 'psi', 'rs', 'rp']
}

function calculateMinMax() {
    if (requestBody.materials.length === 0)
        return [0, 99998];
    let xmin = requestBody.materials[0].xmin;
    let xmax = requestBody.materials[0].xmax;
    for (const material of requestBody.materials) {
        if (material.xmin > xmin)
            xmin = material.xmin;
        if (material.xmax < xmax)
            xmax = material.xmax;
    }

    return [Math.ceil(xmin), Math.floor(xmax)];
}

function renderHtmlMaterial(material, index, isFirst, isLast) {
    let name = 'Material name';
    if (material.type === 'file')
        name = `File('${material.name}')`;
    if (material.type === 'cauchy')
        name = `Cauchy(A=${material.A}, B=${material.B}, C=${material.C})`;
    if (material.type === 'constant')
        name = `Constant(n=${material.n}, k=${material.k})`;

    const html = `
    <tr>
        <td class="buttons-row">
            <button class="btn-action" onclick="switchMaterialsPositions(${index}, ${index - 1})" ${isFirst ? 'disabled' : ''}>↑</button>
            <button class="btn-action" onclick="switchMaterialsPositions(${index}, ${index + 1})" ${isLast ? 'disabled' : ''}>↓</button>
            <button class="btn-action" onclick="removeMaterial(${index})">×</button>
        </td>
        <td>
            <input type="number" value="${material.thick}" oninput="changeMaterialThickness(${index}, this.value)" ${isFirst || isLast ? 'disabled' : ''} ${isFirst || isLast ? 'title="can\'t change thickness of the first or last layer"': ''}"/>
        </td>
        <td>${name}</td>
    </tr>
    `;
    return html;
}

function renderHtmlMaterials() {
    const materials = requestBody.materials;
    let html = `
    <tr>
        <th style="width: 50px;"></th>
        <th style="width: 150px;">Thickness (nm)</th>
        <th>Material</th>
    </tr>
    `;
    for (let index = 0; index < materials.length; index++) {
        const isFirst = index === 0;
        const isLast = index === (materials.length - 1);
        html += renderHtmlMaterial(materials[index], index, isFirst, isLast);
    }
    elTableSelected.innerHTML = html;
    if (materials.length < 2 )
        elErrorsSelected.textContent = "Please, add at least 2 layers.";
    else
        elErrorsSelected.textContent = "";
}

async function fetchImage() {
    const postData = JSON.parse(JSON.stringify(requestBody));
    try {
        const response = await fetch('/image', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(postData)
        });
        const data = await response.json();
        document.getElementById('graph-img').src = data['image_url'];
        elErrors.textContent = '';
    }
    catch (error) {
        console.error('fetch error:', error);
        elErrors.textContent = "Bad input data. Please, check your input fields."
    }
}

function recalculateMinMax() {
    const [xmin, xmax] = calculateMinMax();
    if (Number(elXfrom.value) < xmin)
        elXfrom.value = xmin;
    if (Number(elXto.value) > xmax)
        elXto.value = xmax;

    elXfrom.min = xmin;
    elXto.max = xmax;
    requestBody.ustart = xmin;
    requestBody.uend = xmax
}

function addMaterial(material) {
    requestBody.materials.push(material);
    recalculateMinMax();
    renderHtmlMaterials();
    fetchImage();
}

function removeMaterial(index) {
    requestBody.materials.splice(index, 1);
    recalculateMinMax();
    renderHtmlMaterials();
    fetchImage();
}

function switchMaterialsPositions(index1, index2) {
    if (index1 < 0 || index2 < 0)
        return;
    if (index1 >= requestBody.materials.length || index2 >= requestBody.materials.length)
        return;
    const material1 = requestBody.materials[index1];
    const material2 = requestBody.materials[index2];
    requestBody.materials[index1] = material2;
    requestBody.materials[index2] = material1;

    renderHtmlMaterials();
    fetchImage();
}

function changeMaterialThickness(index, thickness) {
    requestBody.materials[index].thick = Number(thickness);
    fetchImage();
}

function toggleFunction(functionName) {
    if (requestBody.functions.includes(functionName))
        requestBody.functions = requestBody.functions.filter(fn => fn !== functionName);
    else
        requestBody.functions.push(functionName);
    fetchImage();
}

elInputAngle.addEventListener('input', (evt) => {
    const angle = Number(evt.target.value);
    requestBody.uangle = angle
    fetchImage();
});

elXfrom.addEventListener('input', (evt) => {
    const xfrom = Number(evt.target.value);
    requestBody.ustart = xfrom
    fetchImage();

});

elXto.addEventListener('input', (evt) => {
    const xto = Number(evt.target.value);
    requestBody.uend = xto
    fetchImage();
});


elBtnNewCauchy.addEventListener('click', (evt) =>{
    const a = Number(document.getElementById('cauchy-a').value);
    const b = Number(document.getElementById('cauchy-b').value);
    const c = Number(document.getElementById('cauchy-c').value);

    if (isNaN(a) || isNaN(b) || isNaN(c)) {
        alert("Please, enter valid numbers for A, B and C");
        return;
    }
    addMaterial({
        'type': 'cauchy',
        'A': a,
        'B': b,
        'C': c,
        'thick': 1000,
        'xmin': 0,
        'xmax': 99998
    });
});

elBtnNewConstant.addEventListener('click',(evt) => {
    const n = Number(document.getElementById('constant-n').value);
    const k = Number(document.getElementById('constant-k').value);

    if (isNaN(n) || isNaN(k)) {
        alert("Please, enter valid numbers for n and k");
        return;
    }
    addMaterial({
        'type': 'constant',
        'n': n,
        'k': k,
        'thick': 1000,
        'xmin': 0,
        'xmax': 99998
    });
});


// create on page laod
const allFileMaterialItems = document.querySelectorAll('.material-item');
for (const fileMaterialItem of allFileMaterialItems) {
    fileMaterialItem.addEventListener('click', (evt) => {
        addMaterial({
            'type': 'file',
            'path': evt.target.getAttribute('data-path'),
            'name': evt.target.getAttribute('data-name'),
            'thick': 1000,
            'xmin': Number(evt.target.getAttribute('data-umin')),
            'xmax': Number(evt.target.getAttribute('data-umax'))
        });
    });
}

fetchImage();
renderHtmlMaterials();
