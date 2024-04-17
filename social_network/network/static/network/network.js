document.addEventListener('DOMContentLoaded', function() {
    
    if (document.querySelector('#pagination')) {
        const pages = document.querySelectorAll('li')

        pages.forEach(function(page) {
            page.addEventListener('click', () => {

                //fetch the posts and display them
                fetch(`/`, {
                    method:'POST',
                    body: JSON.stringify({
                        'page_number':page.id,
                        'ajax':True
                    })
                }
            )
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                })
            })
        });
    }
    // I will need to check that the text area respects the constraints of the model.
    // Add my variable types
    if (document.querySelector('.edit-button')) {
        const edit_buttons = document.querySelectorAll('.edit-button');
        edit_buttons.forEach(function(button) {
            button.addEventListener('click', () => {
                button.style.display = 'none'

                paragraph = button.nextElementSibling;
                const previous_content = paragraph.innerHTML;
                paragraph.innerHTML = '';
                textarea = document.createElement('textarea');
                textarea.id = "edited_post";
                textarea.rows = 1;
                textarea.cols = 50;
                textarea.value = previous_content;
                paragraph.appendChild(textarea);
                textarea.focus();

                validate = document.createElement('button')
                validate.className = 'btn btn-outline-primary btn-sm'
                validate.style.display='block'
                validate.innerHTML = 'confirm'
                paragraph.appendChild(validate)

                //I don't precisely know what the following does. It comes from CS50's AI and it solves
                // a problem I've had with a csrf error while trying to put data in 
                // in the following request
                const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken')).split('=')[1];

                validate.addEventListener('click', () => {
                    validate.style.display = 'none'
                    button.style.display = 'inline'
                    const edited_content = textarea.value
                    const currentUserId = button.dataset.userId;
                    fetch('/posts', {
                        method:'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken
                        },
                        body: JSON.stringify({
                            user_id:currentUserId,
                            previous_content: previous_content,
                            edited_content: edited_content,
                        })
                    })

                    paragraph.innerHTML =  edited_content
                })

            })
        })
        
    }

    if (document.querySelector('#toggle_button')) {
        const toggle_button = document.querySelector('#toggle_button');
        const user_profile = document.querySelector('#user_profile').innerHTML;

        fetch(`/users/${user_profile}`)
        .then(response => response.json())
        .then(data => {
            if (data.follows.includes(user_profile)) {
                toggle_button.innerHTML = 'Unfollow';
                toggle_button.style.backgroundColor = 'darkblue';
            } else {
                toggle_button.innerHTML = 'Follow';
            }
        })

        toggle_button.addEventListener('click', function() {
            if (toggle_button.innerHTML === 'Follow') {
                toggle_button.innerHTML ='Unfollow';
                toggle_button.style.backgroundColor = 'darkblue';
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
                toggle_button.style.backgroundColor = 'blue'
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

    if (document.querySelector('.like_button')) {
        const likeButtons = document.querySelectorAll('.like_button')
        likeButtons.forEach(function(likeButton) {
            const userId = likeButton.dataset.userId;
            const postId = likeButton.dataset.postId;
            const span = likeButton.nextElementSibling
            fetch('/posts', {
                method:'POST',
                body: JSON.stringify({
                    user_id:userId,
                    post_id:postId
                })
            })
            .then (response => response.json())
            .then (data => {
                span.innerHTML = data.likeCount
                const hasLiked = data.hasLiked
                if (hasLiked === true) {
                    likeButton.innerHTML = '<i class="bi bi-heart-fill"></i>'
                   
                } else {
                    likeButton.innerHTML = '<i class="bi bi-heart"></i>'
                }
            })
            
            likeButton.addEventListener('click', () => {
                if (likeButton.innerHTML === '<i class="bi bi-heart"></i>') {
                    likeButton.innerHTML = '<i class="bi bi-heart-fill"></i>';
                  
                    fetch('/posts', {
                        method:'POST',
                        body: JSON.stringify({
                            action:"like",
                            user_id:userId,
                            post_id:postId
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        span.innerHTML = data.actualizedCount                        
                    });
                } else {
                    likeButton.innerHTML = '<i class="bi bi-heart"></i>';
                    
                    fetch('/posts', {
                        method:'POST',
                        body:  JSON.stringify({
                            action:"unlike",
                            user_id:userId,
                            post_id:postId
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        span.innerHTML = data.actualizedCount                        
                    });
                }
            })
        })
    }
});