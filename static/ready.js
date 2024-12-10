// Prevent layout shift from content loading before styles are loaded.

let ready = (callback) => {
  document.readyState === 'complete' || document.readyState === 'interactive'
    ? callback()
    :document.addEventListener('DOMContentLoaded', callback)
}

ready(() => {
  document.body.style.visibility = 'visible'
})