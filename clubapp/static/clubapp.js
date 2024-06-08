function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function fetchAndDeleteOnSuccess(url, ids, request='DELETE'){
    fetch(url,
    {
        method: request,
        headers: {
            'X-CSRFToken': csrftoken,
        },
    })
    .then((response) => {
        console.log(response);
        if (response.ok){
                for (i in ids) {
                    document.getElementById(ids[i]).remove();
                }
        }
    })
    .catch((error) => {
        alert('Error:', error);
    })
}
