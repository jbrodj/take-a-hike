// Get first element of the log new hike form and set it to focus when page loads.
form = document.getElementById('new-hike-form')
firstInput = form.children[0].children[1]

setTimeout(() => {
  firstInput.focus()
}, 0)
