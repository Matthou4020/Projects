document.addEventListener('DOMContentLoaded', function() {
  
    const toggle_button = document.querySelector('#toggle_button');
    const user_profile = document.querySelector('#user_profile').innerHTML;

    fetch(`/users/${user_profile}`)
    .then(response => response.json())
    .then(data => {
        console.log(data.follows)
        if (data.follows.includes(user_profile)) {
            toggle_button.innerHTML = 'Unfollow';
        }
    })
    toggle_button.innerHTML = 'Follow'
    
    toggle_button.addEventListener('click', function() {
        if (toggle_button.innerHTML === 'Follow') {
            toggle_button.innerHTML ='Unfollow';
            // add user to follows
          
        } else {
            toggle_button.innerHTML = 'Follow';
            // remove user from follows
            
        }
    });
});

// // Fetch post
// fetch('/emails', {
//     method:'POST',
//     body: JSON.stringify({
//       recipients: recipients,
//       subject: subject,
//       body: body
//     })
//   })
//   .then(response => response.json())
//     .then(result => {
//       console.log(result);
//         })
//     .catch(error => {
//       console.log('Error:', error);
//       });
//       load_mailbox('sent');
//       return false


//       //fetch get
// fetch('/emails/archive')
// .then(response => response.json())
// .then(emails => {

// //fetch put
// fetch(`/emails/${emails[i].id}`, {
// method: 'PUT',
// body: JSON.stringify({
// archived: false

// });

// });