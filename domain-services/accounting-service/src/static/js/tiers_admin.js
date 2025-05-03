// Script pour la gestion automatique des types et comptes en fonction du code
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé, initialisation du script...");
    
    // Récupérer les éléments par ID
    const codeField = document.getElementById('id_code');
    const nameField = document.getElementById('id_name');
    const typeField = document.getElementById('id_type');
    const accountField = document.getElementById('id_account');
    
    // Vérifier que tous les éléments ont été trouvés
    console.log("Champs trouvés:", {
        code: !!codeField,
        name: !!nameField,
        type: !!typeField,
        account: !!accountField
    });
    
    if(codeField && typeField && accountField) {
        // Rendre les champs type et account en lecture seule
        typeField.setAttribute('readonly', 'readonly');
        typeField.setAttribute('disabled', 'disabled');
        accountField.setAttribute('readonly', 'readonly');
        accountField.setAttribute('disabled', 'disabled');
        
        // Ajouter une indication visuelle
        typeField.style.backgroundColor = '#f0f0f0';
        accountField.style.backgroundColor = '#f0f0f0';
        
        // Créer des champs cachés pour conserver les valeurs
        const hiddenTypeField = document.createElement('input');
        hiddenTypeField.type = 'hidden';
        hiddenTypeField.name = 'type';
        hiddenTypeField.id = 'hidden_type';
        typeField.parentNode.appendChild(hiddenTypeField);
        
        const hiddenAccountField = document.createElement('input');
        hiddenAccountField.type = 'hidden';
        hiddenAccountField.name = 'account';
        hiddenAccountField.id = 'hidden_account';
        accountField.parentNode.appendChild(hiddenAccountField);
        
        // Mettre à jour le type et le compte lorsque le code change
        codeField.addEventListener('input', function() {
            const code = this.value.trim().toUpperCase();
            console.log("Code modifié:", code);
            
            if(code.length >= 3) {
                const prefix = code.substring(0, 3);
                console.log("Préfixe détecté:", prefix);
                updateTypeAndAccount(prefix);
            }
        });
        
        // Vérifier le code initial au chargement
        if(codeField.value.trim().length >= 3) {
            const prefix = codeField.value.trim().substring(0, 3);
            updateTypeAndAccount(prefix);
        }
    } else {
        console.error("Un ou plusieurs champs n'ont pas été trouvés!");
    }
    
    function updateTypeAndAccount(prefix) {
        console.log("Mise à jour du type pour le préfixe:", prefix);
        
        let typeValue = '';
        let accountId = '';
        
        // Déterminer le type en fonction du préfixe
        if(prefix === '401') {
            typeValue = 'SUPPLIER';
            // Trouver l'ID du compte 401 dans les options disponibles
            accountId = findAccountIdByPrefix('401');
        } else if(prefix === '411') {
            typeValue = 'CUSTOMER';
            accountId = findAccountIdByPrefix('411');
        } else if(prefix === '422') {
            typeValue = 'EMPLOYEE';
            accountId = findAccountIdByPrefix('422');
        }
        
        if(typeValue) {
            // Mettre à jour l'affichage visuel
            for(let i = 0; i < typeField.options.length; i++) {
                if(typeField.options[i].value === typeValue) {
                    typeField.options[i].selected = true;
                    break;
                }
            }
            
            // Mettre à jour le champ caché
            document.getElementById('hidden_type').value = typeValue;
            console.log("Type défini sur:", typeValue);
        }
        
        if(accountId) {
            // Mettre à jour l'affichage visuel
            for(let i = 0; i < accountField.options.length; i++) {
                if(accountField.options[i].value === accountId) {
                    accountField.options[i].selected = true;
                    break;
                }
            }
            
            // Mettre à jour le champ caché
            document.getElementById('hidden_account').value = accountId;
            console.log("Compte défini sur ID:", accountId);
        }
    }
    
    function findAccountIdByPrefix(prefix) {
        // Parcourir toutes les options pour trouver un compte commençant par le préfixe
        for(let i = 0; i < accountField.options.length; i++) {
            const option = accountField.options[i];
            const text = option.textContent || option.innerText;
            
            // Vérifier si le texte contient le préfixe (mais une seule fois)
            if(text.includes(prefix) && !text.includes(prefix + " " + prefix)) {
                // Améliorer l'affichage de l'option si elle contient un doublon
                if(text.includes(" - " + prefix)) {
                    // Nettoyer le texte pour éviter les répétitions
                    const cleanText = text.split(" - ")[0];
                    option.textContent = cleanText;
                }
                return option.value;
            }
        }
        return '';
    }
});