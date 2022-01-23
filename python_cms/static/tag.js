let index = 0;
let index_obj = {}

document.querySelector('#tag-ok').addEventListener('click', function () {
    let tags = document.getElementById('tags');
    // console.log(tags.value, document.getElementById('tags-for-python').value);
    index_obj[index] = tags.value
    document.getElementById('tags-for-python').value = document.getElementById('tags-for-python').value + "-" + tags.value;
    // console.log(index_obj)
    render(tags.value, index);
    index = index + 1;

});

function render(tag, index) {
    const markup = `
    <span class="tag">
      <a class="tag-name" href="#">${tag}</a>
      <i id=${index} class="fas fa-times"></i>
    </span> 
    `;

    document.querySelector('#tag-elements').insertAdjacentHTML('beforeend', markup);
    document.getElementById(`${index}`).addEventListener('click', (event) => {
        deleleted_index = document.getElementById(`${index}`).getAttribute('id')
        delete index_obj[deleleted_index]
        event.target.closest('.tag').remove();

        document.getElementById('tags-for-python').value = '';
        for (const key in index_obj) {
            document.getElementById('tags-for-python').value = document.getElementById('tags-for-python').value + "-" + index_obj[key]
        }

    });
}
