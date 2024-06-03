document.addEventListener('DOMContentLoaded', function() {
    // Interaction mapping
    const interactionMapping = {
      'Timing': ['fall', 'spring'],
      'Inhibitor': ['V6', 'centuro', 'nitrapyrin'],
      'N_rate': ['high', 'low', 'medium'],
      'Landscape': ['flat', 'tilt'],
      'Biological': ['provenN', 'utrishaN', 'NA'],
      'Cover_Crop': ['withcrop', 'withoutcrop', 'corncrop'],
      'Crop_Rotation': ['peanut', 'cotton'],
      'Fall_N_Rate': ['10', '20', '30'],
      'Previous_N_Rate': ['11', '12', '13'],
      'Grazing': ['yes', 'no', 'na'],
      'Spring_N_Rate': ['4', '6', '5'],
      'NA': ['NA'],
      'Select': ['Select']
    };
  
    const unitOptions = ['u1', 'u2', 'u3','na'];
  
    // Function to update interaction fields dynamically
    function updateInteractionFields(countId, fieldsContainerId, fieldPrefix, interactionType, fieldType) {
      const countValue = parseInt(document.getElementById(countId).value);
      const fieldsContainer = document.getElementById(fieldsContainerId);
      fieldsContainer.innerHTML = ''; // Clear existing fields
  
      for (let i = 1; i <= countValue; i++) {
        const label = document.createElement('label');
        label.textContent = `${fieldPrefix.replace('_', ' ')} ${i}: `;
        fieldsContainer.appendChild(label);
  
        if (fieldType === 'continuous') {
          const input = document.createElement('input');
          input.type = 'text';
          input.name = `${fieldPrefix}_${i}`;
          input.id = `${fieldPrefix}_${i}`;
          fieldsContainer.appendChild(input);
  
          const unitSelect = document.createElement('select');
          unitSelect.name = `${fieldPrefix}_${i}_unit`;
          unitSelect.id = `${fieldPrefix}_${i}_unit`;
          unitOptions.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            unitSelect.appendChild(optionElement);
          });
          fieldsContainer.appendChild(unitSelect);
        } else if (fieldType === 'class') {
          const select = document.createElement('select');
          const fieldName = `${fieldPrefix}_${i}`;
          select.name = fieldName;
          select.id = fieldName;
          const options = interactionMapping[interactionType] || [];
          options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
          });
          fieldsContainer.appendChild(select);
        }
        fieldsContainer.appendChild(document.createElement('br'));
      }
    }
  
    // Show the add experiment form when the button is clicked
    document.querySelector('#add-experiment-button').addEventListener('click', function() {
      document.querySelector('#experiment-actions').style.display = 'block';
    });
  
    // Handle dropdown selection
    document.querySelector('#experiment-action-select').addEventListener('change', function() {
      const action = this.value;
      if (action === 'add') {
        document.querySelector('#add-experiment-form').style.display = 'block';
      } else {
        document.querySelector('#add-experiment-form').style.display = 'none';
      }
    });
  
    // Handle form submission
    document.querySelector('#experiment-form').addEventListener('submit', function(event) {
      event.preventDefault(); // Prevent the default form submission
  
      const formData = new FormData(this);
      // Sends a POST request to the server-side URL
      fetch('{% url "add_experiment" %}', {
        method: 'POST',
        headers: {
          'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          const experimentID = formData.get('Experiment_ID');
          // Redirect to the show_treatments page
          window.location.href = `{% url 'show_treatments' experiment_id='EXPERIMENT_ID_PLACEHOLDER' %}`.replace('EXPERIMENT_ID_PLACEHOLDER', experimentID);
        } else {
          alert('Failed to add experiment: ' + data.error);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to add experiment. Please try again.');
      });
    });
  
    // Event listeners for interaction count fields and type selection
    document.getElementById('Interaction_1_count')?.addEventListener('change', function() {
      const interactionType = "{{ project.Interaction_1 }}";
      const fieldType = document.querySelector('input[name="interaction_1_type"]:checked')?.value;
      if (fieldType) {
        updateInteractionFields('Interaction_1_count', 'interaction_1-fields', 'Interaction_1_count', interactionType, fieldType);
      }
    });
  
    document.querySelectorAll('input[name="interaction_1_type"]').forEach(element => {
      element.addEventListener('change', function() {
        const interactionType = "{{ project.Interaction_1 }}";
        const fieldType = this.value;
        const countValue = parseInt(document.getElementById('Interaction_1_count').value);
        if (countValue) {
          updateInteractionFields('Interaction_1_count', 'interaction_1-fields', 'Interaction_1_count', interactionType, fieldType);
        }
      });
    });
  
    // Repeat the above for Interaction 2 and Interaction 3 if needed
  
    // Repeat the above for Interaction 2 and Interaction 3 if needed
  
    document.querySelectorAll('input[name="interaction_2_type"]').forEach(element => {
      element.addEventListener('change', function() {
        const interactionType = "{{ project.Interaction_2 }}";
        const fieldType = this.value;
        const countValue = parseInt(document.getElementById('Interaction_2_count').value);
        if (countValue) {
          updateInteractionFields('Interaction_2_count', 'interaction_2-fields', 'Interaction_2_count', interactionType, fieldType);
        }
      });
    });
  
    document.querySelectorAll('input[name="interaction_3_type"]').forEach(element => {
      element.addEventListener('change', function() {
        const interactionType = "{{ project.Interaction_3 }}";
        const fieldType = this.value;
        const countValue = parseInt(document.getElementById('Interaction_3_count').value);
        if (countValue) {
          updateInteractionFields('Interaction_3_count', 'interaction_3-fields', 'Interaction_3_count', interactionType, fieldType);
        }
      });
    });
  
  });