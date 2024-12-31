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
    msgContainer.classList.add('hidden')
  })
}

closeContextMsg()


// Get first element in a form (if present) and set it to focus when page loads.
const autofocus = () => {

  setTimeout(() => {
    form = document.getElementsByClassName('user-input-form')
    firstInput = form[0]?.children[0]?.children[0]
    // Tree is: <form.user-input-form> --> <div.form-content> --> <label> + <input>
    firstInput?.focus()
  }, 0)
}

autofocus()