// Dynamically filter engineers in dropdown based on selected type

document.addEventListener('DOMContentLoaded', function() {
    const engineerTypeSelect = document.getElementById('id_engineer_type');
    const engineerSelect = document.getElementById('id_engineer_id');

    // Parse engineersByType from JSON script tag
    let engineersByType = {};
    const dataTag = document.getElementById('engineersByTypeData');
    if (dataTag) {
        try {
            engineersByType = JSON.parse(dataTag.textContent);
        } catch (e) {
            engineersByType = {};
        }
    }

    function updateEngineerDropdown(selectedType) {
        engineerSelect.innerHTML = '';
        const engineers = engineersByType[selectedType] || [];
        if (engineers.length === 0) {
            const opt = document.createElement('option');
            opt.textContent = 'No engineers available';
            opt.disabled = true;
            engineerSelect.appendChild(opt);
            return;
        }
        engineers.forEach(function(engineer) {
            const opt = document.createElement('option');
            opt.value = engineer.eng_id;
            opt.textContent = engineer.name;
            engineerSelect.appendChild(opt);
        });
    }

    if (engineerTypeSelect) {
        engineerTypeSelect.addEventListener('change', function() {
            updateEngineerDropdown(this.value);
        });
        updateEngineerDropdown(engineerTypeSelect.value);
    }
});
