console.log("Script classe_form.js chargé");

// Ce code irait dans static/js/tiers_admin.js
document.addEventListener('DOMContentLoaded', function() {
    const codeField = document.getElementById('id_code');
    const nameField = document.getElementById('id_name');
    const typeField = document.getElementById('id_type');
    const accountField = document.getElementById('id_account');

    if(codeField && nameField && typeField && accountField) {
        // Mettre à jour le type et le compte lorsque le code change
        codeField.addEventListener('input', function() {
            const code = this.value.trim().toUpperCase();
            if(code.length >= 3) {
                const prefix = code.substring(0, 3);
                updateTypeAndAccount(prefix);
            }
        });

        // Générer le code automatiquement quand le nom change
        nameField.addEventListener('blur', function() {
            if(!codeField.value && this.value) {
                const selectedType = typeField.value;
                generateCodeFromTypeAndName(selectedType, this.value);
            }
        });

        // Mettre à jour le code lorsque le type change
        typeField.addEventListener('change', function() {
            if(nameField.value) {
                generateCodeFromTypeAndName(this.value, nameField.value);
            }
        });
    }

    function updateTypeAndAccount(prefix) {
        // Logique pour mettre à jour le type et le compte en fonction du préfixe
        if(prefix === '401') {
            setSelectValue(typeField, 'SUPPLIER');
        } else if(prefix === '411') {
            setSelectValue(typeField, 'CUSTOMER');
        } else if(prefix === '422') {
            setSelectValue(typeField, 'EMPLOYEE');
        }
    }

    function generateCodeFromTypeAndName(type, name) {
        // Extraire les 3 premières lettres du nom (sans caractères spéciaux)
        const namePart = name.replace(/[^A-Za-z]/g, '').substring(0, 3).toUpperCase();
        let prefix = '';
        
        // Déterminer le préfixe en fonction du type
        if(type === 'SUPPLIER') {
            prefix = '401';
        } else if(type === 'CUSTOMER') {
            prefix = '411';
        } else if(type === 'EMPLOYEE') {
            prefix = '422';
        }
        
        if(prefix && namePart) {
            codeField.value = prefix + namePart;
        }
    }

    function setSelectValue(selectElement, value) {
        for(let i = 0; i < selectElement.options.length; i++) {
            if(selectElement.options[i].value === value) {
                selectElement.selectedIndex = i;
                break;
            }
        }
    }
});