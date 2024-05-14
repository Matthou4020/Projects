document.addEventListener('DOMContentLoaded', function() {
  window.onload = () => {
    document.querySelector('#body').classList.remove('d-none')
  }

  // By default, load the inbox
  load_mailbox('inbox');
  document.querySelector('#inbox').classList.toggle('active');


  // Use toggle buttons to toggle between views
  const buttons = document.querySelectorAll('.menu-btn')
  
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      buttons.forEach(otherButton => {
        if (otherButton !== button) {
          otherButton.classList.remove('active')
        }
      })
    if (button.id === 'inbox') {
      button.classList.toggle('active')
      load_mailbox('inbox');
    } else if (button.id === 'compose') {
      button.classList.toggle('active')
      compose_email();
    } else if (button.id === 'sent') {
      button.classList.toggle('active')
      load_mailbox('sent');
    } else if (button.id === 'archived') {
      button.classList.toggle('active')
      load_mailbox('archive');
    }
  })
})


  function compose_email(mail) {


    document.querySelector('#mailbox-title').innerHTML = '';

    // Show compose view and hide other views
    displayView('compose-view');

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
      load_mailbox('sent');
      return false
    }
  };


  // Displaying mail when clicking on it in the inbox
  function display_mail(mail) {
    displayView('display-mail')
    emails_view = document.querySelector('#display-mail')

    let subject = mail.subject;
    let sender = mail.sender;
    let timestamp = mail.timestamp;
    let body = mail.body;
    let header = document.querySelector('#header');
    let paragraph = document.querySelector('#paragraph');

    if (!header || !paragraph) {

      // Add header
      let header = document.createElement('h4');
      header.innerHTML = `Subject: ${subject}. ${sender}${timestamp}`;
      header.id = "header"
      emails_view.append(header)

      // Add body
      const paragraph = document.createElement('p');
      paragraph.innerHTML = `${body}`;
      paragraph.id = "paragraph"
      emails_view.append(paragraph)
    }
  
  // Update paragraph and header content
    else {
      header.innerHTML = `Subject: ${subject}. ${sender}${timestamp}`;
      paragraph.innerHTML = `${body}`
    }

    let reply = document.querySelector("#reply");
    let archive = document.querySelector("#archive");

    if (!reply) {
    // Add reply button
    reply = document.createElement('button');
    reply.className = "btn btn-sm btn-outline-secondary";
    reply.id = "reply";
    reply.innerHTML = "Reply";
    emails_view.append(reply);
    reply.addEventListener('click', () => {
      compose_email(mail)
      });
    }
    if (!archive) {
      // Add archive button
      archive = document.createElement('button');
      archive.className = "btn btn-sm btn-outline-secondary";
      archive.id = "archive";
      archive.innerHTML = "Archive";
      emails_view.append(archive);
      archive.addEventListener('click', () => {
      fetch(`/emails/${mail.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: true
        })
      });
      load_mailbox('inbox')
      });
    } 
  }
  

  function displayView(elementID) {
    views = document.querySelectorAll('.view')
    views.forEach(view => {
      view.style.display= 'none'
    });
    newView = document.getElementById(elementID);
    newView.style.display = 'block';
  }


  function load_mailbox(mailbox) {

    // Show the mailbox name
    document.querySelector('#mailbox-title').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
    
    if (mailbox === 'archive') {
      displayView('archives')

      fetch('/emails/archive')
      .then(response => response.json())
      .then(emails => {
        if (!document.querySelector('#restore')) {
          for(let i = 0; i < emails.length; i++) {
            let subject = emails[i].subject;
            let sender = emails[i].sender;
            let timestamp = emails[i].timestamp;
            let id = emails[i].id;
            let content = emails[i].body

            const tableBody = document.getElementById('archives-view-table');
            const row = document.createElement('tr');
            const dateCell = document.createElement('td');
            const subjectCell = document.createElement('td')
            const senderCell = document.createElement('td')
            const restoreBtn = document.createElement('td')

            dateCell.innerHTML = `${timestamp}`
            subjectCell.innerHTML = `${subject} <span class='text-muted'>${content}</span>`
            senderCell.innerHTML = `${sender}`

            tableBody.append(row);
            tableBody.append(restoreBtn);
            row.append(senderCell, subjectCell,dateCell, restoreBtn) 

            row.id = id;    
            row.classList.add('archives-row')


            restoreBtn.classList.add('btn', 'restore-btn');
            restoreBtn.innerHTML = "Restore";
            restoreBtn.addEventListener('click', () => {
              fetch(`/emails/${emails[i].id}`, {
                method: 'PUT',
                body: JSON.stringify({
                  tableBody: false
                })
              });
              load_mailbox('inbox')
            });
          }}
        })
      }

    if (mailbox === 'inbox') {
      fetch('/emails/inbox')
      .then(response => response.json())
      .then(emails => {
        displayView('emails-view')
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
            const subjectCell = document.createElement('td');
            const senderCell = document.createElement('td');
            const deleteBtn = document.createElement('td');

            if (read !== true) {
              row.classList.add('table-unread');
              senderCell.innerHTML = `<strong>${sender}</strong>`
              subjectCell.innerHTML = `<strong>${subject}</strong>`
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
              emailsView.style.display = 'none'
              row.classList.remove('table-unread')
              fetch(`/emails/${row.id}`)
              .then(response => response.json())
              .then(email => {
                display_mail(email)
                fetch(`/emails/${email.id}`, {
                  method: 'PUT',
                  body: JSON.stringify({
                      read: true
                  })
                }
              )
            })
          })
          deleteBtn.addEventListener('click', () => {
            // Add logic to delete a button
          })
        }
      }
    
      }
    )}

      if (mailbox === 'sent') {
        displayView('sent-view')
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
  }
});
