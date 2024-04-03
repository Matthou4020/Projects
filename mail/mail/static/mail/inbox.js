document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  document.querySelector('#compose-form').onsubmit = function() {
    const subject = document.querySelector('#compose-subject').value;
    const recipients = document.querySelector('#compose-recipients').value;
    const body = document.querySelector('#compose-body').value;
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
  });
  
  
function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#display-mail').style.display = 'none';
  document.querySelector('#archives').style.display = 'none';
  document.querySelector('#sent_view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
};


function display_mail(mail) {
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  emails_view = document.querySelector('#display-mail')
  emails_view.style.display = 'block'
  const subject = mail.subject;
  const sender = mail.sender;
  const timestamp = mail.timestamp;
  const body = mail.body;

  if (document.querySelector('#header') && document.querySelector('#paragraph')) {
  header.innerHTML = `Subject: ${subject}. ${sender}${timestamp}`;
  paragraph.innerHTML = `${body}`;
  }
  else {
    const header = document.createElement('h4');
    header.innerHTML = `Subject: ${subject}. ${sender}${timestamp}`;
    header.id = "header"
    const paragraph = document.createElement('p');
    paragraph.innerHTML = `${body}`;
    paragraph.id = "paragraph"
    emails_view.append(header, paragraph);
    const archive = document.createElement('button');
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

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#display-mail').style.display = 'none'
  document.querySelector('#archives').style.display = 'none'
  document.querySelector('#sent_view').style.display = 'none'

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
  //I STILL NEED TO CLEAR INSTANCES OF ARCHIVED MAILS WHEN I CLICK THE BUTTON
  // AT THE MOMENT, WITHIN THE SAME SESSION, ARCHIVED ITEMS STAY ON THE PAGE
  // BECAUSE NO REFRESH
  // ALSO CHECK THE CSS COHERENCE.
  // ALSO, USERS SHOULD BE ABLE TO ACCESS A VIEW OF THEIR SENT MAILS. DO I CARE THOUGH?
  if (mailbox === 'archive') {
    document.querySelector('#archives').style.display = 'block'
    fetch('/emails/archive')
    .then(response => response.json())
    .then(emails => {
      if (!document.querySelector('#restore')) {
    for(let i = 0; i < emails.length; i++) {
      const subject = emails[i].subject;
      const sender = emails[i].sender;
      const timestamp = emails[i].timestamp;
      const element = document.createElement('div');
      element.innerHTML = `${timestamp} Subject: ${subject}. From: ${sender}`
      
      const archived = document.querySelector('#archives')
      archives.append(element);
      const restore = document.createElement('button');
      restore.className = "btn btn-sm btn-outline-secondary";
      restore.id = "restore";
      restore.innerHTML = "Restore";
      archives.append(restore);
      restore.addEventListener('click', () => {
        fetch(`/emails/${emails[i].id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: false
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
        for (let i = 0; i < emails.length; i++) {
          const subject = emails[i].subject;
          const sender = emails[i].sender;
          const timestamp = emails[i].timestamp;
          const read = emails[i].read;
          const id = emails[i].id;
          const element = document.createElement('div');
          element.id = id
          element.innerHTML = `${timestamp} Subject: ${subject}. From: ${sender}`
          if (read) {
            element.style.backgroundColor = 'lightgray';
          }
          const emailsview = document.querySelector('#emails-view')
          emailsview.append(element);
          
          element.addEventListener('click', function() {
            fetch(`/emails/${element.id}`)
            .then(response => response.json())
            .then(email => {
              element.style.backgroundColor = 'white'
              display_mail(email)

              fetch(`/emails/${email.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    read: true
                })
              })
            }
           ) })
          }}
           )}
  if (mailbox === 'sent') {
    document.querySelector('#sent_view').style.display = 'block'
    
    if(!document.querySelector('#sent_email')) {
    fetch('/emails/sent')
    .then(response => response.json())
    .then(emails => {
      for (let i = 0; i < emails.length; i++) {
        const subject = emails[i].subject;
        const recipients = emails[i].recipients;
        const timestamp = emails[i].timestamp;
        const element = document.createElement('div');
        element.innerHTML = `${timestamp} Subject: ${subject}. To: ${recipients}`
        element.id = "sent_email"
        const sent_view = document.querySelector('#sent_view')
        sent_view.append(element);
    }
  })}
};
}

