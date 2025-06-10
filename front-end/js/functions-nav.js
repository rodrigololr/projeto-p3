
//isso é pra pegar a nav do site e colocar lá
fetch('../html/nav.html')
        .then(response => response.text())
        .then(data => {
          document.getElementById('navbar-placeholder').innerHTML = data;
    
          // pegando o nome do arquivo atual
          const path = window.location.pathname.split("/").pop();
          
    
          // adicionando a classe 'active' no link correspondente
          if(path === "principal.html") {
            document.getElementById("buttons-nav").classList.add("active");
            
          } 
          else if (path === "metas.html") {
            document.getElementById("buttons-nav-2").classList.add("active");
            
          } 
          else if (path === "dicas.html") {
            document.getElementById("buttons-nav-3").classList.add("active");
          }

          else if (path === "investimento.html") {
            document.getElementById("buttons-nav-4").classList.add("active");
          }

        });





/* =-=-=-=-=-=-=-=- JS do switch =-=-=-=-=-=-=-=- */
    // controle do toggle
    const notificationToggle = document.getElementById('notificationToggle');
    const notificationToggleMobile = document.getElementById('notificationToggleMobile');

    // sincroniza os tongos
    function syncNotificationToggles() {
      notificationToggleMobile.checked = notificationToggle.checked;
    }

    notificationToggle.addEventListener('change', syncNotificationToggles);
    notificationToggleMobile.addEventListener('change', function() {
      notificationToggle.checked = this.checked;
    });

    // se tiver estado, ele verifica 
    if (localStorage.getItem('notificationsEnabled') !== null) {
      const isEnabled = localStorage.getItem('notificationsEnabled') === 'true';
      notificationToggle.checked = isEnabled;
      notificationToggleMobile.checked = isEnabled;
    }

    // alterado o estado, ele salva
    function saveNotificationPreference() {
      localStorage.setItem('notificationsEnabled', notificationToggle.checked);
      showAlert(`Notificações ${notificationToggle.checked ? 'ativadas' : 'desativadas'} com sucesso!`);
    }

    notificationToggle.addEventListener('change', saveNotificationPreference);
    notificationToggleMobile.addEventListener('change', saveNotificationPreference);
    //acabou graças a deus amém 