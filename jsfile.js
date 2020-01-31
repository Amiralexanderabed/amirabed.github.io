        /*
        window.setInterval(function(){ // Set interval for checking
            
        }, 600000); // Repeat every 600000 milliseconds (10 minute)
        */
       
        const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
        
        /*function switchTheme(e) {
              if (e.target.checked) {
                 document.documentElement.setAttribute('data-theme', 'dark');
              }
              else {
                  document.documentElement.setAttribute('data-theme', 'light');
              }    
        }*/
  
        toggleSwitch.addEventListener('change', switchTheme, false);
  
        function switchTheme(e) {
            
            if (e.target.checked) {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark'); //add this
            }
            else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light'); //add this
            }    
        }
  
        const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : null;
        
            var date = new Date(); // Create a Date object to find out what time it is
            /*if(date.getHours() >= 17){ // Check the time
                //toggleSwitch.checked = true;
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark'); //add this
            }*/

            if (currentTheme) {
                document.documentElement.setAttribute('data-theme', currentTheme);
  
              if (currentTheme === 'dark') {
                  toggleSwitch.checked = true;
              }
            }