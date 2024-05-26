// Remaining:

  // Handle subject overflow in the mail display view and everywhere else.

  // Keep refactoring

  // I need to find a way for the new mails to appear on top. When new mails are appended
  // they go at the end of the mail list if I don't refresh the app.

  // Add error-catching

  // Add responsiveness

  // For some reason, when restoring a mail after loading the sent view or after sending
  // a mail, the inbox does not display the newly restored mail without a refresh.

document.addEventListener('DOMContentLoaded', function() {
  window.onload = () => {
    document.querySelector('#body').classList.remove('d-none')
  }

  // Add event listeners for the menu buttons
  addMenuButtonListeners()

  // By default, load the inbox
  load_mailbox('inbox');

  function addMenuButtonListeners() {

    // Use toggle buttons to toggle between views
    const buttons = document.querySelectorAll('.menu-btn');

    buttons.forEach(button => {
      button.addEventListener('click', () => {
        // Remove 'active' class from all buttons except the clicked one
        buttons.forEach(otherButton => {
          if (otherButton !== button) {
            otherButton.classList.remove('active')
          }
        })
        
        // Perform the associated action
        if (button.id === 'inbox') {
          load_mailbox('inbox');
        } else if (button.id === 'compose') {
          compose_email();
        } else if (button.id === 'sent') {
          load_mailbox('sent');
        } else if (button.id === 'archived') {
          load_mailbox('archive');
        }
        
      })
    })
  }


  function toggleButton(mailbox) {
    const menuButtons = document.querySelectorAll('.menu-btn') 
    menuButtons.forEach(button => {
      if (button.id === mailbox ){
        if(!button.classList.contains('active')) {
          button.classList.toggle('active')
        }
      } else {
        button.classList.remove('active')
      }
    })
  }


  // Display full mail if click on a row of the inbox
  function display_mail(mail) {
    document.querySelector('#mailbox-title').innerHTML = '';
    displayCurrentView('mail-display');
        
    // Populate row cells
    document.getElementById('header').innerHTML = `${mail.subject}`;
    document.getElementById('sender').innerHTML = `${mail.sender}`;
    document.getElementById('date').innerHTML = `${mail.timestamp}`;
    document.getElementById('content').innerHTML = `${mail.body}`;

    // Update later if I want the recipient's information to be dynamic
    document.getElementById('recipient').innerHTML = `To: you`;
    
    // Reply and archive logic
    let reply = document.querySelector("#reply-btn");
    let archive = document.querySelector("#archive-btn");
    reply.classList.add("btn")
    archive.classList.add("btn")

    reply.addEventListener('click', () => {
      compose_email(mail)
    });

    archive.addEventListener('click', () => {
    fetch(`/emails/${mail.id}`, {
      method: 'PUT',
      body: JSON.stringify({
        archived: true
      })
    });
    load_mailbox('inbox')
    document.getElementById(`${mail.id}`).style.display = 'none';
    });
  }
  

  function displayCurrentView(elementID) {
    views = document.querySelectorAll('.view')
    views.forEach(view => {
      view.style.display= 'none'
    });
    newView = document.getElementById(elementID);
    newView.style.display = 'block';
  }


  function load_mailbox(mailbox) {
    
    // Switch menu buttons
    toggleButton(mailbox)

    // Display mailbox name
    document.querySelector('#mailbox-title').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
    
    // Inbox logic
    if (mailbox === 'inbox') {
      fetch('/emails/inbox')
      .then(response => response.json())
      .then(emails => {
        displayCurrentView('emails-view')
        const emailsView = document.getElementById('emails-view');
        const body = document.getElementById('emails-view-table');
            
        for (let i = 0; i < emails.length; i++) {
          let subject = emails[i].subject;
          let sender = emails[i].sender;
          let timestamp = emails[i].timestamp;
          let read = emails[i].read;
          let id = emails[i].id;
          let content = emails[i].body
          
          if (!document.getElementById(`${emails[i].id}`)) {
            const row = document.createElement('tr');
            const dateCell = document.createElement('td');
            const senderCell = document.createElement('td');
            const deleteBtn = document.createElement('td');
            const subjectCell = document.createElement('td');
        
            if (read !== true) {
              row.classList.add('table-unread');
              senderCell.innerHTML = `<strong>${sender}</strong>`
              subjectCell.innerHTML = `<strong>${subject}</strong> <span class='text-muted'>${content}</span>`
            } else {
              row.classList.remove('table-unread')
              senderCell.innerHTML = `${sender}`
              subjectCell.innerHTML = `${subject} <span class='text-muted'>${content}</span>`
            }

            dateCell.innerHTML = `${timestamp}`
            
            deleteBtn.innerHTML = `<i class="bi bi-trash"></i>`
            deleteBtn.classList.add('delete-btn')
            body.appendChild(row)
            row.append(senderCell, subjectCell, dateCell, deleteBtn)            
            row.id = id;
            row.classList.add('mail-row')

            row.addEventListener('click', () => {
              row.classList.remove('table-unread')
              emailsView.style.display = 'none'
              fetch(`/emails/${row.id}`)
              .then(response => response.json())
              .then(email => {
                display_mail(email)
                fetch(`/emails/${email.id}`, {
                  method: 'PUT',
                  body: JSON.stringify({
                      read: true
                  })
                })
              })
            })

            // Logic to delete mail
            deleteBtn.addEventListener('click', (event) => {
              event.stopPropagation();
              fetch(`/emails/${row.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                  archived: true
                })
              })
              .then(() => {
                // Delete animation
                row.style.animationPlayState = 'running';
                row.addEventListener('animationend', () => {
                  row.remove();
                })
              })
            })
          }
        }
      })
    }

    // Archive logic
    if (mailbox === 'archive') {
      toggleButton('archived')
      displayCurrentView('archives')

      fetch('/emails/archive')
      .then(response => response.json())
      .then(emails => {
        if (!document.querySelector('.archives-row')) {
          
          // Build table view
          for(let i = 0; i < emails.length; i++) {

            // Select table
            const tableBody = document.getElementById('archives-view-table');
            
            // Populate table
            const row = document.createElement('tr');

            row.id = emails[i].id;    
            row.classList.add('archives-row')
            tableBody.append(row);

            // Populate table rows
            const dateCell = document.createElement('td');
            const subjectCell = document.createElement('td');
            const senderCell = document.createElement('td');

            dateCell.innerHTML = `${emails[i].timestamp}`
            subjectCell.innerHTML = `${emails[i].subject} <span class='text-muted'>${emails[i].body}</span>`;
            senderCell.innerHTML = `${emails[i].sender}`;

            // Add a restore button
            const restoreBtn = document.createElement('td');

            restoreBtn.classList.add('restore-btn');
            restoreBtn.innerHTML = "Restore";

            // Append all elements
            row.append(senderCell, subjectCell,dateCell, restoreBtn) 

            // Restore button logic
            restoreBtn.addEventListener('click', () => {
              console.log("unarchived")
              fetch(`/emails/${emails[i].id}`, {
                method: 'PUT',
                body: JSON.stringify({
                  archived: false
                })
              })
              .then(() => {
                row.style.animationPlayState = 'running';
                row.addEventListener('animationend', () => {
                  row.remove()
                  load_mailbox('inbox');
                })
              })
            });
          }}
        })
      }


    // Sent view logic
    if (mailbox === 'sent') {
      displayCurrentView('sent-view')
      const body = document.getElementById('sent-view-table')
      
      if(!document.querySelector('.sent-mail')) {
        fetch('/emails/sent')
        .then(response => response.json())
        .then(emails => {
          for (let i = 0; i < emails.length; i++) {
            let subject = emails[i].subject;
            let sender = emails[i].sender;
            let timestamp = emails[i].timestamp;
            let id = emails[i].id;
            let content = emails[i].body

            const row = document.createElement('tr');
            const dateCell = document.createElement('td');
            const subjectCell = document.createElement('td')
            const senderCell = document.createElement('td')

            row.classList.remove('table-unread')
            senderCell.innerHTML = `${sender}`
            subjectCell.innerHTML = `${subject} <span class='text-muted'>${content}</span>`
            
            dateCell.innerHTML = `${timestamp}`

            body.appendChild(row)
            row.append(senderCell, subjectCell,dateCell)            
            row.id = id;
            row.classList.add('sent-mail')
          }
        })
      }
    };
  } // End of load_mailbox function


  // Display the compose view
  function compose_email(mail) {
    toggleButton('compose')

    document.querySelector('#mailbox-title').innerHTML = `<h3>New message</h3>`;

    // Show compose view and hide other views
    displayCurrentView('compose-view');

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
    
    // If user comes after clicking a reply button
    if (mail) {
      document.querySelector('#compose-recipients').value = mail.sender;
      document.querySelector('#compose-subject').value = `Re: ${mail.subject}`;
      document.querySelector('#compose-body').value = `On ${mail.timestamp},${mail.sender} wrote:\n ${mail.body}`;
    }

    // Submit logic
    document.querySelector('#compose-form').onsubmit = function() {
      let subject = document.querySelector('#compose-subject').value;
      let recipients = document.querySelector('#compose-recipients').value;
      let body = document.querySelector('#compose-body').value;
      fetch('/emails', {
        method:'POST',
        body: JSON.stringify({
          recipients: recipients,
          subject: subject,
          body: body
        })
      })
      .then(response => response.json())
      .then(result => {
        console.log(result);
      })
      .catch(error => {
        console.log('Error:', error);
      });
      load_mailbox('inbox');
      return false
    }
  };

}); // DOMeventlistener closed
