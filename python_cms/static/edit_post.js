const del_img = document.querySelector('#delete-img-btn')
if (del_img) {
    del_img.addEventListener('click', function (e) {
        e.target.closest('#delete-img-btn').remove();
        document.querySelector('#edit-img').remove();
        document.querySelector('#originalTeaserImage').remove();
        document.querySelector('#teaser_image').classList.remove('hidden');
    });
}

document.querySelector('#editPost').addEventListener('click', function (e) {
    // if the text area has no text in it, we'll alert the user
    const data = CKEDITOR.instances.body.getData();
    if (!data) {
        alert('Article content is required.');
        e.preventDefault();
    }
});