document.addEventListener('DOMContentLoaded', function() {
  
    if (document.querySelector('#toggle_button')) {
        const toggle_button = document.querySelector('#toggle_button');
        const user_profile = document.querySelector('#user_profile').innerHTML;

        fetch(`/users/${user_profile}`)
        .then(response => response.json())
        .then(data => {
            if (data.follows.includes(user_profile)) {
                toggle_button.innerHTML = 'Unfollow';
            } else {
                toggle_button.innerHTML = 'Follow';
            }
        })
        
        
        toggle_button.addEventListener('click', function() {
            if (toggle_button.innerHTML === 'Follow') {
                toggle_button.innerHTML ='Unfollow';
                fetch(`/users/${user_profile}`, {
                    method:'POST',
                    body: JSON.stringify({
                        action:"follow",
                        follows: user_profile
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                });
            } else {
                toggle_button.innerHTML = 'Follow';
                fetch(`/users/${user_profile}`, {
                    method:'POST',
                    body: JSON.stringify({
                        action:"unfollow",
                        follows: user_profile
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                });
            }
        });
    };
});