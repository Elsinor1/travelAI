document.addEventListener('DOMContentLoaded', function() {
    const like_buttons = document.querySelectorAll('.like-button');
    if (like_buttons) {like_buttons.forEach((button) => button.onclick = (event) => {like(event.target.id)})};
    const edit_buttons = document.querySelectorAll('.edit-post');
    if (edit_buttons) {edit_buttons.forEach((button) => button.onclick = (event) => {edit(event.target.id)})};
})


function like(like_button_id) {
    console.log(like_button_id.split('_')[2]);
    const post_id = parseInt(like_button_id.split('_')[2]);
    fetch(`/like/${post_id}`, {
        method: 'PUT'
    })
    .then(response => response.json())
    .then(result => {
        const like_btn = document.getElementById(`like_button_${post_id}`);
        const likes = document.getElementById(`likes_${post_id}`);

        if (result.is_liked) {
            like_btn.innerHTML = 'Unlike <i class="fa fa-thumbs-down"></i>';
        }
        else {
            like_btn.innerHTML = 'Like <i class="fa fa-thumbs-up"></i>';
        }
        like_btn.blur();
        likes.innerHTML = result.likes_count
    })
}


function edit(edit_button_id) {

    const post_id = parseInt(edit_button_id.split('_')[2]);
    const text_p = document.getElementById(`post_text_${post_id}`);
    let text = text_p.innerHTML;

    // Replace post text paragraph with text area
    text_p.style.display = 'None';
    const new_text_area = document.createElement('textArea');
    new_text_area.innerHTML = text;
    new_text_area.id = `edit_area_${post_id}`
    text_p.closest('div').append(new_text_area);

    // Hide edit button
    const edit_btn = document.getElementById(edit_button_id);
    edit_btn.style.display = 'None';
    edit_btn.blur();

    // Create save edit button
    const save_btn = document.createElement('button')
    save_btn.onclick = () => save_edit(post_id);
    save_btn.innerHTML = "Save Edit";
    save_btn.id = `save_btn_${post_id}`;
    btn_classes = edit_btn.classList;
    btn_classes.forEach((btn_class) => save_btn.classList.add(btn_class));
    edit_btn.closest('div').append(save_btn);
}


function save_edit(post_id) {
    const post_text_area = document.getElementById(`edit_area_${post_id}`);
    const post_text = post_text_area.value;

    fetch(`/save/${post_id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json' // Set the Content-Type header to indicate JSON data
        },
        body: JSON.stringify({ post_text: post_text }) // Convert your data to JSON format
    })
    .then(response => {
        if (response.ok) {

            // Switch buttons
            const edit_btn = document.getElementById(`edit_button_${post_id}`);
            const save_btn = document.getElementById(`save_btn_${post_id}`);
            save_btn.remove();
            edit_btn.style.display = "inline-block";

            // Switch textarea with p
            const text_p = document.getElementById(`post_text_${post_id}`);
            const text_area = document.getElementById(`edit_area_${post_id}`);
            text_p.innerHTML = text_area.value;
            text_area.remove();
            text_p.style.display = 'block';
        }
        else {
            console.error('Error! Status code:', response.status);
            // Handle error cases based on the status code
        }
    })
    .catch(error => {
        console.error('Error occurred:', error);
        // Handle any network-related or other errors
    });
}

