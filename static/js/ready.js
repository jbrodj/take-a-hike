// Prevent layout shift from content loading before styles are loaded.

const ready = (callback) => {
  document.readyState === 'complete' || document.readyState === 'interactive'
    ? callback()
    :document.addEventListener('DOMContentLoaded', callback)
}

ready(() => {
  document.body.style.visibility = 'visible'
})

ready()


// Provide functionality for close button on context message container

const closeContextMsg = () => {
  msgContainer = document.getElementById('contextMsgContainer')
  closeBtn = document.getElementById('contextCloseBtn')

  closeBtn?.addEventListener('click', (event) => {
    console.log('close btn event')
    msgContainer.classList.add('hidden')
  })
}

closeContextMsg()