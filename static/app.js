$('.team-fav').on('submit', async function(evt) {
    evt.preventDefault()
    let e = evt.target
    let res = await axios.post(`/users/toggle-favorite-team/${e.id}`)
    let button = $(`#btn${e.id}`)
    if (res.data !== 'Unauthorized') {
        if (button.hasClass('btn-danger')) {
            button.removeClass('btn-danger')
            button.addClass('btn-secondary')
        } else {
            button.removeClass('btn-secondary')
            button.addClass('btn-danger')
        }
    }
})

$('.player-fav').on('submit', async function(evt) {
    evt.preventDefault()
    let e = evt.target
    let res = await axios.post(`/users/toggle-favorite-player/${e.id}`)
    let button = $(`#btn${e.id}`)
    if (res.data !== 'Unauthorized') {
        if (button.hasClass('btn-danger')) {
            button.removeClass('btn-danger')
            button.addClass('btn-secondary')
        } else {
            button.removeClass('btn-secondary')
            button.addClass('btn-danger')
        }
    }
})