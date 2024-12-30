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