document.addEventListener('DOMContentLoaded', () => {

    const follow_btn = document.querySelector('#follow-btn');
    if (follow_btn) {
        follow_btn_setup(follow_btn.dataset.user_id);
        follow_btn.onclick = () => follow(follow_btn.dataset.user_id);
    }
});


function follow_btn_setup(user_id) {
    let is_followed = false;
    const follow_btn = document.querySelector('#follow-btn');
    fetch(`/follow/${user_id}`)
        .then(response => response.json())
        .then(result => {
            is_followed = result.is_followed;
            if (is_followed) {
                follow_btn.innerHTML = 'Unfollow';
            }
            else {
                follow_btn.innerHTML = 'Follow';
            }
        })
        .catch(error => {
            console.error('Error fetching follow status:', error);
        });

}


function follow(user_id) {
    const follow_btn = document.querySelector('#follow-btn');
    fetch(`/follow/${user_id}`, {
        method: 'PUT'
    })
    .then(response => response.json())
    .then(result => {
        // Check if user is followed
        const is_followed = result.is_followed

        // Change button text
        if (is_followed) {
            follow_btn.innerHTML = 'Unfollow'
        }
        else {
            follow_btn.innerHTML = 'Follow'
        }

        // Update follower info values
        document.querySelector('#followed_by').innerHTML = `Is followed by: ${result.followed_by_count} user(s)`;
        document.querySelector('#follows').innerHTML = `Follows: ${result.follows_count} user(s)`;
    });

    console.log(`Follow of ${user_id} is updated`);
}

